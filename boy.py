from math import pi
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a,
    get_canvas_width, get_time, load_image,
)
from transitions import Machine


RESOURCE_DIR = Path(__file__).resolve().parent / 'assets'
IDLE_FRAME_COUNT = 8
IDLE_FPS = 8
IDLE_TIMEOUT = 5.0
RUN_FRAME_COUNT = 8
RUN_FPS = 8
RUN_SPEED = 200.0
SPRITE_SIZE = 100
AUTO_RUN_SPEED = RUN_SPEED * 2
AUTO_RUN_SCALE = 1.5
AUTO_RUN_FPS = RUN_FPS * 2
AUTO_RUN_DURATION = 5.0


class AutoRun:
    """Timed, enlarged run state with automatic reflection at screen edges."""

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0

    def enter(self):
        boy = self.boy
        boy.frame = 0
        boy.scale = AUTO_RUN_SCALE
        boy.run_dir = boy.face_dir
        boy.pressed_directions.clear()
        self.started_at = get_time()
        boy.last_update_time = self.started_at
        half_size = SPRITE_SIZE * boy.scale / 2
        boy.x = max(half_size, min(get_canvas_width() - half_size, boy.x))

    def exit(self, frame_time=None):
        self.boy.scale = 1.0

    def update(self, frame_time):
        boy = self.boy
        boy.frame = (boy.frame + AUTO_RUN_FPS * frame_time) % RUN_FRAME_COUNT
        half_size = SPRITE_SIZE * boy.scale / 2
        left, right = half_size, get_canvas_width() - half_size
        boy.x += boy.run_dir * AUTO_RUN_SPEED * frame_time
        # Reflect overshoot as well, so long frames preserve traveled distance.
        while boy.x < left or boy.x > right:
            if boy.x < left:
                boy.x = 2 * left - boy.x
                boy.run_dir = 1
            elif boy.x > right:
                boy.x = 2 * right - boy.x
                boy.run_dir = -1
        if boy.x <= left:
            boy.run_dir = 1
        elif boy.x >= right:
            boy.run_dir = -1
        boy.face_dir = boy.run_dir

    def draw(self):
        self.boy.draw_running_sprite()


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.run_dir = 0
        self.pressed_directions = []
        self.scale = 1.0
        self.image = load_image(str(RESOURCE_DIR / 'animation_sheet.png'))
        self.last_update_time = get_time()
        self.idle_started_at = self.last_update_time
        self.auto_run = AutoRun(self)

        self.machine = Machine(
            model=self,
            states=[
                'IDLE', 'RUN', 'SLEEP',
                {
                    'name': 'AUTO_RUN',
                    'on_enter': self.auto_run.enter,
                    'on_exit': self.auto_run.exit,
                },
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        # Check the timeout before the internal animation transition.
        self.machine.add_transition(
            trigger='tick',
            source='IDLE',
            dest='SLEEP',
            conditions='_idle_timed_out',
            after='_enter_sleep',
        )
        self.machine.add_transition(
            trigger='tick',
            source='IDLE',
            dest=None,
            after='_update_idle_animation',
        )
        self.machine.add_transition(trigger='tick', source='SLEEP', dest=None)
        self.machine.add_transition(
            trigger='tick',
            source='RUN',
            dest=None,
            after='_update_run',
        )
        self.machine.add_transition(
            trigger='start_running',
            source=['IDLE', 'SLEEP', 'AUTO_RUN'],
            dest='RUN',
            after='_start_run',
        )
        self.machine.add_transition(
            trigger='stop_running',
            source='RUN',
            dest='IDLE',
            after='_restart_idle',
        )
        self.machine.add_transition(
            trigger='start_auto_run', source='IDLE', dest='AUTO_RUN',
        )
        self.machine.add_transition(
            trigger='tick', source='AUTO_RUN', dest='IDLE',
            conditions='_auto_run_timed_out', after='_restart_idle',
        )
        self.machine.add_transition(
            trigger='tick', source='AUTO_RUN', dest=None,
            after=self.auto_run.update,
        )
        self.machine.add_transition(
            trigger='wake_up',
            source='SLEEP',
            dest='IDLE',
            after='_restart_idle',
        )

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        if event.key == SDLK_a:
            if (event.type == SDL_KEYDOWN and self.state == 'IDLE'
                    and not getattr(event, 'repeat', 0)):
                self.start_auto_run()
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            if self.state == 'SLEEP':
                self.wake_up()
            return

        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            if self.state == 'AUTO_RUN':
                self.pressed_directions.clear()
            # Ignore key repeats so the most recently pressed key keeps priority.
            if event.key in self.pressed_directions:
                return
            self.pressed_directions.append(event.key)
        elif event.key in self.pressed_directions:
            self.pressed_directions.remove(event.key)
        else:
            return

        if self.pressed_directions:
            self.run_dir = 1 if self.pressed_directions[-1] == SDLK_RIGHT else -1
            self.face_dir = self.run_dir
            if self.state in ('IDLE', 'SLEEP', 'AUTO_RUN'):
                self.start_running()
        elif self.state == 'RUN':
            self.stop_running()

    def update(self):
        now = get_time()
        frame_time = now - self.last_update_time
        self.last_update_time = now
        self.tick(frame_time)

    def _update_idle_animation(self, frame_time):
        self.frame = (self.frame + IDLE_FPS * frame_time) % IDLE_FRAME_COUNT

    def _idle_timed_out(self, frame_time):
        return get_time() - self.idle_started_at >= IDLE_TIMEOUT

    def _auto_run_timed_out(self, frame_time):
        return get_time() - self.auto_run.started_at >= AUTO_RUN_DURATION

    def _enter_sleep(self, frame_time):
        self.frame = 0

    def _start_run(self):
        self.frame = 0
        self.last_update_time = get_time()

    def _update_run(self, frame_time):
        self.frame = (self.frame + RUN_FPS * frame_time) % RUN_FRAME_COUNT
        self.x += self.run_dir * RUN_SPEED * frame_time
        half_size = SPRITE_SIZE / 2
        self.x = max(half_size, min(get_canvas_width() - half_size, self.x))

    def _restart_idle(self, frame_time=None):
        self.frame = 0
        self.run_dir = 0
        self.pressed_directions.clear()
        self.last_update_time = get_time()
        self.idle_started_at = self.last_update_time

    def draw(self):
        if self.state == 'AUTO_RUN':
            self.auto_run.draw()
            return

        if self.state == 'SLEEP':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                0, row, 100, 100, pi / 2, '',
                self.x, self.y - 25, 100, 100,
            )
            return

        if self.state == 'RUN':
            self.draw_running_sprite()
            return

        row = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(
            int(self.frame) * SPRITE_SIZE, row,
            SPRITE_SIZE, SPRITE_SIZE, self.x, self.y,
        )

    def draw_running_sprite(self):
        row = 100 if self.face_dir == 1 else 0
        size = SPRITE_SIZE * self.scale
        # Keep the bottom of the sprite fixed when entering/leaving AutoRun.
        draw_y = self.y + (size - SPRITE_SIZE) / 2
        self.image.clip_draw(
            int(self.frame) * SPRITE_SIZE, row,
            SPRITE_SIZE, SPRITE_SIZE, self.x, draw_y, size, size,
        )

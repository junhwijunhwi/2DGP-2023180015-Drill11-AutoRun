from math import pi
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE,
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


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.run_dir = 0
        self.pressed_directions = []
        self.image = load_image(str(RESOURCE_DIR / 'animation_sheet.png'))
        self.last_update_time = get_time()
        self.idle_started_at = self.last_update_time

        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP'],
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
            source=['IDLE', 'SLEEP'],
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
            trigger='wake_up',
            source='SLEEP',
            dest='IDLE',
            after='_restart_idle',
        )

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            if self.state == 'SLEEP':
                self.wake_up()
            return

        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
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
            if self.state in ('IDLE', 'SLEEP'):
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

    def _restart_idle(self):
        self.frame = 0
        self.run_dir = 0
        self.pressed_directions.clear()
        self.last_update_time = get_time()
        self.idle_started_at = self.last_update_time

    def draw(self):
        if self.state == 'SLEEP':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                0, row, 100, 100, pi / 2, '',
                self.x, self.y - 25, 100, 100,
            )
            return

        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
        else:
            row = 300 if self.face_dir == 1 else 200
        self.image.clip_draw(
            int(self.frame) * SPRITE_SIZE, row,
            SPRITE_SIZE, SPRITE_SIZE, self.x, self.y,
        )

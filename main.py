"""Run the standalone Drill #11 game with: python main.py."""

from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE,
    clear_canvas, close_canvas, delay, get_events, open_canvas, update_canvas,
)

from boy import Boy
from grass import Grass


def main():
    open_canvas(800, 600)
    try:
        world = [Grass(), Boy()]
        boy = world[1]
        running = True
        while running:
            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                    running = False
                else:
                    boy.handle_event(event)
            if not running:
                break
            for obj in world:
                obj.update()
            clear_canvas()
            for obj in world:
                obj.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()

"""Render real SDL images without a visible window; save evidence in docs/."""

import os
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pico2d
import sdl2
from sdl2 import sdlimage

import boy
from grass import Grass

engine = importlib.import_module('pico2d.pico2d')


def save_frame(path, grass, character):
    pico2d.clear_canvas()
    grass.draw()
    character.draw()
    surface = sdl2.SDL_CreateRGBSurfaceWithFormat(0, 800, 600, 32, sdl2.SDL_PIXELFORMAT_RGBA32)
    if not surface:
        raise RuntimeError(sdl2.SDL_GetError())
    try:
        result = sdl2.SDL_RenderReadPixels(
            engine.renderer, None, surface.contents.format.contents.format,
            surface.contents.pixels, surface.contents.pitch,
        )
        if result != 0:
            raise RuntimeError(sdl2.SDL_GetError())
        if sdlimage.IMG_SavePNG(surface, str(path).encode('utf-8')) != 0:
            raise RuntimeError(sdl2.SDL_GetError())
    finally:
        sdl2.SDL_FreeSurface(surface)
    pico2d.update_canvas()


def main():
    output = ROOT / 'docs'
    output.mkdir(exist_ok=True)
    pico2d.open_canvas(800, 600)
    try:
        # SDL's dummy driver has no accelerated renderer. pico2d 1.5.1 tests
        # pointer identity against None, so explicitly select software here.
        if not engine.renderer:
            engine.renderer = sdl2.SDL_CreateRenderer(
                engine.window, -1, sdl2.SDL_RENDERER_SOFTWARE,
            )
        if not engine.renderer:
            raise RuntimeError(sdl2.SDL_GetError())
        now = [0.0]
        with patch.object(boy, 'get_time', side_effect=lambda: now[0]):
            character, grass = boy.Boy(), Grass()
            save_frame(output / 'idle.png', grass, character)
            character.handle_event(SimpleNamespace(type=boy.SDL_KEYDOWN, key=boy.SDLK_a))
            now[0] = 0.5
            character.update()
            save_frame(output / 'auto_run.png', grass, character)
            character.handle_event(SimpleNamespace(type=boy.SDL_KEYDOWN, key=boy.SDLK_LEFT))
            save_frame(output / 'run.png', grass, character)
            character.handle_event(SimpleNamespace(type=boy.SDL_KEYUP, key=boy.SDLK_LEFT))
            now[0] = 5.5
            character.update()
            save_frame(output / 'sleep.png', grass, character)
        print('PASS: actual SDL image loading and Idle/AutoRun/Run/Sleep rendering')
    finally:
        pico2d.close_canvas()


if __name__ == '__main__':
    main()

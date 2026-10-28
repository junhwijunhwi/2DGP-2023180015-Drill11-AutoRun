"""실제 main 함수를 통해 종료·입력 전달·자원 정리를 검증한다."""

from contextlib import ExitStack
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import main


class GameLoopTests(unittest.TestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.grass = Mock()
        self.boy = Mock()
        self.grass_factory = stack.enter_context(patch.object(main, 'Grass', return_value=self.grass))
        stack.enter_context(patch.object(main, 'Boy', return_value=self.boy))
        self.open_canvas = stack.enter_context(patch.object(main, 'open_canvas'))
        self.close_canvas = stack.enter_context(patch.object(main, 'close_canvas'))
        self.clear = stack.enter_context(patch.object(main, 'clear_canvas'))
        self.present = stack.enter_context(patch.object(main, 'update_canvas'))
        stack.enter_context(patch.object(main, 'delay'))
        self.focus = stack.enter_context(patch.object(main, 'SDL_GetKeyboardFocus', return_value=True))
        self.quit_event = SimpleNamespace(type=main.SDL_QUIT)
        self.events = stack.enter_context(patch.object(main, 'get_events', side_effect=[[], [self.quit_event]]))

    def test_quit_does_not_update_or_draw_an_extra_frame(self):
        self.events.side_effect = [[self.quit_event]]
        main.main()
        self.open_canvas.assert_called_once_with(800, 600)
        self.boy.update.assert_not_called()
        self.present.assert_not_called()
        self.close_canvas.assert_called_once()

    def test_escape_exits_without_forwarding_it_to_the_boy(self):
        escape = SimpleNamespace(type=main.SDL_KEYDOWN, key=main.SDLK_ESCAPE)
        self.events.side_effect = [[escape]]
        main.main()
        self.boy.handle_event.assert_not_called()
        self.close_canvas.assert_called_once()

    def test_keyboard_input_reaches_boy_and_world_is_rendered(self):
        event = SimpleNamespace(type=main.SDL_KEYDOWN, key=123)
        self.events.side_effect = [[event], [self.quit_event]]
        main.main()
        self.boy.handle_event.assert_called_once_with(event)
        self.boy.update.assert_called_once()
        self.grass.draw.assert_called_once()
        self.boy.draw.assert_called_once()
        self.present.assert_called_once()

    def test_unfocused_window_releases_held_controls(self):
        self.focus.return_value = False
        main.main()
        self.boy.release_controls.assert_called_once()
        self.boy.update.assert_called_once()

    def test_render_failure_still_closes_the_canvas(self):
        self.boy.draw.side_effect = RuntimeError('render failed')
        with self.assertRaisesRegex(RuntimeError, 'render failed'):
            main.main()
        self.close_canvas.assert_called_once()

    def test_asset_loading_failure_still_closes_the_canvas(self):
        self.grass_factory.side_effect = OSError('missing grass image')
        with self.assertRaisesRegex(OSError, 'missing grass image'):
            main.main()
        self.close_canvas.assert_called_once()


if __name__ == '__main__':
    unittest.main()

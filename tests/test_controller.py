"""Behavior tests use the real transitions machine with a controllable clock."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import boy


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.0
        self.image = Mock()
        for replacement in (
            patch.object(boy, 'get_time', side_effect=lambda: self.now),
            patch.object(boy, 'get_canvas_width', return_value=800),
            patch.object(boy, 'load_image', return_value=self.image),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)
        self.boy = boy.Boy()

    def key(self, key, event_type=boy.SDL_KEYDOWN, repeat=0):
        self.boy.handle_event(SimpleNamespace(type=event_type, key=key, repeat=repeat))

    def advance(self, seconds):
        self.now += seconds
        self.boy.update()

    def start_auto_run(self):
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_auto_run_has_a_dedicated_state_class(self):
        self.assertIsInstance(self.boy.auto_run, boy.AutoRun)
        self.assertEqual(set(self.boy.machine.states), {'IDLE', 'RUN', 'SLEEP', 'AUTO_RUN'})

    def test_a_starts_auto_run_and_release_does_not_stop_it(self):
        self.start_auto_run()
        self.key(boy.SDLK_a, boy.SDL_KEYUP)
        self.advance(0.25)
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.assertAlmostEqual(self.boy.x, 500)

    def test_auto_run_is_twice_as_fast_as_run(self):
        self.key(boy.SDLK_RIGHT)
        self.advance(0.25)
        normal_distance = self.boy.x - 400
        self.key(boy.SDLK_RIGHT, boy.SDL_KEYUP)
        self.boy.x = 400
        self.start_auto_run()
        self.advance(0.25)
        self.assertAlmostEqual(self.boy.x - 400, normal_distance * 2)

    def test_enlargement_preserves_the_bottom_of_the_sprite(self):
        self.start_auto_run()
        self.boy.draw()
        args = self.image.clip_draw.call_args.args
        self.assertEqual(args[-2:], (150, 150))
        self.assertEqual(args[5] - args[7] / 2, self.boy.y - 50)

    def test_auto_run_expires_at_five_seconds_not_before(self):
        self.start_auto_run()
        self.now = 4.999
        self.boy.update()
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.now = 5.0
        self.boy.update()
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.scale, 1.0)
        self.assertEqual(self.boy.run_dir, 0)
        self.assertEqual(self.boy.idle_started_at, 5.0)

    def test_expiry_followed_by_fresh_idle_timeout(self):
        self.start_auto_run()
        self.advance(5)
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'IDLE')
        self.now = 10
        self.boy.update()
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_right_boundary_reflects_remaining_distance(self):
        self.start_auto_run()
        self.boy.x = 720
        self.advance(0.1)
        self.assertAlmostEqual(self.boy.x, 690)
        self.assertEqual(self.boy.face_dir, -1)

    def test_left_boundary_reflects_remaining_distance(self):
        self.boy.face_dir = -1
        self.start_auto_run()
        self.boy.x = 80
        self.advance(0.1)
        self.assertAlmostEqual(self.boy.x, 110)
        self.assertEqual(self.boy.face_dir, 1)

    def test_exact_boundary_hit_turns_inward(self):
        self.start_auto_run()
        self.boy.x = 625
        self.advance(0.25)
        self.assertEqual(self.boy.x, 725)
        self.assertEqual(self.boy.run_dir, -1)

    def test_multiple_bounces_in_a_long_frame(self):
        self.start_auto_run()
        self.advance(4)
        self.assertAlmostEqual(self.boy.x, 700)
        self.assertEqual(self.boy.face_dir, 1)
        self.assertLessEqual(self.boy.x + 75, 800)
        self.assertGreaterEqual(self.boy.x - 75, 0)

    def test_enlarging_at_either_edge_is_immediately_clamped(self):
        for x, expected in ((50, 75), (750, 725)):
            with self.subTest(x=x):
                self.boy = boy.Boy()
                self.boy.x = x
                self.start_auto_run()
                self.assertEqual(self.boy.x, expected)

    def test_either_arrow_cancels_auto_run_into_normal_run(self):
        for key, direction in ((boy.SDLK_LEFT, -1), (boy.SDLK_RIGHT, 1)):
            with self.subTest(direction=direction):
                self.boy = boy.Boy()
                self.start_auto_run()
                self.key(key)
                self.assertEqual(self.boy.state, 'RUN')
                self.assertEqual(self.boy.scale, 1.0)
                self.assertEqual(self.boy.face_dir, direction)
                self.advance(0.25)
                self.assertAlmostEqual(self.boy.x, 400 + direction * 50)
                self.boy.draw()
                self.assertEqual(self.image.clip_draw.call_args.args[-2:], (100, 100))
                self.key(key, boy.SDL_KEYUP)
                self.assertEqual(self.boy.state, 'IDLE')

    def test_a_and_space_do_not_reset_or_cancel_auto_run(self):
        self.start_auto_run()
        self.advance(3)
        self.key(boy.SDLK_a)
        self.key(boy.SDLK_SPACE)
        self.assertEqual(self.boy.auto_run.started_at, 0)
        self.advance(2)
        self.assertEqual(self.boy.state, 'IDLE')
        self.key(boy.SDLK_a, repeat=1)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_a_is_only_enabled_in_idle(self):
        self.key(boy.SDLK_RIGHT)
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')
        self.key(boy.SDLK_RIGHT, boy.SDL_KEYUP)
        self.advance(5)
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'SLEEP')

    def test_holding_a_cannot_restart_auto_run_after_timeout(self):
        self.start_auto_run()
        self.advance(5)
        self.boy.handle_event(SimpleNamespace(type=boy.SDL_KEYDOWN, key=boy.SDLK_a))
        self.assertEqual(self.boy.state, 'IDLE')
        self.key(boy.SDLK_a, boy.SDL_KEYUP)
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_sleep_wakes_with_space_or_either_arrow(self):
        for key, expected in ((boy.SDLK_SPACE, 'IDLE'), (boy.SDLK_LEFT, 'RUN'), (boy.SDLK_RIGHT, 'RUN')):
            with self.subTest(key=key):
                self.boy = boy.Boy()
                self.advance(5)
                self.key(key)
                self.assertEqual(self.boy.state, expected)

    def test_overlapping_arrows_and_key_repeats_keep_last_pressed_direction(self):
        self.key(boy.SDLK_LEFT)
        self.key(boy.SDLK_RIGHT)
        self.key(boy.SDLK_LEFT, repeat=1)
        self.assertEqual(self.boy.face_dir, 1)
        self.key(boy.SDLK_RIGHT, boy.SDL_KEYUP)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.face_dir, -1)
        self.key(boy.SDLK_LEFT, boy.SDL_KEYUP)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_normal_run_stays_inside_screen(self):
        self.key(boy.SDLK_RIGHT)
        self.advance(10)
        self.assertEqual(self.boy.x, 750)
        self.key(boy.SDLK_LEFT)
        self.advance(10)
        self.assertEqual(self.boy.x, 50)

    def test_non_keyboard_events_are_ignored(self):
        self.boy.handle_event(SimpleNamespace(type=-1))
        self.assertEqual(self.boy.state, 'IDLE')

    def test_lost_focus_stops_manual_run(self):
        self.key(boy.SDLK_LEFT)
        self.boy.release_controls()
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.pressed_directions, [])
        self.assertEqual(self.boy.run_dir, 0)

    def test_lost_focus_keeps_auto_run_active(self):
        self.start_auto_run()
        self.boy.release_controls()
        self.advance(0.25)
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.assertEqual(self.boy.x, 500)
        self.advance(4.75)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_lost_focus_releases_a_latch(self):
        self.start_auto_run()
        self.advance(5)
        self.boy.release_controls()
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_lost_focus_does_not_restart_idle_timeout(self):
        self.advance(4)
        self.boy.release_controls()
        self.advance(1)
        self.assertEqual(self.boy.state, 'SLEEP')


if __name__ == '__main__':
    unittest.main()

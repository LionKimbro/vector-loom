import math
import unittest
from unittest.mock import patch

from vectorloom.canvas import canvas_context, transform_stack
from vectorloom.demo import canvas_host_demo
from vectorloom.tk_runtime import app_shell, canvas_host_window, tk_runtime


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))
        return len(self.calls)

    def create_rectangle(self, *args, **kwargs):
        self.calls.append(("rectangle", args, kwargs))
        return len(self.calls)

    def create_oval(self, *args, **kwargs):
        self.calls.append(("oval", args, kwargs))
        return len(self.calls)

    def create_polygon(self, *args, **kwargs):
        self.calls.append(("polygon", args, kwargs))
        return len(self.calls)

    def create_text(self, *args, **kwargs):
        self.calls.append(("text", args, kwargs))
        return len(self.calls)

    def delete(self, *args):
        self.calls.append(("delete", args, {}))


class FakeWindow:
    def __init__(self):
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


class FakeRoot:
    def __init__(self, events):
        self.events = events

    def mainloop(self):
        self.events.append("mainloop")


class AppShellTests(unittest.TestCase):
    def setUp(self):
        app_shell.config["app-specific-setup"] = None

    def test_main_requires_an_application_specific_setup_function(self):
        with self.assertRaisesRegex(RuntimeError, "app-specific-setup"):
            app_shell.main()

    def test_main_runs_setup_before_starting_the_timer_and_mainloop(self):
        events = []
        root = FakeRoot(events)

        def create_root():
            events.append("root")
            tk_runtime.g["root"] = root

        def set_up_application():
            events.append("setup")

        def start_timer():
            events.append("timer")

        app_shell.config["app-specific-setup"] = set_up_application
        with patch.object(tk_runtime, "create_and_withdraw_root", create_root):
            with patch("vectorloom.tk_runtime.app_shell.timer.start_timer", start_timer):
                app_shell.main()

        self.assertEqual(events, ["root", "setup", "timer", "mainloop"])


class TransformStackMathTests(unittest.TestCase):
    def setUp(self):
        transform_stack.S[:] = [transform_stack.identity_frame()]

    def assertPointAlmostEqual(self, actual, expected):
        self.assertTrue(
            math.isclose(actual[0], expected[0], abs_tol=1e-9)
            and math.isclose(actual[1], expected[1], abs_tol=1e-9),
            f"{actual!r} != {expected!r}",
        )

    def test_01_identity_frame_maps_a_point_to_itself(self):
        self.assertPointAlmostEqual(transform_stack.local_to_world(3, -4), (3, -4))

    def test_02_locate_moves_the_root_frame(self):
        transform_stack.locate(10, 20)
        self.assertPointAlmostEqual(transform_stack.local_to_world(0, 0), (10, 20))

    def test_03_positive_angle_rotates_clockwise(self):
        transform_stack.turn(90)
        self.assertPointAlmostEqual(transform_stack.local_to_world(4, 0), (0, 4))

    def test_04_root_slide_moves_in_world_coordinates(self):
        transform_stack.locate(10, 20)
        transform_stack.slide(-3, 7)
        self.assertPointAlmostEqual(transform_stack.local_to_world(0, 0), (7, 27))

    def test_05_push_with_defaults_preserves_the_current_transform(self):
        transform_stack.locate(8, 9)
        transform_stack.push_transform({})
        self.assertPointAlmostEqual(transform_stack.local_to_world(0, 0), (8, 9))

    def test_06_child_translation_is_relative_to_an_unrotated_parent(self):
        canvas_context.locate(10, 20)
        canvas_context.push_transform({"x": 5, "y": 6})
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (15, 26))

    def test_07_child_translation_follows_parent_orientation(self):
        canvas_context.turn(90)
        canvas_context.push_transform({"x": 10})
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (0, 10))

    def test_08_nested_angles_accumulate(self):
        canvas_context.turn(30)
        canvas_context.push_transform({"angle": 60})
        self.assertPointAlmostEqual(canvas_context.local_to_world(2, 0), (0, 2))

    def test_09_three_level_translations_compose(self):
        canvas_context.locate(10, 0)
        canvas_context.turn(90)
        canvas_context.push_transform({"x": 5})
        canvas_context.push_transform({"y": 2})
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (8, 5))

    def test_10_slide_uses_the_parent_coordinate_system(self):
        canvas_context.turn(90)
        canvas_context.push_transform({"x": 5})
        canvas_context.slide(3, 0)
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (0, 8))

    def test_11_locate_replaces_the_top_frame_position(self):
        canvas_context.turn(90)
        canvas_context.push_transform({"x": 5})
        canvas_context.locate(2, 3)
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (-3, 2))

    def test_12_turn_changes_the_top_frame_in_place(self):
        canvas_context.turn(30)
        canvas_context.push_transform({"angle": 20})
        canvas_context.turn(40)
        self.assertPointAlmostEqual(canvas_context.local_to_world(1, 0), (0, 1))

    def test_13_world_to_local_inverts_a_root_transform(self):
        canvas_context.locate(10, 20)
        canvas_context.turn(90)
        self.assertPointAlmostEqual(canvas_context.world_to_local(6, 23), (3, 4))

    def test_14_world_to_local_inverts_a_nested_transform(self):
        canvas_context.locate(10, -4)
        canvas_context.turn(30)
        canvas_context.push_transform({"x": 3, "y": 5, "angle": -70})
        local_point = (2, -7)
        self.assertPointAlmostEqual(
            canvas_context.world_to_local(*canvas_context.local_to_world(*local_point)),
            local_point,
        )

    def test_15_inverse_remains_valid_after_slide_and_turn(self):
        canvas_context.locate(7, 11)
        canvas_context.push_transform({"x": 4, "angle": 15})
        canvas_context.slide(-2, 9)
        canvas_context.turn(35)
        local_point = (-3, 8)
        self.assertPointAlmostEqual(
            canvas_context.world_to_local(*canvas_context.local_to_world(*local_point)),
            local_point,
        )

    def test_16_peek_returns_a_copy_not_the_live_frame(self):
        frame = canvas_context.peek_transform()
        frame["x"] = 99
        self.assertEqual(canvas_context.peek_transform()["x"], 0)

    def test_17_drop_returns_the_popped_frame_and_restores_the_parent(self):
        canvas_context.locate(10, 20)
        canvas_context.push_transform({"x": 4, "y": 5, "angle": 30})
        popped = canvas_context.drop_transform()
        self.assertEqual((popped["x"], popped["y"], popped["angle"]), (4, 5, 30))
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (10, 20))

    def test_18_root_frame_cannot_be_dropped(self):
        with self.assertRaisesRegex(RuntimeError, "identity root"):
            canvas_context.drop_transform()

    def test_19_push_caches_the_composed_local_to_world_matrix(self):
        canvas_context.locate(10, 20)
        canvas_context.turn(90)
        canvas_context.push_transform({"x": 5})
        matrix = canvas_context.peek_transform()["M"]
        self.assertPointAlmostEqual(canvas_context._apply_matrix(matrix, 0, 0), (10, 25))

    def test_20_parent_frame_is_unchanged_when_a_child_is_mutated(self):
        canvas_context.locate(10, 20)
        canvas_context.push_transform({"x": 5})
        canvas_context.slide(3, 4)
        canvas_context.drop_transform()
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (10, 20))


class CanvasContextTests(unittest.TestCase):
    def setUp(self):
        canvas_context.styles.clear()
        canvas_context.designs.clear()
        canvas_context.clear_connectors()
        canvas_context.S[:] = [canvas_context._identity_frame()]
        self.canvas = FakeCanvas()
        canvas_context.set_canvas(self.canvas)

    def assertPointAlmostEqual(self, actual, expected):
        self.assertTrue(
            math.isclose(actual[0], expected[0], abs_tol=1e-9)
            and math.isclose(actual[1], expected[1], abs_tol=1e-9),
            f"{actual!r} != {expected!r}",
        )

    def test_transform_stack_converts_points_and_preserves_local_values(self):
        canvas_context.locate(10, 20)
        canvas_context.turn(90)

        self.assertPointAlmostEqual(canvas_context.local_to_world(4, 0), (10, 24))
        self.assertPointAlmostEqual(canvas_context.world_to_local(10, 24), (4, 0))

        canvas_context.push_transform({"x": 5})
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (10, 25))
        canvas_context.slide(2, 0)
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (10, 27))

    def test_draw_recurses_through_groups_and_restores_the_stack(self):
        canvas_context.designs["nested"] = {
            "contents": [
                {
                    "type": "group",
                    "x": 5,
                    "angle": 90,
                    "contents": [
                        {"type": "line", "x1": 0, "y1": 0, "x2": 10, "y2": 0},
                    ],
                },
            ],
        }
        canvas_context.push_transform({"x": 10, "y": 20})
        incoming_depth = len(canvas_context.S)

        self.assertEqual(canvas_context.draw("nested"), [1])

        self.assertEqual(len(canvas_context.S), incoming_depth)
        kind, args, options = self.canvas.calls[0]
        self.assertEqual(kind, "line")
        self.assertEqual(options, {"tags": ("design:nested",)})
        self.assertPointAlmostEqual(args[:2], (15, 20))
        self.assertPointAlmostEqual(args[2:4], (15, 30))

    def test_rotated_box_uses_transformed_polygon(self):
        canvas_context.designs["box"] = {
            "contents": [{"type": "rect", "x": 0, "y": 0, "w": 10, "h": 5}],
        }
        canvas_context.turn(90)

        self.assertEqual(canvas_context.draw("box"), [1])

        kind, args, _options = self.canvas.calls[0]
        self.assertEqual(kind, "polygon")
        self.assertPointAlmostEqual(args[:2], (0, 0))
        self.assertPointAlmostEqual(args[2:4], (0, 10))

    def test_connector_is_recorded_with_its_effective_world_frame(self):
        canvas_context.designs["arm"] = {
            "contents": [{
                "type": "group",
                "x": 10,
                "y": 20,
                "angle": 90,
                "contents": [{
                    "type": "connector",
                    "id": "hand",
                    "x": 5,
                    "y": 0,
                    "role": "attachment",
                    "tags": ["grip", "hot-spot"],
                }],
            }],
        }

        self.assertEqual(canvas_context.draw("arm", "left-arm"), [])

        record = canvas_context.select_connector("left-arm", "hand")
        self.assertEqual(record["connector-role"], "attachment")
        self.assertEqual(record["connector-tags"], ["grip", "hot-spot"])
        self.assertPointAlmostEqual((record["x"], record["y"]), (10, 25))
        self.assertTrue(math.isclose(record["angle"], 90, abs_tol=1e-9))
        self.assertPointAlmostEqual(
            canvas_context._apply_matrix(record["M"], 0, 0),
            (10, 25),
        )
        self.assertPointAlmostEqual(
            canvas_context._apply_matrix(record["Minverse"], 10, 25),
            (0, 0),
        )
        self.assertEqual(self.canvas.calls, [])

    def test_connector_without_an_instance_id_raises_after_prior_shapes_draw(self):
        canvas_context.designs["requires-id"] = {
            "contents": [
                {"type": "line", "x1": 0, "y1": 0, "x2": 5, "y2": 0},
                {"type": "connector", "id": "hand", "x": 5, "y": 0, "role": "attachment"},
            ],
        }

        with self.assertRaisesRegex(RuntimeError, "requires instance_id"):
            canvas_context.draw("requires-id")

        self.assertEqual(len(self.canvas.calls), 1)
        self.assertEqual(canvas_context.connectors, {})

    def test_dry_run_uses_the_normal_traversal_without_drawing_or_recording(self):
        canvas_context.designs["requires-id"] = {
            "contents": [{
                "type": "group",
                "contents": [
                    {"type": "line", "x1": 0, "y1": 0, "x2": 5, "y2": 0},
                    {"type": "connector", "id": "hand", "x": 5, "y": 0, "role": "attachment"},
                ],
            }],
        }

        with self.assertRaisesRegex(RuntimeError, "requires instance_id"):
            canvas_context.draw("requires-id", flags=["dry-run"])

        self.assertEqual(self.canvas.calls, [])
        self.assertEqual(canvas_context.connectors, {})
        self.assertEqual(len(canvas_context.S), 1)

    def test_attach_draws_from_the_selected_connector_frame(self):
        canvas_context.designs["anchor"] = {
            "contents": [{
                "type": "connector",
                "id": "joint",
                "x": 10,
                "y": 20,
                "angle": 90,
                "role": "attachment",
            }],
        }
        canvas_context.designs["child"] = {
            "contents": [{"type": "line", "x1": 0, "y1": 0, "x2": 5, "y2": 0}],
        }
        canvas_context.draw("anchor", "base")
        canvas_context.select_connector("base", "joint")

        self.assertEqual(canvas_context.draw("child", "child", ["attach"]), [1])

        kind, args, options = self.canvas.calls[0]
        self.assertEqual(kind, "line")
        self.assertPointAlmostEqual(args[:2], (10, 20))
        self.assertPointAlmostEqual(args[2:4], (10, 25))
        self.assertEqual(options["tags"], ("design:child", "instance:child"))
        self.assertEqual(len(canvas_context.S), 1)


class CanvasHostWindowTests(unittest.TestCase):
    def setUp(self):
        canvas_context.styles.clear()
        canvas_context.designs.clear()
        canvas_context.S[:] = [canvas_context._identity_frame()]
        self.canvas = FakeCanvas()
        canvas_host_window.g.update({
            "canvas": self.canvas,
        })
        canvas_host_demo.stop_canvas_host_demo()

    def test_kinetic_experiment_builds_and_draws_nested_groups(self):
        canvas_host_demo.start_canvas_host_demo()

        self.assertIn("kinetic-transform-lab", canvas_context.designs)
        self.assertIsNotNone(canvas_host_demo.g["orbit-group"])
        self.assertIsNotNone(canvas_host_demo.g["spin-group"])
        self.assertIsNotNone(canvas_host_demo.g["counter-spin-group"])
        self.assertEqual(self.canvas.calls[0], ("delete", ("all",), {}))
        self.assertEqual(len(canvas_context.S), 1)

    def test_timer_tick_advances_every_animation_transform(self):
        canvas_host_demo.start_canvas_host_demo()
        call_count = len(self.canvas.calls)

        canvas_host_demo.periodic_timer_callback()

        self.assertEqual(canvas_host_demo.g["orbit-angle"], 2)
        self.assertEqual(canvas_host_demo.g["spin-angle"], 9)
        self.assertEqual(canvas_host_demo.g["counter-spin-angle"], 346)
        self.assertGreater(canvas_host_demo.g["bob-phase"], 0)
        self.assertEqual(canvas_host_demo.g["orbit-group"]["angle"], 2)
        self.assertEqual(canvas_host_demo.g["spin-group"]["angle"], 9)
        self.assertEqual(canvas_host_demo.g["counter-spin-group"]["angle"], 346)
        self.assertEqual(self.canvas.calls[call_count], ("delete", ("all",), {}))
        self.assertEqual(len(canvas_context.S), 1)

    def test_close_unregisters_the_periodic_callback_before_destroying_window(self):
        window = FakeWindow()
        canvas_host_window.g["window"] = window
        canvas_host_demo.g.update({
            "orbit-group": {"angle": 0},
            "spin-group": {"angle": 0},
            "counter-spin-group": {"angle": 0},
        })
        canvas_host_window.set_close_callback(canvas_host_demo.stop_canvas_host_demo)
        tk_runtime.g["periodic-callback"] = canvas_host_demo.periodic_timer_callback

        canvas_host_window.close_canvas_host_window()

        self.assertIsNone(tk_runtime.g["periodic-callback"])
        self.assertTrue(window.destroyed)
        self.assertIsNone(canvas_host_window.g["canvas"])
        self.assertIsNone(canvas_host_demo.g["orbit-group"])

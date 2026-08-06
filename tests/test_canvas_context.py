import math
import unittest

from vectorloom import canvas_context


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


class TransformStackMathTests(unittest.TestCase):
    def setUp(self):
        canvas_context.S[:] = [canvas_context._identity_frame()]

    def assertPointAlmostEqual(self, actual, expected):
        self.assertTrue(
            math.isclose(actual[0], expected[0], abs_tol=1e-9)
            and math.isclose(actual[1], expected[1], abs_tol=1e-9),
            f"{actual!r} != {expected!r}",
        )

    def test_01_identity_frame_maps_a_point_to_itself(self):
        self.assertPointAlmostEqual(canvas_context.local_to_world(3, -4), (3, -4))

    def test_02_locate_moves_the_root_frame(self):
        canvas_context.locate(10, 20)
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (10, 20))

    def test_03_positive_angle_rotates_clockwise(self):
        canvas_context.turn(90)
        self.assertPointAlmostEqual(canvas_context.local_to_world(4, 0), (0, 4))

    def test_04_root_slide_moves_in_world_coordinates(self):
        canvas_context.locate(10, 20)
        canvas_context.slide(-3, 7)
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (7, 27))

    def test_05_push_with_defaults_preserves_the_current_transform(self):
        canvas_context.locate(8, 9)
        canvas_context.push_transform({})
        self.assertPointAlmostEqual(canvas_context.local_to_world(0, 0), (8, 9))

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
        self.assertEqual(options, {})
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

import unittest
from unittest.mock import patch

from vectorloom.editor import discrete_engine, event_queue, interaction_runtime, projection


class FakeTree:
    def __init__(self):
        self.rows = {}

    def get_children(self):
        return tuple(self.rows)

    def delete(self, *item_iids):
        for item_iid in item_iids:
            self.rows.pop(item_iid)

    def insert(self, parent, index, iid, text):
        self.rows[iid] = {"parent": parent, "index": index, "text": text}


class EditorEventQueueTests(unittest.TestCase):
    def setUp(self):
        event_queue.event_queue.clear()
        event_queue.recent_events.clear()

    def test_adjacent_pointer_motion_is_coalesced_without_crossing_an_event(self):
        event_queue.post_pointer_motion(10, 20, 1)
        event_queue.post_pointer_motion(11, 21, 2)
        event_queue.post_event({"type": "KEY_PRESSED", "keysym": "a", "ms": 3})
        event_queue.post_pointer_motion(12, 22, 4)

        pending = event_queue.drain_events()

        self.assertEqual([event["type"] for event in pending], [
            "POINTER_MOTION", "KEY_PRESSED", "POINTER_MOTION",
        ])
        self.assertEqual(pending[0]["samples"], [
            {"x": 10, "y": 20, "ms": 1},
            {"x": 11, "y": 21, "ms": 2},
        ])
        self.assertEqual(event_queue.recent_events, pending)


class EditorProjectionTests(unittest.TestCase):
    def test_empty_library_category_has_a_selectable_test_placeholder(self):
        tree = FakeTree()

        projection._replace_tree_rows(tree, {}, "design")

        self.assertEqual(tree.rows, {
            "design:empty": {
                "parent": "",
                "index": "end",
                "text": "(no designs loaded)",
            },
        })


class EditorDiscreteEngineTests(unittest.TestCase):
    def setUp(self):
        discrete_engine.initialize_discrete_engine()

    def test_workspace_events_set_primary_design_and_root_focal_address(self):
        effects = discrete_engine.reduce_events([
            {"type": "SET_PRIMARY_DESIGN", "design-name": "house"},
            {"type": "SET_FOCAL_ADDRESS", "address": ".6"},
        ])

        self.assertEqual(discrete_engine.workspace["primary-design-name"], "house")
        self.assertEqual(discrete_engine.workspace["focal-address"], ".6")
        self.assertEqual([effect["owner"] for effect in effects], [
            "projection", "projection",
        ])


class EditorInteractionRuntimeTests(unittest.TestCase):
    def setUp(self):
        event_queue.event_queue.clear()
        event_queue.recent_events.clear()
        interaction_runtime.initialize_editor_runtime()

    def test_cycle_drains_raw_input_and_projects_without_a_tk_window(self):
        event_queue.post_event({"type": "KEY_PRESSED", "keysym": "a", "ms": 5})

        with patch("vectorloom.editor.interaction_runtime.projection.project") as project:
            interaction_runtime.run_update_cycle()

        self.assertEqual(interaction_runtime.raw["last-event-type"], "KEY_PRESSED")
        self.assertEqual(interaction_runtime.raw["keys-down"], ["a"])
        self.assertEqual(event_queue.recent_events, [
            {"type": "KEY_PRESSED", "keysym": "a", "ms": 5},
        ])
        project.assert_called_once_with()

    def test_motion_packet_updates_raw_once_for_each_preserved_sample(self):
        event_queue.post_pointer_motion(10, 20, 1)
        event_queue.post_pointer_motion(30, 40, 2)

        with patch("vectorloom.editor.interaction_runtime.projection.project") as project:
            interaction_runtime.run_update_cycle()

        self.assertEqual((interaction_runtime.raw["x"], interaction_runtime.raw["y"]), (30, 40))
        self.assertTrue(interaction_runtime.raw["inside-canvas"])
        self.assertEqual(interaction_runtime.raw["ms"], 2)
        self.assertEqual(project.call_count, 2)

    def test_semantic_exit_request_routes_to_a_window_destroy_effect(self):
        interaction_runtime.post_semantic_event({"type": "EXIT_EDITOR"})

        with patch("vectorloom.editor.interaction_runtime.editor_window.destroy_editor_window") as destroy:
            with patch("vectorloom.editor.interaction_runtime.projection.project"):
                interaction_runtime.run_update_cycle()

        destroy.assert_called_once_with()

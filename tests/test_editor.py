"""Tests for the editor's model layer, history, and the CIRA loop.

The pure tests (normalization idempotency, world mutations, history) run
headlessly. The integration test drives the real TkVillage tick loop with
simulated RAW input and is skipped when Tk is unavailable.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, r"C:\lion\github\tkvillage\src")

from vectorloom import model  # noqa: E402
from vectorloom.editor import history, world  # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def _doc(name="primitives.vloom.json"):
    return model.load_file(os.path.join(EXAMPLES, name))


@pytest.mark.parametrize("name", ["primitives.vloom.json", "folder_node.vloom.json"])
def test_normalize_is_idempotent(name):
    # Re-normalizing a canonical document must not change it; this is what makes
    # save -> reload a lossless round-trip (transforms in particular).
    doc = _doc(name)
    again = model.normalize_document(doc)
    assert again == doc


def test_find_move_and_parent():
    doc = _doc()
    box = world.find_node(doc, "root.box")
    assert box["type"] == "rect"
    x0, y0 = box["x"], box["y"]
    world.move_node(doc, "root.box", 15.0, -5.0)
    assert (box["x"], box["y"]) == (x0 + 15.0, y0 - 5.0)
    parent, last = world.get_parent(doc, "root.box")
    assert parent["id"] == "root" and last == "box"


def test_move_inside_scaled_group_uses_local_delta():
    # The spun group in primitives is scaled 1.4 and rotated; a world-space move
    # must convert to the child's local frame so it lands where expected.
    doc = _doc()
    r = world.find_node(doc, "root.spun.r")
    x0 = r["x"]
    world.move_node(doc, "root.spun.r", 14.0, 0.0)
    # World dx 14 inside a 1.4x scaled (and rotated) parent is a smaller local
    # delta; it must differ from a naive +14 and from 0.
    assert r["x"] != x0
    assert abs(r["x"] - (x0 + 14.0)) > 1e-6


def test_add_delete_replace_roundtrip(tmp_path):
    doc = _doc()
    n0 = len(doc["root"]["children"])
    new_path = world.add_child(doc, "root", {"type": "rect", "x": 5, "y": 5, "w": 10, "h": 10})
    assert len(doc["root"]["children"]) == n0 + 1
    assert world.find_node(doc, new_path)["type"] == "rect"

    world.replace_node(doc, new_path, {"type": "oval", "x": 5, "y": 5, "w": 20, "h": 20})
    assert world.find_node(doc, new_path)["type"] == "oval"  # id preserved, type changed

    out = tmp_path / "out.vloom.json"
    world.save(str(out), doc)
    reloaded = model.load_file(str(out))
    assert reloaded == doc  # lossless save -> reload

    world.delete_node(doc, new_path)
    assert len(doc["root"]["children"]) == n0


def test_history_undo_redo():
    doc = _doc()
    path = "history-doc"
    history.init(path, doc, None)
    assert not history.can_undo(path)

    world.move_node(doc, "root.box", 10.0, 0.0)
    history.push(path, doc, "root.box")
    assert history.can_undo(path)

    snap = history.undo(path)
    assert snap["doc"]["root"]["children"][0]["x"] != doc["root"]["children"][0]["x"]
    again = history.redo(path)
    assert again["selection"] == "root.box"


def test_cira_loop_select_and_drag(tmp_path):
    village = pytest.importorskip("tkvillage")
    from vectorloom import geometry as geo, render
    from vectorloom.editor import app

    src = os.path.join(EXAMPLES, "primitives.vloom.json")
    doc_path = str(tmp_path / "edit.vloom.json")
    import shutil
    shutil.copy(src, doc_path)

    try:
        world.load(doc_path)
        history.init(doc_path, world.get(doc_path), None)
        village.create_app("vl-test", ".vl-test", test_mode=True)
    except Exception:
        pytest.skip("Tk not available")

    try:
        app.register()
        rec = village.summon_window(app.CANVAS_WINDOW, key=doc_path, payload={"doc_path": doc_path})
        village.run_ticks(3, update_tk=True)

        s = rec["state"]
        base = geo.compose(geo.translate(s["ox"], s["oy"]), geo.scale(s["scale"], s["scale"]))
        bb = render.path_world_bounds(world.get(doc_path), "root.disc", base)
        cx, cy = (bb[0] + bb[2]) / 2.0, (bb[1] + bb[3]) / 2.0
        cur = rec["raw"]["current"]

        def raw(x, y, down):
            cur["x"], cur["y"], cur["button1_down"] = x, y, down

        # click-select
        raw(cx, cy, True); village.run_ticks(1, update_tk=True)
        raw(cx, cy, False); village.run_ticks(2, update_tk=True)
        assert rec["state"]["selection"] == "root.disc"

        # drag-move
        disc = world.find_node(world.get(doc_path), "root.disc")
        x0 = disc["x"]
        raw(cx, cy, True); village.run_ticks(1, update_tk=True)
        raw(cx + 60, cy, True); village.run_ticks(1, update_tk=True)
        raw(cx + 60, cy, False); village.run_ticks(2, update_tk=True)
        disc = world.find_node(world.get(doc_path), "root.disc")
        assert disc["x"] > x0  # moved right
    finally:
        village.shutdown()
        import shutil
        for d in (".vl-test",):
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)

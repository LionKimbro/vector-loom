"""Smoke tests for the Vector Loom model and renderer.

These run headlessly where possible. The render test needs a Tk root and is
skipped automatically when Tk is unavailable, per TkVillage testing guidance.
"""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vectorloom import geometry as geo  # noqa: E402
from vectorloom import model, render  # noqa: E402


def test_normalize_fills_defaults_and_ids():
    doc = model.normalize_document({"root": {"type": "rect", "x": 0, "y": 0, "w": 10, "h": 10}})
    assert doc["format"] == "vectorloom"
    # A bare primitive root is wrapped in a group.
    assert doc["root"]["type"] == "group"
    child = doc["root"]["children"][0]
    assert child["id"]  # an id was fabricated
    assert child["style"]["stroke"] == "#222222"


def test_unknown_node_type_rejected():
    with pytest.raises(model.VloomError):
        model.normalize_document({"root": {"type": "blob"}})


def test_instance_unknown_def_rejected():
    with pytest.raises(model.VloomError):
        model.normalize_document({"root": {"type": "instance", "def": "missing"}})


def test_style_reference_resolution():
    doc = model.normalize_document({
        "styles": {"box": {"stroke": "#ff0000", "width": 3}},
        "root": {"type": "group", "id": "root", "children": [
            {"type": "rect", "id": "r", "x": 0, "y": 0, "w": 5, "h": 5, "style": "box", "fill": "#00ff00"},
        ]},
    })
    style = doc["root"]["children"][0]["style"]
    assert style["stroke"] == "#ff0000"   # from named style
    assert style["fill"] == "#00ff00"     # shorthand override wins
    assert style["width"] == 3.0


def test_transform_compose_and_apply():
    m = geo.from_trs(10, 20, 2, 2, 0)
    assert geo.apply_point(m, 1, 1) == (12.0, 22.0)
    rot = geo.from_trs(0, 0, 1, 1, 90)
    x, y = geo.apply_point(rot, 1, 0)
    assert math.isclose(x, 0.0, abs_tol=1e-9)
    assert math.isclose(y, 1.0, abs_tol=1e-9)


def test_document_bounds_of_primitives():
    doc = model.load_file(os.path.join(os.path.dirname(__file__), "..", "examples", "primitives.vloom.json"))
    bounds = render.document_bounds(doc)
    assert bounds is not None
    minx, miny, maxx, maxy = bounds
    assert minx < maxx and miny < maxy


def test_render_to_real_canvas():
    tk = pytest.importorskip("tkinter")
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available in this environment")
    try:
        root.withdraw()
        canvas = tk.Canvas(root, width=400, height=300)
        doc = model.load_file(os.path.join(os.path.dirname(__file__), "..", "examples", "folder_node.vloom.json"))
        result = render.render_document(canvas, doc)
        assert result["items"]            # something was drawn
        assert result["connectors"]       # ports/connectors were resolved
    finally:
        root.destroy()

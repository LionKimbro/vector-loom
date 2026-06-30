# Vector Loom

A data format, runtime, and editor for **2-D nestable vector structures** —
small, structural, agent-readable visual objects that render onto a tkinter
`Canvas`. Think of it as the missing layer between raw Canvas primitives and a
heavyweight vector editor: a constrained visual vocabulary that programs and
coding agents can author, reason about, and reuse.

## The three legs

1. **Format** — a JSON document describing a tree of vector structures:
   `line`, `rect`, `oval`, `polyline`, `port` (connector points), `text`,
   `group` (local coordinate systems), and `defs` + `instance` (reusable
   structures placed by reference). Files are `*.vloom.json`.
   See [docs/raw/0001__vectorloom-format_v1.json](docs/raw/0001__vectorloom-format_v1.json).
2. **Runtime** — pure-Python rendering. It normalizes a document at the castle
   gate, composes transforms (translate / scale / rotate), flattens every
   primitive to world-space points (so rotation and scaling are *exact*, unlike
   tkinter's native rect/oval items), draws to a `Canvas`, and resolves
   connector world positions for attachment and hit-testing. Works without the
   editor. A headless **PNG exporter** renders documents with no display.
3. **Editor** — a TkVillage-hosted Canvas window following Lion's tkinter
   conventions (reducer core, semantic events, projection). Currently supports
   pan / zoom / fit over a loaded document; direct editing is the next layer.

## Quickstart

```bash
# View a document (drag = pan, mouse wheel = zoom, f = fit, q = quit)
python run_viewer.py examples/folder_node.vloom.json

# Open it in the TkVillage editor scaffold
python run_editor.py examples/folder_node.vloom.json

# Render headlessly to a PNG (no display needed)
PYTHONPATH=src python -m vectorloom.export_png examples/folder_node.vloom.json out.png

# Tests
python -m pytest tests/ -q
```

## A taste of the format

```json
{
  "vectorloom": "1",
  "defs": {
    "folder_node": {
      "type": "group", "id": "folder_node",
      "connectors": {"output": {"x": 110, "y": 45, "role": "output"}},
      "children": [
        {"type": "rect", "id": "body", "x": 0, "y": 12, "w": 110, "h": 66, "style": "panel"},
        {"type": "port", "id": "out", "x": 110, "y": 45, "role": "output"}
      ]
    }
  },
  "root": {
    "type": "group", "id": "root",
    "children": [
      {"type": "instance", "id": "launch", "def": "folder_node", "x": 60, "y": 60},
      {"type": "instance", "id": "stage",  "def": "folder_node", "x": 320, "y": 60}
    ]
  }
}
```

## Runtime API

```python
from vectorloom import load_file, render_document, document_bounds

doc = load_file("examples/folder_node.vloom.json")    # normalized + validated
result = render_document(canvas, doc, base_transform)  # -> {items, by_item, connectors}
bounds = document_bounds(doc)                          # (min_x, min_y, max_x, max_y)
```

## Status

v1 foundation: format spec, pure runtime renderer, headless PNG export, a
standalone viewer, an editor scaffold, and tests. Next: direct manipulation in
the editor (select / move / create / connect), connector snap semantics, and a
SoftSpec formalization of the format. Text is experimental — tkinter Canvas
text does not scale/rotate consistently; a stroke-font built from these same
primitives may replace it.

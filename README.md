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
3. **Editor** — a full **CIRA**-structured structural editor hosted on
   TkVillage. Click to select, drag to move, add/delete primitives, edit node
   JSON in an inspector, save, and undo/redo — with pan/zoom/fit. The
   architecture is laid out by CIRA subsystem (see below) so specialized
   workbenches can be built on the same seams.

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

## Editor architecture (CIRA on TkVillage)

The editor is built on the Coordinated Interactive Runtime Architecture from the
start. Each module owns one CIRA subsystem; the TkVillage tick *is* the CIRA
loop. A workbench is added by registering a new window kind that reuses the
World Model, History, and Discrete vocabulary and supplies its own organisms,
projection overlays, and node templates.

| CIRA subsystem | Module | Owns |
|---|---|---|
| Continuity Engine | `editor/continuity.py` | RAW input, tokenizers (hit-testing), Judge, select/move/pan organisms. Emits semantic events + immediates. |
| Discrete Engine | `editor/discrete.py` | Pure reducer; selection + desired camera; emits effects (never mutates world). |
| World Model | `editor/world.py` | Document store + mutations (find/move/add/delete/replace) + atomic save. |
| History Manager | `editor/history.py` | Checkpoint snapshots; undo/redo state jumps (one per completed edit). |
| Projection | `editor/projection.py` | Renders document + selection/hover/drag overlays + inspector. Non-authoritative. |
| Runtime | `editor/app.py` | TkVillage glue: `on_tick` continuity driver + effect-routing reducer adapter. |

Flow: thin Tk callbacks write RAW → `on_tick` runs Continuity (tokenize →
organisms) which posts semantic events and writes immediates → the reducer
adapter (Discrete) processes events and routes effects to World/History →
Projection redraws. During a drag the dragged shape itself follows the cursor
(Projection shifts its rendered items each tick via a `DRAG_PREVIEW` immediate);
the model is untouched until the completed drag commits one `NODE_MOVED` (one
undo step).

## Status

Working editor milestone: open a `.vloom.json`, click-select, drag-move,
add/delete rect/oval/line/polyline/port/group, edit node JSON, save, reload, and
undo/redo — all on full CIRA. The pure runtime (format, renderer, PNG export,
viewer) is dependency-free except Pillow.

Dragging moves the real shape live under the cursor, and **connector snapping**
works: dragging a node with ports near a compatible connector (output↔input,
bidirectional↔any, anchor↔anchor) snaps it exactly onto the target, with a live
ring overlay marking the connection. Snap is a tokenizer (spatial candidate
computation) consulted by the move organism — the first piece of the Diagram
Workbench.

Next: a CONNECT semantic action that records an actual edge/wire when a snap
commits, a Glyph Workbench (strokes/baselines/advance width), and a SoftSpec
formalization of the format. Text is experimental — tkinter Canvas text does not
scale/rotate consistently; a stroke-font built from these same primitives may
replace it.

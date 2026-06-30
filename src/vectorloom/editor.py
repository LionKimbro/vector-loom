"""Vector Loom editor scaffold, hosted on TkVillage.

This is the third leg of the project (format, runtime, editor). It is an honest
scaffold: it summons a Canvas window that renders a loaded document and supports
pan, zoom, and fit through the conventional pipeline. Direct editing (select,
move, create) is the next layer and is intentionally not built yet.

Conventions followed (lions-tkinter-development-conventions.v1):
  - Hidden root; visible window is a TkVillage Toplevel window kind.
  - Callbacks are thin adapters that post semantic events; they do no logic.
  - A reducer core owns compact semantic state (the desired camera + status).
  - The document is durable world-model data, kept out of reducer state in DOCS.
  - Projection redraws the Canvas from state; it decides no semantic truth.
  - Pan/zoom are continuous gestures; the widget adapter derives dx/dy/step and
    posts semantic camera events. A fuller localized CIRA can replace this when
    real direct manipulation (drag-select, connect, draw) is added.

Run it:
    python run_editor.py examples/folder_node.vloom.json
"""

import os
import sys
import tkinter as tk

# Bootstrap TkVillage from its source checkout if it is not installed.
_TKV_SRC = r"C:\lion\github\tkvillage\src"
if _TKV_SRC not in sys.path and os.path.isdir(_TKV_SRC):
    sys.path.insert(0, _TKV_SRC)

import tkvillage as village  # noqa: E402

from . import geometry as geo  # noqa: E402
from . import model  # noqa: E402
from . import render  # noqa: E402


CANVAS_WINDOW = "canvas"

# Semantic events
FIT_REQUESTED = "FIT_REQUESTED"
PAN_BY = "PAN_BY"
ZOOM_AT = "ZOOM_AT"

# World-model surrogate: normalized documents keyed by path. Loading is a
# filesystem action and so happens here, outside the reducer.
DOCS = {}


# --------------------------------------------------------------------------
# window kind: state, widgets, reducer, projection
# --------------------------------------------------------------------------

def make_initial_state(_rt, key=None, payload=None):
    """Compact semantic state: the desired camera and a status line."""
    return {
        "doc_path": payload["doc_path"],
        "scale": 1.0,
        "ox": 0.0,
        "oy": 0.0,
        "fit_pending": True,
        "status": "Loaded",
    }


def create(_rt, record):
    """Build the Canvas and status bar; wire thin event-posting callbacks."""
    top = record["toplevel"]
    top.geometry("960x680")
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)

    canvas = tk.Canvas(top, background="#fafafa", highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")
    status = tk.Label(top, anchor="w", padx=6, pady=2, fg="#2e7d32")
    status.grid(row=1, column=0, sticky="ew")

    record["widgets"]["canvas"] = canvas
    record["widgets"]["status"] = status
    record["widgets"]["drag"] = None  # adapter-local pan bookkeeping

    window_id = record["window_id"]

    canvas.bind("<ButtonPress-1>", lambda e: _begin_pan(record, e))
    canvas.bind("<B1-Motion>", lambda e: _continue_pan(window_id, record, e))
    canvas.bind("<MouseWheel>", lambda e: village.post_event_to_window(
        window_id, {"type": ZOOM_AT, "x": e.x, "y": e.y, "step": e.delta}))
    canvas.bind("<Button-4>", lambda e: village.post_event_to_window(
        window_id, {"type": ZOOM_AT, "x": e.x, "y": e.y, "step": 120}))
    canvas.bind("<Button-5>", lambda e: village.post_event_to_window(
        window_id, {"type": ZOOM_AT, "x": e.x, "y": e.y, "step": -120}))
    top.bind("f", lambda e: village.post_event_to_window(
        window_id, {"type": FIT_REQUESTED, "w": canvas.winfo_width(), "h": canvas.winfo_height()}))


def _begin_pan(record, event):
    record["widgets"]["drag"] = (event.x, event.y)


def _continue_pan(window_id, record, event):
    drag = record["widgets"]["drag"]
    if not drag:
        return
    sx, sy = drag
    record["widgets"]["drag"] = (event.x, event.y)
    village.post_event_to_window(window_id, {"type": PAN_BY, "dx": event.x - sx, "dy": event.y - sy})


def reduce_event(_rt, state, event):
    """Update the desired camera from semantic events. Pure: reads only state,
    the event, and (for fit) the document bounds from the world model."""
    kind = event["type"]
    if kind == PAN_BY:
        new = dict(state)
        new["ox"] = state["ox"] + event["dx"]
        new["oy"] = state["oy"] + event["dy"]
        new["status"] = "Pan"
        return new, []
    if kind == ZOOM_AT:
        factor = 1.1 if event["step"] > 0 else (1.0 / 1.1)
        wx = (event["x"] - state["ox"]) / state["scale"]
        wy = (event["y"] - state["oy"]) / state["scale"]
        new = dict(state)
        new["scale"] = state["scale"] * factor
        new["ox"] = event["x"] - wx * new["scale"]
        new["oy"] = event["y"] - wy * new["scale"]
        new["status"] = f"Zoom {new['scale']:.2f}x"
        return new, []
    if kind == FIT_REQUESTED:
        new = dict(_fit_camera(DOCS[state["doc_path"]], event["w"], event["h"]))
        merged = dict(state)
        merged.update(new)
        merged["fit_pending"] = False
        merged["status"] = "Fit"
        return merged, []
    return state, []


def project(_rt, record):
    """Redraw the Canvas from camera state and the world-model document."""
    state = record["state"]
    canvas = record["widgets"]["canvas"]
    status = record["widgets"]["status"]
    doc = DOCS[state["doc_path"]]

    # Resolve a deferred fit once the canvas has a real size.
    if state["fit_pending"]:
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w > 1 and h > 1:
            cam = _fit_camera(doc, w, h)
            state["scale"], state["ox"], state["oy"] = cam["scale"], cam["ox"], cam["oy"]
            state["fit_pending"] = False

    base = geo.compose(geo.translate(state["ox"], state["oy"]), geo.scale(state["scale"], state["scale"]))
    canvas.delete("all")
    render.render_document(canvas, doc, base)
    status.configure(text=f"{os.path.basename(state['doc_path'])}   |   {state['status']}   (drag=pan, wheel=zoom, f=fit)")


def _fit_camera(doc, w, h):
    bounds = render.document_bounds(doc)
    if not bounds or w <= 1 or h <= 1:
        return {"scale": 1.0, "ox": (w or 960) / 2.0, "oy": (h or 680) / 2.0}
    minx, miny, maxx, maxy = bounds
    span_x = max(maxx - minx, 1.0)
    span_y = max(maxy - miny, 1.0)
    scale = min(w * 0.85 / span_x, h * 0.85 / span_y)
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    return {"scale": scale, "ox": w / 2.0 - cx * scale, "oy": h / 2.0 - cy * scale}


def register():
    village.register_window_kind(
        CANVAS_WINDOW,
        title="Vector Loom",
        multiplicity="per-key",
        create=create,
        make_initial_state=make_initial_state,
        reduce_event=reduce_event,
        project=project,
    )


def run_editor(doc_path):
    """Load a document and open the editor window on the TkVillage runtime."""
    DOCS[doc_path] = model.load_file(doc_path)
    village.create_app("vectorloom", ".vectorloom")
    register()
    village.summon_window(CANVAS_WINDOW, key=doc_path, payload={"doc_path": doc_path})
    village.run()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m vectorloom.editor <document.vloom.json>")
        return 1
    run_editor(argv[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

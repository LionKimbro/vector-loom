"""Projection: build the window's widgets and render state onto them.

Projection is downstream and non-authoritative. It reads the World Model
document, the Discrete Engine's selection and camera, and the Continuity
Engine's immediates, then reconciles the visible Canvas and the inspector. It
decides no semantic truth and creates no semantic events except through explicit
GUI callback adapters (toolbar buttons, keys) that post events.
"""

import json
import tkinter as tk

import tkvillage as village

from .. import geometry as geo
from .. import render
from .. import symbols as S
from . import continuity
from . import discrete
from . import events as E
from . import world

_STATUS_COLORS = {"ok": "#2e7d32", "error": "#c62828", "info": "#222222", "phase": "#1565c0"}


def create(_rt, record):
    """Build the editor shell: toolbar, canvas, inspector, status bar."""
    top = record["toplevel"]
    top.title("Vector Loom Editor")
    top.geometry("1140x740")
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)

    record["state"]["window_id"] = record["window_id"]
    window_id = record["window_id"]

    def post(event):
        village.post_event_to_window(window_id, event)

    _build_toolbar(top, post).grid(row=0, column=0, columnspan=2, sticky="ew")

    canvas = tk.Canvas(top, background="#fafafa", highlightthickness=0)
    canvas.grid(row=1, column=0, sticky="nsew")

    inspector = _build_inspector(top, record, post)
    inspector["frame"].grid(row=1, column=1, sticky="ns")

    status = tk.Label(top, anchor="w", padx=6, pady=2, fg=_STATUS_COLORS["ok"])
    status.grid(row=2, column=0, columnspan=2, sticky="ew")

    record["widgets"]["canvas"] = canvas
    record["widgets"]["status"] = status
    record["widgets"]["inspector"] = inspector["text"]
    record["widgets"]["path_label"] = inspector["path_label"]
    record["projection"] = {"by_item": {}}
    record["inspector_path"] = "<unset>"

    continuity.init_continuity(record)
    continuity.bind_raw(record)
    _bind_camera_and_keys(top, canvas, post)


def project(_rt, record):
    """Render the document plus selection/hover/drag overlays and the inspector."""
    state = record["state"]
    canvas = record["widgets"]["canvas"]
    doc = world.get(state["doc_path"])

    if state["fit_pending"]:
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w > 1 and h > 1:
            cam = discrete.fit_camera(doc, w, h)
            state["scale"], state["ox"], state["oy"] = cam["scale"], cam["ox"], cam["oy"]
            state["fit_pending"] = False

    base = geo.compose(geo.translate(state["ox"], state["oy"]), geo.scale(state["scale"], state["scale"]))
    canvas.delete("all")
    result = render.render_document(canvas, doc, base)
    record["projection"]["by_item"] = result["by_item"]

    _draw_overlays(canvas, doc, state, base, result["by_item"], record.get("immediates", []))
    _update_inspector(record, doc, state)
    _update_status(record, state)


# --------------------------------------------------------------------------
# overlays
# --------------------------------------------------------------------------

def _draw_overlays(canvas, doc, state, base, by_item, immediates):
    drag = next((i for i in immediates if i["type"] == E.DRAG_PREVIEW), None)

    if drag is not None:
        # Live drag: shift the actual rendered items of the dragged node by the
        # current pixel delta, so the real shape follows the cursor. The model
        # is untouched until NODE_MOVED commits on release. Re-render each tick
        # draws at the origin; this move re-applies the cumulative delta.
        _move_subtree(canvas, by_item, drag["path"], drag["sdx"], drag["sdy"])
        bb = render.path_world_bounds(doc, drag["path"], base)
        if bb:
            minx, miny, maxx, maxy = _pad(bb, 3)
            canvas.create_rectangle(
                minx + drag["sdx"], miny + drag["sdy"], maxx + drag["sdx"], maxy + drag["sdy"],
                outline="#1565c0", width=2, dash=(4, 2))
        return  # suppress hover/static selection while dragging

    for imm in immediates:
        if imm["type"] == E.HOVER and imm["path"] != state["selection"]:
            bb = render.path_world_bounds(doc, imm["path"], base)
            if bb:
                canvas.create_rectangle(*_pad(bb, 2), outline="#90a4ae", width=1)

    if state["selection"]:
        bb = render.path_world_bounds(doc, state["selection"], base)
        if bb:
            canvas.create_rectangle(*_pad(bb, 3), outline="#1565c0", width=2, dash=(4, 2))


def _move_subtree(canvas, by_item, path, dx, dy):
    """Shift every rendered item belonging to a node (and its subtree) by (dx, dy)."""
    for item, item_path in by_item.items():
        if item_path == path or item_path.startswith(path + ".") or item_path.startswith(path + "="):
            canvas.move(item, dx, dy)


def _pad(bb, n):
    minx, miny, maxx, maxy = bb
    return (minx - n, miny - n, maxx + n, maxy + n)


# --------------------------------------------------------------------------
# inspector + status
# --------------------------------------------------------------------------

def _update_inspector(record, doc, state):
    sel = state["selection"]
    record["widgets"]["path_label"].configure(text=sel or "(no selection)")
    # Do not clobber the text while the user is editing it.
    if record["toplevel"].focus_get() is record["widgets"]["inspector"]:
        return
    node = world.find_node(doc, sel) if sel else None
    text = json.dumps(node, indent=2) if node else ""
    widget = record["widgets"]["inspector"]
    widget.delete("1.0", "end")
    widget.insert("1.0", text)
    record["inspector_path"] = sel


def _update_status(record, state):
    label = record["widgets"]["status"]
    label.configure(text=state["status"], fg=_STATUS_COLORS.get(state["status_kind"], "#222222"))


# --------------------------------------------------------------------------
# widget construction + callback adapters
# --------------------------------------------------------------------------

def _build_toolbar(top, post):
    bar = tk.Frame(top, padx=4, pady=4)
    adders = [("Rect", S.RECT), ("Oval", S.OVAL), ("Line", S.LINE),
              ("Polyline", S.POLYLINE), ("Port", S.PORT), ("Group", S.GROUP)]
    for label, kind in adders:
        tk.Button(bar, text=f"+ {label}", command=lambda k=kind: post({"type": E.NODE_ADDED, "kind": k})).pack(side="left", padx=2)
    tk.Frame(bar, width=12).pack(side="left")
    tk.Button(bar, text="Delete", command=lambda: post({"type": E.NODE_DELETED})).pack(side="left", padx=2)
    tk.Button(bar, text="Undo", command=lambda: post({"type": E.UNDO})).pack(side="left", padx=2)
    tk.Button(bar, text="Redo", command=lambda: post({"type": E.REDO})).pack(side="left", padx=2)
    tk.Button(bar, text="Save", command=lambda: post({"type": E.SAVE_FILE})).pack(side="left", padx=2)
    return bar


def _build_inspector(top, record, post):
    frame = tk.Frame(top, padx=6, pady=4, width=300)
    frame.grid_propagate(False)
    tk.Label(frame, text="Selected node", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
    path_label = tk.Label(frame, text="(no selection)", anchor="w", fg="#555555", wraplength=280, justify="left")
    path_label.pack(anchor="w", fill="x")
    text = tk.Text(frame, width=38, height=30, font=("TkFixedFont", 9), wrap="none")
    text.pack(fill="both", expand=True, pady=4)

    def apply_edits():
        sel = record["state"]["selection"]
        if not sel:
            return
        try:
            node = json.loads(record["widgets"]["inspector"].get("1.0", "end"))
        except json.JSONDecodeError as exc:
            record["widgets"]["status"].configure(text=f"Invalid JSON: {exc}", fg=_STATUS_COLORS["error"])
            return
        post({"type": E.NODE_FIELD_CHANGED, "path": sel, "node": node})

    tk.Button(frame, text="Apply edits", command=apply_edits).pack(anchor="e")
    return {"frame": frame, "text": text, "path_label": path_label}


def _bind_camera_and_keys(top, canvas, post):
    canvas.bind("<MouseWheel>", lambda e: post({"type": E.ZOOM_AT, "x": e.x, "y": e.y, "step": e.delta}))
    canvas.bind("<Button-4>", lambda e: post({"type": E.ZOOM_AT, "x": e.x, "y": e.y, "step": 120}))
    canvas.bind("<Button-5>", lambda e: post({"type": E.ZOOM_AT, "x": e.x, "y": e.y, "step": -120}))
    top.bind("f", lambda e: post({"type": E.FIT_REQUESTED, "w": canvas.winfo_width(), "h": canvas.winfo_height()}))
    top.bind("<Delete>", lambda e: post({"type": E.NODE_DELETED}))
    top.bind("<Control-s>", lambda e: post({"type": E.SAVE_FILE}))
    top.bind("<Control-z>", lambda e: post({"type": E.UNDO}))
    top.bind("<Control-y>", lambda e: post({"type": E.REDO}))

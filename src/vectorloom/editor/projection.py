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
from . import handles as handles_mod
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

    # Continuous manipulation (move / resize / rotate) carries a temporary
    # transform intercept at the manipulated node's path. The renderer resolves
    # the node, its subtree, connectors, and wires through that one transform —
    # a coherent preview, model untouched. Move sends a translate; resize/rotate
    # send the full transform.
    immediates = record.get("immediates", [])
    preview = next((i for i in immediates if i["type"] in (E.DRAG_PREVIEW, E.TRANSFORM_PREVIEW)), None)
    overlay = _overlay_from_preview(preview)

    canvas.delete("all")
    result = render.render_document(canvas, doc, base, overlay=overlay)
    record["projection"]["by_item"] = result["by_item"]
    record["projection"]["connectors"] = result["connectors"]
    record["projection"]["connections"] = result["connections"]

    # Selection bounds and handles resolve through the same overlay, so they track
    # the previewed shape during a manipulation.
    sel = state["selection"]
    sel_bb = render.path_world_bounds(doc, sel, base, overlay=overlay) if sel else None
    record["projection"]["handles"] = handles_mod.layout(sel_bb, state["handle_mode"]) if sel else []

    _draw_overlays(canvas, doc, state, base, sel_bb, record["projection"]["handles"], preview, immediates)
    _update_inspector(record, doc, state)
    _update_status(record, state)


def _overlay_from_preview(preview):
    if preview is None:
        return None
    if preview["type"] == E.DRAG_PREVIEW:
        return {preview["path"]: geo.translate(preview["sdx"], preview["sdy"])}
    return {preview["path"]: preview["transform"]}


# --------------------------------------------------------------------------
# selection / handles / hover / snap overlays (the model-untouched decorations)
# --------------------------------------------------------------------------

def _draw_overlays(canvas, doc, state, base, sel_bb, handle_list, preview, immediates):
    if preview is None:
        for imm in immediates:
            if imm["type"] == E.HOVER and imm["path"] != state["selection"]:
                bb = render.path_world_bounds(doc, imm["path"], base)
                if bb:
                    canvas.create_rectangle(*_pad(bb, 2), outline="#90a4ae", width=1)

    if sel_bb is not None:
        canvas.create_rectangle(*_pad(sel_bb, 3), outline="#1565c0", width=2, dash=(4, 2))
    _draw_handles(canvas, handle_list)

    if preview is not None:
        snap = next((i for i in immediates if i["type"] == E.SNAP), None)
        if snap is not None:
            tx, ty = snap["target_world"]
            canvas.create_oval(tx - 9, ty - 9, tx + 9, ty + 9, outline="#ff6f00", width=3)


def _draw_handles(canvas, handle_list):
    r = handles_mod.HANDLE_RADIUS
    for h in handle_list:
        x, y = h["x"], h["y"]
        if h["kind"] == E.HANDLE_RESIZE:
            canvas.create_rectangle(x - r, y - r, x + r, y + r, fill="#ffffff", outline="#1565c0", width=2)
        else:  # rotate
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff3e0", outline="#ff6f00", width=2)


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

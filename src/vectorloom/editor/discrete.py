"""Discrete Engine: the pure reducer core of the editor.

It owns compact workspace/editor state — the committed selection, the desired
semantic camera, and the document path reference — and processes semantic
events into a new state plus explicit effects. It never touches Tk, the
filesystem, time, or randomness, and it never mutates the World Model directly:
mutations are *described* as WORLD_MUTATE / CHECKPOINT / STATE_JUMP / SAVE /
RELOAD effects that the runtime routes.

It may *read* the World Model (passed in as `doc`) to make semantic decisions
such as which group a new node belongs to, or to fit the camera to the content.
Reading across a boundary is allowed; mutating across it is not.

    new_state, effects = reduce(state, event, doc)
"""

from .. import render
from .. import symbols as S
from . import events as E


def make_initial_state(_rt, key=None, payload=None):
    """Compact semantic state. The document itself lives in the World Model."""
    return {
        "doc_path": payload["doc_path"],
        "selection": None,
        "scale": 1.0,
        "ox": 0.0,
        "oy": 0.0,
        "fit_pending": True,
        "status": "Loaded",
        "status_kind": "ok",
    }


def reduce(state, event, doc):
    kind = event["type"]

    if kind == E.SET_SELECTION:
        new = dict(state)
        new["selection"] = event["path"]
        new["status"] = f"Selected {event['path']}" if event["path"] else "Deselected"
        new["status_kind"] = "info"
        return new, []

    if kind == E.NODE_MOVED:
        new = dict(state)
        new["selection"] = event["path"]
        new["status"] = f"Moved {event['path']}"
        new["status_kind"] = "ok"
        return new, [
            {"type": E.WORLD_MUTATE, "op": E.OP_MOVE, "path": event["path"], "dx": event["dx"], "dy": event["dy"]},
            {"type": E.CHECKPOINT},
        ]

    if kind == E.NODE_ADDED:
        parent = state["selection"] if _selection_is_group(state, doc) else doc["root"]["id"]
        new = dict(state)
        new["status"] = f"Added {event['kind']}"
        new["status_kind"] = "ok"
        return new, [
            {"type": E.WORLD_MUTATE, "op": E.OP_ADD, "parent": parent, "node": _template(event["kind"])},
            {"type": E.CHECKPOINT},
        ]

    if kind == E.NODE_DELETED:
        path = state["selection"]
        if not path or path == doc["root"]["id"]:
            return _warn(state, "Nothing deletable selected"), []
        new = dict(state)
        new["selection"] = None
        new["status"] = f"Deleted {path}"
        new["status_kind"] = "ok"
        return new, [
            {"type": E.WORLD_MUTATE, "op": E.OP_DELETE, "path": path},
            {"type": E.CHECKPOINT},
        ]

    if kind == E.NODE_FIELD_CHANGED:
        new = dict(state)
        new["status"] = f"Edited {event['path']}"
        new["status_kind"] = "ok"
        return new, [
            {"type": E.WORLD_MUTATE, "op": E.OP_REPLACE, "path": event["path"], "node": event["node"]},
            {"type": E.CHECKPOINT},
        ]

    if kind == E.SAVE_FILE:
        return state, [{"type": E.SAVE}]

    if kind == E.LOAD_FILE:
        return state, [{"type": E.RELOAD}]

    if kind == E.UNDO:
        return state, [{"type": E.STATE_JUMP, "direction": "undo"}]

    if kind == E.REDO:
        return state, [{"type": E.STATE_JUMP, "direction": "redo"}]

    # --- camera (desired semantic camera; never checkpointed) ---
    if kind == E.PAN_BY:
        new = dict(state)
        new["ox"] = state["ox"] + event["dx"]
        new["oy"] = state["oy"] + event["dy"]
        return new, []

    if kind == E.ZOOM_AT:
        factor = 1.1 if event["step"] > 0 else (1.0 / 1.1)
        wx = (event["x"] - state["ox"]) / state["scale"]
        wy = (event["y"] - state["oy"]) / state["scale"]
        new = dict(state)
        new["scale"] = state["scale"] * factor
        new["ox"] = event["x"] - wx * new["scale"]
        new["oy"] = event["y"] - wy * new["scale"]
        return new, []

    if kind == E.FIT_REQUESTED:
        new = dict(state)
        new.update(fit_camera(doc, event["w"], event["h"]))
        new["fit_pending"] = False
        return new, []

    return state, []


# --------------------------------------------------------------------------

def fit_camera(doc, w, h):
    """Compute camera fields that fit the document into a w x h viewport."""
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


def _selection_is_group(state, doc):
    from . import world
    return bool(state["selection"]) and world.is_group(doc, state["selection"])


def _warn(state, message):
    new = dict(state)
    new["status"] = message
    new["status_kind"] = "error"
    return new


def _template(kind):
    """Loose default node for a newly created primitive of the given kind."""
    if kind == S.RECT:
        return {"type": S.RECT, "x": 20, "y": 20, "w": 90, "h": 60, "stroke": "#222222"}
    if kind == S.OVAL:
        return {"type": S.OVAL, "x": 20, "y": 20, "w": 90, "h": 60, "stroke": "#c62828"}
    if kind == S.LINE:
        return {"type": S.LINE, "x1": 20, "y1": 20, "x2": 120, "y2": 90, "stroke": "#222222", "width": 2}
    if kind == S.POLYLINE:
        return {"type": S.POLYLINE, "points": [[20, 20], [70, 70], [120, 20]], "stroke": "#222222", "width": 2}
    if kind == S.PORT:
        return {"type": S.PORT, "x": 40, "y": 40, "role": "anchor"}
    if kind == S.GROUP:
        return {"type": S.GROUP, "x": 40, "y": 40, "children": []}
    return {"type": S.RECT, "x": 20, "y": 20, "w": 60, "h": 40}

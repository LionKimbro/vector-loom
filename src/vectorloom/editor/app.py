"""Runtime glue: host the CIRA loop on TkVillage.

This module is the Runtime in CIRA terms. It owns loop ordering and effect
routing, and it adapts the pure Discrete Engine onto TkVillage's reducer slot:

  - Thin Tk callbacks (continuity.bind_raw) write RAW each between ticks.
  - on_tick() runs the Continuity Engine: tokenize -> organisms -> post semantic
    events + write immediates, then request projection when something changed.
  - reduce_event() adapts the pure reducer: it calls discrete.reduce(), then
    routes the domain effects (world mutation, checkpoint, save, reload, state
    jump) through the World Model and History Manager. The reducer stays pure;
    the runtime performs the effects.

Per-tick order in TkVillage is: drain queue (reduce) -> route effects -> on_tick
-> project dirty windows. So organisms' committed events are reduced on the next
tick (invisible latency), while immediates written in on_tick are projected the
same tick (smooth drag/hover).
"""

import os
import sys

# Bootstrap TkVillage from its source checkout if it is not installed.
_TKV_SRC = r"C:\lion\github\tkvillage\src"
if _TKV_SRC not in sys.path and os.path.isdir(_TKV_SRC):
    sys.path.insert(0, _TKV_SRC)

import tkvillage as village  # noqa: E402

from .. import geometry as geo  # noqa: E402
from . import continuity  # noqa: E402
from . import discrete  # noqa: E402
from . import events as E  # noqa: E402
from . import history  # noqa: E402
from . import projection  # noqa: E402
from . import world  # noqa: E402

CANVAS_WINDOW = "canvas"


# --------------------------------------------------------------------------
# Discrete adapter + effect routing (the Runtime's job)
# --------------------------------------------------------------------------

def reduce_event(_rt, state, event):
    doc = world.get(state["doc_path"])
    new_state, effects = discrete.reduce(state, event, doc)
    for effect in effects:
        new_state = _route_domain_effect(effect, new_state)
    return new_state, [{"type": "REQUEST_PROJECT", "window_id": state["window_id"]}]


def _route_domain_effect(effect, state):
    doc_path = state["doc_path"]
    doc = world.get(doc_path)
    kind = effect["type"]

    if kind == E.WORLD_MUTATE:
        return _route_world_mutate(effect, state, doc)
    if kind == E.CHECKPOINT:
        history.push(doc_path, world.get(doc_path), state["selection"])
        return state
    if kind == E.SAVE:
        world.save(doc_path, doc)
        return _status(state, f"Saved {os.path.basename(doc_path)}", "ok")
    if kind == E.RELOAD:
        world.load(doc_path)
        history.init(doc_path, world.get(doc_path), None)
        out = _status(state, "Reloaded from disk", "phase")
        out["selection"] = None
        out["fit_pending"] = True
        return out
    if kind == E.STATE_JUMP:
        return _route_state_jump(effect, state, doc_path)
    return state


def _route_world_mutate(effect, state, doc):
    op = effect["op"]
    if op == E.OP_MOVE:
        world.move_node(doc, effect["path"], effect["dx"], effect["dy"])
        return state
    if op == E.OP_ADD:
        new_path = world.add_child(doc, effect["parent"], effect["node"])
        out = dict(state)
        out["selection"] = new_path
        out["handle_mode"] = E.MODE_RESIZE
        return out
    if op == E.OP_DELETE:
        world.delete_node(doc, effect["path"])
        return state
    if op == E.OP_REPLACE:
        world.replace_node(doc, effect["path"], effect["node"])
        return state
    if op == E.OP_CONNECT:
        world.add_connection(doc, effect["connect"]["from"], effect["connect"]["to"])
        return state
    if op == E.OP_TRANSFORM:
        # The transform is in screen space; baking it needs the camera so it can
        # be conjugated into the node's local frame.
        camera = geo.compose(geo.translate(state["ox"], state["oy"]),
                             geo.scale(state["scale"], state["scale"]))
        world.apply_screen_transform(doc, effect["path"], tuple(effect["transform"]), camera)
        return state
    return state


def _route_state_jump(effect, state, doc_path):
    snap = history.undo(doc_path) if effect["direction"] == "undo" else history.redo(doc_path)
    if snap is None:
        return _status(state, f"Nothing to {effect['direction']}", "info")
    world.set_document(doc_path, snap["doc"])
    out = _status(state, effect["direction"].capitalize(), "phase")
    out["selection"] = snap["selection"]
    return out


def _status(state, message, kind):
    out = dict(state)
    out["status"] = message
    out["status_kind"] = kind
    return out


# --------------------------------------------------------------------------
# Continuity driver (runs each tick before projection)
# --------------------------------------------------------------------------

def on_tick(_rt, record):
    record["immediates"] = []
    derived = continuity.tokenize(record)
    out_events = []
    continuity.run_organisms(record, derived, out_events)
    for event in out_events:
        village.post_event_to_window(record["window_id"], event)

    hover_target = next((i["path"] for i in record["immediates"] if i["type"] == E.HOVER), None)
    hover_changed = hover_target != record["last_hover"]
    record["last_hover"] = hover_target
    # Any manipulation preview (move, resize, rotate) must drive a per-frame
    # reprojection so the overlay updates live, not only on commit.
    has_preview = any(i["type"] in (E.DRAG_PREVIEW, E.TRANSFORM_PREVIEW) for i in record["immediates"])

    continuity.promote_raw(record)

    need_projection = bool(out_events) or has_preview or hover_changed or record["state"]["fit_pending"]
    if need_projection:
        return [{"type": "REQUEST_PROJECT", "window_id": record["window_id"]}]
    return None


# --------------------------------------------------------------------------
# registration + entrypoint
# --------------------------------------------------------------------------

def register():
    village.register_window_kind(
        CANVAS_WINDOW,
        title="Vector Loom",
        multiplicity="per-key",
        create=projection.create,
        make_initial_state=discrete.make_initial_state,
        reduce_event=reduce_event,
        project=projection.project,
        on_tick=on_tick,
    )


def run_editor(doc_path):
    """Load a document and open the editor on the TkVillage runtime.

    The canvas window owns program lifetime: TkVillage's on-window-close policy
    ends the runtime at tick-end once no canvas windows remain, so closing the
    editor window exits the app.
    """
    world.load(doc_path)
    history.init(doc_path, world.get(doc_path), None)
    village.declare_app({
        "name": "vectorloom",
        "project-dir-name": ".vectorloom",
        "tick-interval-ms": 33,
        "shutdown-policy": "on-window-close",
        "shutdown-window-kind": CANVAS_WINDOW,
        "on-shutdown": None,
    })
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

"""Continuity Engine: interpret embodied interaction into semantic meaning.

Thin Tk callbacks write RAW facts (pointer position, button state). Each tick
the runtime calls tokenize() to derive perceptual facts (motion, press/release
edges, the node under the pointer via hit-testing, whether a drag threshold was
crossed), then run_organisms() to advance small gesture finite-state-machines
that consult a Judge for pointer ownership and emit:

  - semantic events (SET_SELECTION, NODE_MOVED, PAN_BY) for the Discrete Engine,
  - immediates (DRAG_PREVIEW, HOVER) for single-frame Projection only.

Boundaries (CIRA): tokenizers do perception (hit-testing) and emit nothing;
organisms run behavior episodes, consult the Judge for contention, and never do
their own hit-testing or mutate world/editor state. This is the seam where a
workbench later adds organisms (e.g. glyph point-drag, connector-snap) without
disturbing the reducer or projection.
"""

import math

from .. import symbols as S
from . import events as E
from . import world

DRAG_THRESHOLD = 4.0  # pixels before a press becomes a drag
SNAP_THRESHOLD = 16.0  # pixels within which a dragged connector snaps to another


def init_continuity(record):
    """Install RAW state, tokenizer bookkeeping, Judge, and organisms."""
    blank = {"x": 0, "y": 0, "button1_down": False, "inside": False}
    record["raw"] = {"current": dict(blank), "previous": dict(blank)}
    record["continuity"] = {"press_x": None, "press_y": None, "press_target": None}
    record["judge"] = {}                       # resource -> owning organism name
    record["gesture"] = {"consumed": False}    # was this gesture handled by pan/drag?
    record["organisms"] = {
        "pan": {"state": "IDLE"},
        "drag": {"state": "IDLE", "path": None},
        "select": {"state": "IDLE"},
    }
    record["immediates"] = []
    record["last_hover"] = None


def bind_raw(record):
    """Bind Tk callbacks that only write RAW facts. No logic lives here."""
    canvas = record["widgets"]["canvas"]
    cur = record["raw"]["current"]

    def on_motion(e):
        cur["x"], cur["y"], cur["inside"] = e.x, e.y, True

    def on_press(e):
        cur["x"], cur["y"], cur["button1_down"] = e.x, e.y, True

    def on_release(e):
        cur["x"], cur["y"], cur["button1_down"] = e.x, e.y, False

    canvas.bind("<Motion>", on_motion)
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<B1-Motion>", on_motion)
    canvas.bind("<Enter>", lambda e: cur.__setitem__("inside", True))
    canvas.bind("<Leave>", lambda e: cur.__setitem__("inside", False))


def tokenize(record):
    """Derive perceptual facts from RAW. Performs hit-testing; emits nothing."""
    cur = record["raw"]["current"]
    prev = record["raw"]["previous"]
    book = record["continuity"]
    canvas = record["widgets"]["canvas"]
    by_item = record["projection"]["by_item"]

    pressed = cur["button1_down"] and not prev["button1_down"]
    released = (not cur["button1_down"]) and prev["button1_down"]
    target = _hit_test(canvas, by_item, cur["x"], cur["y"])

    if pressed:
        book["press_x"], book["press_y"], book["press_target"] = cur["x"], cur["y"], target

    moved = book["press_x"] is not None and \
        math.hypot(cur["x"] - book["press_x"], cur["y"] - book["press_y"]) > DRAG_THRESHOLD
    crossed = cur["button1_down"] and moved

    # Compute snap throughout a drag, including the release frame (button is
    # already up there but `released` is true), so the committed NODE_MOVED uses
    # the snapped delta. Gating on button-down alone would miss the commit.
    snap = None
    if book["press_target"] and moved and (cur["button1_down"] or released):
        connectors = record["projection"].get("connectors", [])
        snap = _snap_candidate(connectors, book["press_target"],
                               cur["x"] - book["press_x"], cur["y"] - book["press_y"])

    return {
        "pressed": pressed,
        "released": released,
        "button_down": cur["button1_down"],
        "target": target,
        "press_target": book["press_target"],
        "press_x": book["press_x"],
        "press_y": book["press_y"],
        "sx": cur["x"],
        "sy": cur["y"],
        "dx": cur["x"] - prev["x"],
        "dy": cur["y"] - prev["y"],
        "threshold_crossed": crossed,
        "snap": snap,
    }


def _snap_candidate(connectors, dragged_path, free_dx, free_dy):
    """Find the best connector-snap for the current free drag delta, or None.

    Connector world positions are in screen coordinates (the renderer applies
    the camera), so the snap delta that lands a dragged connector exactly on a
    target is simply target - source. We pick the compatible pair whose snap
    delta is closest to the free drag delta and within SNAP_THRESHOLD pixels.
    This is pure spatial candidate computation: a tokenizer job, no behavior.
    """
    sources = [c for c in connectors if _in_subtree(c["path"], dragged_path)]
    targets = [c for c in connectors if not _in_subtree(c["path"], dragged_path)]
    best = None
    best_dist = SNAP_THRESHOLD
    for s in sources:
        for t in targets:
            if not _roles_compatible(s["role"], t["role"]):
                continue
            snap_dx = t["world"][0] - s["world"][0]
            snap_dy = t["world"][1] - s["world"][1]
            dist = math.hypot(free_dx - snap_dx, free_dy - snap_dy)
            if dist < best_dist:
                best_dist = dist
                best = {"sdx": snap_dx, "sdy": snap_dy, "source": s, "target": t}
    return best


def _in_subtree(conn_path, node_path):
    return (conn_path == node_path
            or conn_path.startswith(node_path + ".")
            or conn_path.startswith(node_path + "=")
            or conn_path.startswith(node_path + ":"))


def _roles_compatible(a, b):
    """Connector attachment policy: where role finally earns its keep."""
    if S.ROLE_BIDIRECTIONAL in (a, b):
        return True
    if {a, b} == {S.ROLE_INPUT, S.ROLE_OUTPUT}:
        return True
    if a == S.ROLE_ANCHOR and b == S.ROLE_ANCHOR:
        return True
    return False


def run_organisms(record, derived, out_events):
    """Advance gesture FSMs; append semantic events and immediates."""
    judge = record["judge"]
    gesture = record["gesture"]
    disc = record["state"]
    if derived["pressed"]:
        gesture["consumed"] = False

    _pan(record["organisms"]["pan"], derived, judge, out_events, gesture)
    _drag(record["organisms"]["drag"], derived, judge, out_events, gesture, record, disc)
    _select(record["organisms"]["select"], derived, out_events, gesture)

    # Hover is an idle-only immediate: only when no gesture owns the pointer.
    if not derived["button_down"] and judge.get("pointer") is None and derived["target"]:
        record["immediates"].append({"type": E.HOVER, "path": derived["target"]})


def promote_raw(record):
    """Shift current RAW into previous for next-tick edge detection."""
    record["raw"]["previous"] = dict(record["raw"]["current"])


# --------------------------------------------------------------------------
# organisms
# --------------------------------------------------------------------------

def _pan(o, d, judge, out, gesture):
    if d["pressed"]:
        o["state"] = "ARMED" if d["press_target"] is None else "IDLE"
    if o["state"] == "ARMED" and d["threshold_crossed"] and _commit(judge, "pointer", "pan"):
        o["state"] = "ACTIVE"
    if o["state"] == "ACTIVE":
        if d["released"]:
            _release(judge, "pointer", "pan")
            o["state"] = "IDLE"
            gesture["consumed"] = True
        else:
            out.append({"type": E.PAN_BY, "dx": d["dx"], "dy": d["dy"]})
            gesture["consumed"] = True
    elif d["released"]:
        o["state"] = "IDLE"


def _drag(o, d, judge, out, gesture, record, disc):
    if d["pressed"]:
        o["state"] = "ARMED" if d["press_target"] else "IDLE"
        o["path"] = d["press_target"]
    if o["state"] == "ARMED" and d["threshold_crossed"] and _commit(judge, "pointer", "drag"):
        o["state"] = "ACTIVE"
    if o["state"] == "ACTIVE":
        # When the snap tokenizer found a compatible connector, drive both the
        # preview and the committed move to the snapped delta so the shape locks
        # onto the target connector. Otherwise use the free drag delta.
        snap = d["snap"]
        if snap is not None:
            sdx, sdy = snap["sdx"], snap["sdy"]
        else:
            sdx = d["sx"] - d["press_x"]
            sdy = d["sy"] - d["press_y"]
        # Always hold the live preview, including on the release frame. NODE_MOVED
        # is reduced one tick later; keeping the preview this frame bridges that
        # gap so the shape never flickers back to its origin before the model
        # catches up.
        record["immediates"].append({"type": E.DRAG_PREVIEW, "path": o["path"], "sdx": sdx, "sdy": sdy})
        if snap is not None:
            record["immediates"].append({
                "type": E.SNAP,
                "target_world": snap["target"]["world"],
                "source_name": snap["source"]["name"],
                "target_name": snap["target"]["name"],
                "target_path": snap["target"]["path"],
            })
        gesture["consumed"] = True
        if d["released"]:
            scale = disc["scale"] or 1.0
            out.append({"type": E.NODE_MOVED, "path": o["path"], "dx": sdx / scale, "dy": sdy / scale})
            _release(judge, "pointer", "drag")
            o["state"] = "IDLE"
    elif d["released"]:
        o["state"] = "IDLE"


def _select(o, d, out, gesture):
    if d["pressed"]:
        o["state"] = "ARMED"
    if o["state"] == "ARMED" and d["released"]:
        if not gesture["consumed"]:
            out.append({"type": E.SET_SELECTION, "path": d["target"]})
        o["state"] = "IDLE"


# --------------------------------------------------------------------------
# tokenizer + judge helpers
# --------------------------------------------------------------------------

def _hit_test(canvas, by_item, x, y):
    """Return the editable node path of the topmost domain item near (x, y)."""
    items = canvas.find_overlapping(x - 2, y - 2, x + 2, y + 2)
    for item in reversed(items):
        if item in by_item:
            return world.editable_path(by_item[item])
    return None


def _check(judge, resource, who):
    return judge.get(resource) in (None, who)


def _commit(judge, resource, who):
    if _check(judge, resource, who):
        judge[resource] = who
        return True
    return False


def _release(judge, resource, who):
    if judge.get(resource) == who:
        judge[resource] = None

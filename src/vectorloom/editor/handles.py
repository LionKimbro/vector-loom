"""Resize / rotate handle layout.

Pure geometry: given a selected node's screen bounds and the current handle
mode, produce the handle affordances. Projection draws them; the Continuity
tokenizer hit-tests the pointer against them. Keeping this in one place means
the drawn handle and the hit-tested handle are always the same point.

A resize handle carries its fixed anchor (the opposite corner/edge) and which
axes it scales. A rotate handle carries the pivot (the bounds center).
"""

from . import events as E

HANDLE_RADIUS = 6.0  # pixels; also the hit-test tolerance


def layout(bounds, mode):
    """Return a list of handle dicts for the given screen bounds and mode."""
    if not bounds:
        return []
    minx, miny, maxx, maxy = bounds
    cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0
    if mode == E.MODE_RESIZE:
        return _resize_handles(minx, miny, maxx, maxy, cx, cy)
    if mode == E.MODE_ROTATE:
        return _rotate_handles(minx, miny, maxx, maxy, cx, cy)
    return []


def hit(handles, x, y):
    """Return the handle whose center is within HANDLE_RADIUS of (x, y), or None.
    Iterates in reverse so later-drawn handles win ties."""
    for h in reversed(handles):
        if abs(h["x"] - x) <= HANDLE_RADIUS and abs(h["y"] - y) <= HANDLE_RADIUS:
            return h
    return None


def _resize_handles(minx, miny, maxx, maxy, cx, cy):
    # (role, x, y, anchor_x, anchor_y, scales_x, scales_y)
    specs = [
        ("nw", minx, miny, maxx, maxy, True, True),
        ("ne", maxx, miny, minx, maxy, True, True),
        ("se", maxx, maxy, minx, miny, True, True),
        ("sw", minx, maxy, maxx, miny, True, True),
        ("n", cx, miny, cx, maxy, False, True),
        ("s", cx, maxy, cx, miny, False, True),
        ("e", maxx, cy, minx, cy, True, False),
        ("w", minx, cy, maxx, cy, True, False),
    ]
    return [{"id": f"resize:{role}", "kind": E.HANDLE_RESIZE, "role": role,
             "x": x, "y": y, "ax": ax, "ay": ay, "sx_on": sxo, "sy_on": syo}
            for (role, x, y, ax, ay, sxo, syo) in specs]


def _rotate_handles(minx, miny, maxx, maxy, cx, cy):
    corners = [("nw", minx, miny), ("ne", maxx, miny), ("se", maxx, maxy), ("sw", minx, maxy)]
    return [{"id": f"rotate:{role}", "kind": E.HANDLE_ROTATE, "role": role,
             "x": x, "y": y, "cx": cx, "cy": cy}
            for (role, x, y) in corners]

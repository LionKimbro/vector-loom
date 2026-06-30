"""Render a normalized Vector Loom document onto a tkinter.Canvas.

The runtime walks the canonical tree, composing each node's transform with its
parent's, and flattens every primitive to world-space points. Rectangles and
ovals become polygons of transformed points, so scale and rotation behave with
full consistency rather than relying on Canvas item transforms (which tkinter
does not provide). This is the reusable runtime: it needs no editor.

render_document() draws and returns a result dict:

    {
      "items":      [canvas_item_id, ...],
      "by_item":    {canvas_item_id: node_path},
      "connectors": [{"path", "name", "world", "direction", "role"}, ...],
    }

node_path is a dotted trail of ids (e.g. "root.body.left_port") that the editor
can later use for hit-testing and selection.
"""

import math

from . import geometry as geo
from . import symbols as S


_OVAL_SEGMENTS = 48


def render_document(canvas, doc, base_transform=geo.IDENTITY, overlay=None):
    """Draw a normalized document onto canvas and return a result dict.

    base_transform lets a viewer or editor inject pan/zoom as an outer camera
    transform. The caller owns clearing the canvas.

    overlay is an optional {node_path: transform} map of temporary transform
    intercepts. When the traversal reaches a node whose path is in the overlay,
    the transform is composed (outermost, in screen space) onto the stack for
    that node and its entire subtree. This is how continuous manipulation (a
    live drag) produces a coherent temporary world: the dragged node's geometry,
    connectors, connections, and bounds all resolve through the same stack,
    without mutating the model and without post-render Canvas patching.
    """
    ctx = {"defs": doc["defs"], "items": [], "by_item": {}, "connectors": [],
           "connections": [], "overlay": overlay or {}}
    _draw_node(canvas, doc["root"], base_transform, doc["root"]["id"], ctx)
    _draw_connections(canvas, doc, ctx, base_transform)
    return {
        "items": ctx["items"],
        "by_item": ctx["by_item"],
        "connectors": ctx["connectors"],
        "connections": ctx["connections"],
    }


def _with_overlay(world_m, path, overlay):
    """Compose a temporary overlay transform (outermost/screen space) for a node
    whose path is intercepted. Returns world_m unchanged when there is none."""
    extra = overlay.get(path) if overlay else None
    return geo.compose(extra, world_m) if extra else world_m


def _draw_connections(canvas, doc, ctx, base_transform):
    """Draw wires between connected connectors. Connection items are not
    registered in by_item, so they are decorative relations: not hit-tested,
    not draggable. Endpoints that do not resolve are skipped.

    Each drawn wire is also recorded in ctx["connections"] with its item id, the
    two endpoint node paths, and the endpoint positions, so a live drag can nudge
    the attached endpoint without re-rendering or mutating the model."""
    for conn, a, b in connection_segments(doc, ctx["connectors"]):
        style = conn["style"]
        item = canvas.create_line(
            a[0], a[1], b[0], b[1],
            fill=(style["stroke"] or "#1565c0"),
            width=_stroke_px(style, base_transform),
            dash=_dash(style, base_transform),
        )
        ctx["items"].append(item)
        ctx["connections"].append({
            "id": conn["id"], "item": item,
            "from_node": conn["from"]["node"], "to_node": conn["to"]["node"],
            "a": a, "b": b,
        })


def connection_segments(doc, connectors):
    """Resolve each connection to (connection, point_a, point_b) using the
    supplied connector world positions. Shared by the Canvas renderer and PNG
    exporter so both draw connections identically. Endpoints that do not resolve
    are dropped.
    """
    lookup = {}
    for c in connectors:
        lookup[(_connector_key(c["path"]), c["name"])] = c["world"]
    segments = []
    for conn in doc.get("connections", []):
        a = lookup.get((conn["from"]["node"], conn["from"]["name"]))
        b = lookup.get((conn["to"]["node"], conn["to"]["name"]))
        if a is not None and b is not None:
            segments.append((conn, a, b))
    return segments


def resolve_connectors(doc, base_transform=geo.IDENTITY, overlay=None):
    """Walk the tree and return resolved connector world positions without
    drawing. Lets non-Canvas consumers (the PNG exporter, the snap tokenizer)
    reuse the renderer's connector math. Pass overlay to resolve through the same
    temporary transform intercepts the drawing pass uses."""
    ctx = {"connectors": [], "overlay": overlay or {}}
    _walk_connectors(doc["root"], base_transform, doc["root"]["id"], doc["defs"], ctx)
    return ctx["connectors"]


def _walk_connectors(node, world_m, path, defs, ctx):
    world_m = _with_overlay(world_m, path, ctx["overlay"])
    kind = node["type"]
    if kind == S.GROUP:
        m = geo.compose(world_m, geo.from_trs(**_trs(node)))
        for child in node["children"]:
            _walk_connectors(child, m, f"{path}.{child['id']}", defs, ctx)
        _collect_connectors(node, m, path, ctx)
    elif kind == S.INSTANCE:
        m = geo.compose(world_m, geo.from_trs(**_trs(node)))
        _walk_connectors(defs[node["def"]], m, f"{path}={node['def']}", defs, ctx)
        _collect_connectors(node, m, path, ctx)
    elif kind == S.PORT:
        wx, wy = geo.apply_point(world_m, node["x"], node["y"])
        ctx["connectors"].append({
            "path": path, "name": node["name"], "world": (wx, wy),
            "direction": node["direction"], "role": node["role"],
        })


def _connector_key(render_path):
    """Collapse a connector's render path to its editable node path."""
    return render_path.split("=")[0].split(":")[0]


# --------------------------------------------------------------------------
# tree walk
# --------------------------------------------------------------------------

def _draw_node(canvas, node, world_m, path, ctx):
    world_m = _with_overlay(world_m, path, ctx["overlay"])
    kind = node["type"]
    if kind == S.GROUP:
        local = geo.from_trs(**_trs(node))
        child_m = geo.compose(world_m, local)
        for child in node["children"]:
            _draw_node(canvas, child, child_m, f"{path}.{child['id']}", ctx)
        _collect_connectors(node, child_m, path, ctx)
    elif kind == S.INSTANCE:
        local = geo.from_trs(**_trs(node))
        inst_m = geo.compose(world_m, local)
        target = ctx["defs"][node["def"]]
        # Render the referenced def under the instance transform, but keep the
        # instance's own id in the path so two instances stay distinguishable.
        _draw_node(canvas, target, inst_m, f"{path}={node['def']}", ctx)
        _collect_connectors(node, inst_m, path, ctx)
    elif kind == S.RECT:
        _draw_polygon(canvas, _rect_points(node), node["style"], world_m, path, ctx)
    elif kind == S.OVAL:
        _draw_polygon(canvas, _oval_points(node), node["style"], world_m, path, ctx)
    elif kind == S.LINE:
        pts = [(node["x1"], node["y1"]), (node["x2"], node["y2"])]
        _draw_path(canvas, pts, node["style"], world_m, path, ctx, closed=False)
    elif kind == S.POLYLINE:
        pts = [(p[0], p[1]) for p in node["points"]]
        if node["closed"] and node["style"]["fill"]:
            _draw_polygon(canvas, pts, node["style"], world_m, path, ctx)
        else:
            _draw_path(canvas, pts, node["style"], world_m, path, ctx, closed=node["closed"])
    elif kind == S.PORT:
        _draw_port(canvas, node, world_m, path, ctx)
    elif kind == S.TEXT:
        _draw_text(canvas, node, world_m, path, ctx)


# --------------------------------------------------------------------------
# primitive drawing
# --------------------------------------------------------------------------

def _draw_polygon(canvas, local_points, style, world_m, path, ctx):
    pts = geo.apply_points(world_m, local_points)
    item = canvas.create_polygon(
        _flat(pts),
        fill=(style["fill"] or ""),
        outline=(style["stroke"] or ""),
        width=_stroke_px(style, world_m),
        dash=_dash(style, world_m),
    )
    _record(ctx, item, path)


def _draw_path(canvas, local_points, style, world_m, path, ctx, closed):
    pts = geo.apply_points(world_m, local_points)
    if closed:
        pts = pts + [pts[0]]
    item = canvas.create_line(
        _flat(pts),
        fill=(style["stroke"] or "#222222"),
        width=_stroke_px(style, world_m),
        dash=_dash(style, world_m),
    )
    _record(ctx, item, path)


def _draw_port(canvas, node, world_m, path, ctx):
    # Draw the port marker in its own local space so it scales with placement.
    circle = _ellipse_points(node["x"], node["y"], node["radius"], node["radius"])
    pts = geo.apply_points(world_m, circle)
    style = node["style"]
    fill = style["fill"] or _role_color(node["role"])
    item = canvas.create_polygon(
        _flat(pts),
        fill=fill,
        outline=(style["stroke"] or "#111111"),
        width=max(1.0, _stroke_px(style, world_m)),
    )
    _record(ctx, item, path)
    wx, wy = geo.apply_point(world_m, node["x"], node["y"])
    ctx["connectors"].append({
        "path": path,
        "name": node["name"],
        "world": (wx, wy),
        "direction": node["direction"],
        "role": node["role"],
    })


def _draw_text(canvas, node, world_m, path, ctx):
    wx, wy = geo.apply_point(world_m, node["x"], node["y"])
    size = max(1, int(round(node["size"] * _scale_factor(world_m))))
    item = canvas.create_text(
        wx, wy,
        text=node["text"],
        anchor=node["anchor"],
        fill=(node["style"]["stroke"] or "#222222"),
        font=("TkDefaultFont", size),
    )
    _record(ctx, item, path)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def _trs(node):
    t = node["transform"]
    return {"tx": t["tx"], "ty": t["ty"], "sx": t["sx"], "sy": t["sy"], "rotate_degrees": t["rotate"]}


def _rect_points(node):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def _oval_points(node):
    cx = node["x"] + node["w"] / 2.0
    cy = node["y"] + node["h"] / 2.0
    return _ellipse_points(cx, cy, node["w"] / 2.0, node["h"] / 2.0)


def _ellipse_points(cx, cy, rx, ry):
    pts = []
    for i in range(_OVAL_SEGMENTS):
        a = (2.0 * math.pi * i) / _OVAL_SEGMENTS
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def _collect_connectors(node, world_m, path, ctx):
    for name, c in node.get("connectors", {}).items():
        wx, wy = geo.apply_point(world_m, c["x"], c["y"])
        ctx["connectors"].append({
            "path": f"{path}:{name}",
            "name": name,
            "world": (wx, wy),
            "direction": c["direction"],
            "role": c["role"],
        })


def _scale_factor(m):
    """Approximate uniform scale magnitude of a transform (sqrt of |det|)."""
    a, b, c, d, _e, _f = m
    return math.sqrt(abs(a * d - b * c)) or 1.0


def _stroke_px(style, world_m):
    width = style["width"] if style["width"] is not None else 1.0
    return max(1.0, width * _scale_factor(world_m))


def _dash(style, world_m):
    dash = style.get("dash")
    if not dash:
        return None
    if isinstance(dash, str):
        parts = [int(p) for p in dash.split()]
    else:
        parts = [int(p) for p in dash]
    return tuple(parts) if parts else None


def _role_color(role):
    return {
        S.ROLE_INPUT: "#2e7d32",
        S.ROLE_OUTPUT: "#1565c0",
        S.ROLE_BIDIRECTIONAL: "#6a1b9a",
        S.ROLE_ANCHOR: "#9e9e9e",
    }.get(role, "#9e9e9e")


def document_bounds(doc, base_transform=geo.IDENTITY):
    """Return (min_x, min_y, max_x, max_y) of the document in world space.

    Used by viewers to fit the structure into the window. Returns None when the
    document contains no drawable geometry.
    """
    acc = {"pts": []}
    _bounds_node(doc["root"], base_transform, doc["defs"], acc)
    if not acc["pts"]:
        return None
    xs = [p[0] for p in acc["pts"]]
    ys = [p[1] for p in acc["pts"]]
    return (min(xs), min(ys), max(xs), max(ys))


def path_world_bounds(doc, path, base_transform=geo.IDENTITY, overlay=None):
    """Return the (min_x, min_y, max_x, max_y) screen bounds of the node at an
    editable dotted path (e.g. "root.box" or "root.launch"), or None.

    base_transform is the camera, so the result is in canvas/screen coordinates,
    ready for drawing selection and drag overlays. overlay applies the same
    temporary transform intercepts as the drawing pass, so a selection rectangle
    tracks a node while it is being dragged.
    """
    overlay = overlay or {}
    parts = path.split(".")
    node = doc["root"]
    if not parts or parts[0] != node["id"]:
        return None
    # Accumulate the transform of the node's *parent* frame, applying any overlay
    # intercept as we enter each node. _bounds_node applies the node's own
    # transform internally.
    cur_path = node["id"]
    m = _with_overlay(base_transform, cur_path, overlay)
    for seg in parts[1:]:
        if node["type"] != S.GROUP:
            return None
        m = geo.compose(m, geo.from_trs(**_trs(node)))
        child = _child_by_id(node, seg)
        if child is None:
            return None
        node = child
        cur_path = f"{cur_path}.{seg}"
        m = _with_overlay(m, cur_path, overlay)
    acc = {"pts": []}
    _bounds_node(node, m, doc["defs"], acc)
    if not acc["pts"]:
        return None
    xs = [p[0] for p in acc["pts"]]
    ys = [p[1] for p in acc["pts"]]
    return (min(xs), min(ys), max(xs), max(ys))


def _child_by_id(group, node_id):
    for child in group["children"]:
        if child["id"] == node_id:
            return child
    return None


def _bounds_node(node, world_m, defs, acc):
    kind = node["type"]
    if kind == S.GROUP:
        m = geo.compose(world_m, geo.from_trs(**_trs(node)))
        for child in node["children"]:
            _bounds_node(child, m, defs, acc)
    elif kind == S.INSTANCE:
        m = geo.compose(world_m, geo.from_trs(**_trs(node)))
        _bounds_node(defs[node["def"]], m, defs, acc)
    elif kind == S.RECT:
        acc["pts"].extend(geo.apply_points(world_m, _rect_points(node)))
    elif kind == S.OVAL:
        acc["pts"].extend(geo.apply_points(world_m, _oval_points(node)))
    elif kind == S.LINE:
        acc["pts"].extend(geo.apply_points(world_m, [(node["x1"], node["y1"]), (node["x2"], node["y2"])]))
    elif kind == S.POLYLINE:
        acc["pts"].extend(geo.apply_points(world_m, [(p[0], p[1]) for p in node["points"]]))
    elif kind in (S.PORT, S.TEXT):
        acc["pts"].append(geo.apply_point(world_m, node["x"], node["y"]))


def _flat(points):
    out = []
    for x, y in points:
        out.append(x)
        out.append(y)
    return out


def _record(ctx, item, path):
    ctx["items"].append(item)
    ctx["by_item"][item] = path

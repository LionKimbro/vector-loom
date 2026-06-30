"""Headless PNG export for Vector Loom documents.

Renders a document to a Pillow image without any display or Tk root. This lets
programs and agentic coding systems produce visual artifacts from a structure
file on a server or in a pipeline. It mirrors the Canvas renderer's flattening:
every primitive becomes transformed world-space points, so the PNG matches what
the on-screen runtime draws.

Requires Pillow. Dashed strokes render solid (PIL has no native dash); this is
a known cosmetic limitation of the export path, not the on-screen runtime.

    python -m vectorloom.export_png examples/folder_node.vloom.json out.png
"""

import sys

from PIL import Image, ImageDraw, ImageFont

from . import geometry as geo
from . import model
from . import render
from . import symbols as S


def render_image(doc, size=(900, 560), margin=0.85, background="#fafafa"):
    """Return a Pillow Image of the document, fitted into `size`."""
    width, height = size
    img = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(img)
    base = _fit_transform(doc, width, height, margin)
    _draw_node(draw, doc["root"], base, doc["defs"])
    _draw_connections(draw, doc, base)
    return img


def _draw_connections(draw, doc, base):
    """Draw connection wires, reusing the renderer's shared resolution so the
    PNG matches what the on-screen runtime draws."""
    connectors = render.resolve_connectors(doc, base)
    for conn, a, b in render.connection_segments(doc, connectors):
        style = conn["style"]
        draw.line([a, b], fill=(style["stroke"] or "#1565c0"), width=int(render._stroke_px(style, base)))


def export_file(in_path, out_path, size=(900, 560)):
    """Load a document file and write a PNG to out_path."""
    doc = model.load_file(in_path)
    render_image(doc, size=size).save(out_path)
    return out_path


# --------------------------------------------------------------------------

def _fit_transform(doc, width, height, margin):
    bounds = render.document_bounds(doc)
    if not bounds:
        return geo.translate(width / 2.0, height / 2.0)
    minx, miny, maxx, maxy = bounds
    span_x = max(maxx - minx, 1.0)
    span_y = max(maxy - miny, 1.0)
    scale = min(width * margin / span_x, height * margin / span_y)
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    ox = width / 2.0 - cx * scale
    oy = height / 2.0 - cy * scale
    return geo.compose(geo.translate(ox, oy), geo.scale(scale, scale))


def _draw_node(draw, node, world_m, defs):
    kind = node["type"]
    if kind == S.GROUP:
        m = geo.compose(world_m, geo.from_trs(**render._trs(node)))
        for child in node["children"]:
            _draw_node(draw, child, m, defs)
    elif kind == S.INSTANCE:
        m = geo.compose(world_m, geo.from_trs(**render._trs(node)))
        _draw_node(draw, defs[node["def"]], m, defs)
    elif kind == S.RECT:
        _polygon(draw, render._rect_points(node), node["style"], world_m)
    elif kind == S.OVAL:
        _polygon(draw, render._oval_points(node), node["style"], world_m)
    elif kind == S.LINE:
        _line(draw, [(node["x1"], node["y1"]), (node["x2"], node["y2"])], node["style"], world_m, False)
    elif kind == S.POLYLINE:
        pts = [(p[0], p[1]) for p in node["points"]]
        if node["closed"] and node["style"]["fill"]:
            _polygon(draw, pts, node["style"], world_m)
        else:
            _line(draw, pts, node["style"], world_m, node["closed"])
    elif kind == S.PORT:
        circle = render._ellipse_points(node["x"], node["y"], node["radius"], node["radius"])
        fill = node["style"]["fill"] or render._role_color(node["role"])
        _polygon_fill(draw, circle, fill, node["style"]["stroke"] or "#111111", world_m)
    elif kind == S.TEXT:
        _text(draw, node, world_m)


def _polygon(draw, local_points, style, world_m):
    pts = geo.apply_points(world_m, local_points)
    fill = style["fill"] or None
    outline = style["stroke"] or None
    draw.polygon(pts, fill=fill, outline=outline, width=int(render._stroke_px(style, world_m)))


def _polygon_fill(draw, local_points, fill, outline, world_m):
    pts = geo.apply_points(world_m, local_points)
    draw.polygon(pts, fill=fill, outline=outline)


def _line(draw, local_points, style, world_m, closed):
    pts = geo.apply_points(world_m, local_points)
    if closed:
        pts = pts + [pts[0]]
    draw.line(pts, fill=(style["stroke"] or "#222222"), width=int(render._stroke_px(style, world_m)), joint="curve")


def _text(draw, node, world_m):
    x, y = geo.apply_point(world_m, node["x"], node["y"])
    size = max(8, int(round(node["size"] * render._scale_factor(world_m))))
    font = _load_font(size)
    draw.text((x, y), node["text"], fill=(node["style"]["stroke"] or "#222222"), font=font, anchor=_anchor(node["anchor"]))


def _load_font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _anchor(tk_anchor):
    # Map a few common tk anchors to Pillow's two-letter anchors.
    return {"nw": "la", "n": "ma", "ne": "ra", "w": "lm", "center": "mm", "e": "rm", "sw": "ld", "s": "md", "se": "rd"}.get(tk_anchor, "la")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print("usage: python -m vectorloom.export_png <document.vloom.json> <out.png>")
        return 1
    export_file(argv[0], argv[1])
    print("wrote", argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

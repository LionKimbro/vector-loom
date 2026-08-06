"""Canvas drawing context, designs, and the drawing-time transform stack."""

from copy import deepcopy
import math


g = {
    "canvas": None,
}

styles = {}
designs = {}


def _identity_matrix():
    return (1, 0, 0, 1, 0, 0)


def _matrix_multiply(left, right):
    """Return the affine matrix for applying right, then left."""
    la, lb, lc, ld, le, lf = left
    ra, rb, rc, rd, re, rf = right
    return (
        la * ra + lc * rb,
        lb * ra + ld * rb,
        la * rc + lc * rd,
        lb * rc + ld * rd,
        la * re + lc * rf + le,
        lb * re + ld * rf + lf,
    )


def _translate(x, y):
    return (1, 0, 0, 1, x, y)


def _rotate(angle):
    radians = math.radians(angle)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return (cosine, sine, -sine, cosine, 0, 0)


def _inverse(matrix):
    a, b, c, d, e, f = matrix
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("Transform matrix is not invertible.")
    return (
        d / determinant,
        -b / determinant,
        -c / determinant,
        a / determinant,
        (c * f - d * e) / determinant,
        (b * e - a * f) / determinant,
    )


def _apply_matrix(matrix, x, y):
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def _derive_frame_transform(frame, parent_matrix):
    local_matrix = _matrix_multiply(
        _translate(frame["x"], frame["y"]),
        _rotate(frame["angle"]),
    )
    frame["M"] = _matrix_multiply(parent_matrix, local_matrix)
    frame["Minverse"] = _inverse(frame["M"])


def _identity_frame():
    frame = {"x": 0, "y": 0, "angle": 0}
    _derive_frame_transform(frame, _identity_matrix())
    return frame


S = [_identity_frame()]


def set_canvas(canvas):
    """Point this drawing context at its current Canvas."""
    g["canvas"] = canvas


def push_transform(transform):
    """Push a local transform relative to the current top frame."""
    frame = {
        "x": transform.get("x", 0),
        "y": transform.get("y", 0),
        "angle": transform.get("angle", 0),
    }
    _derive_frame_transform(frame, S[-1]["M"])
    S.append(frame)


def drop_transform():
    """Drop the current nested frame; the root frame cannot be dropped."""
    if len(S) == 1:
        raise RuntimeError("Cannot drop the Transform Stack identity root frame.")
    return S.pop()


def peek_transform():
    """Return a safe copy of the current top frame."""
    return deepcopy(S[-1])


def _rederive_top_frame():
    parent_matrix = _identity_matrix() if len(S) == 1 else S[-2]["M"]
    _derive_frame_transform(S[-1], parent_matrix)


def locate(x, y):
    """Set the top frame's position relative to its parent."""
    S[-1]["x"] = x
    S[-1]["y"] = y
    _rederive_top_frame()


def slide(dx, dy):
    """Move the top frame by a displacement expressed in parent coordinates."""
    S[-1]["x"] += dx
    S[-1]["y"] += dy
    _rederive_top_frame()


def turn(delta):
    """Rotate the top frame clockwise by delta degrees in place."""
    S[-1]["angle"] += delta
    _rederive_top_frame()


def local_to_world(local_x, local_y):
    """Apply the top frame's cached local-to-world transform to one point."""
    return _apply_matrix(S[-1]["M"], local_x, local_y)


def world_to_local(world_x, world_y):
    """Apply the top frame's cached world-to-local transform to one point."""
    return _apply_matrix(S[-1]["Minverse"], world_x, world_y)


def draw(design_name):
    """Draw one named design through the current transform stack frame."""
    design = designs[design_name]
    item_ids = []
    for element in design["contents"]:
        item_ids.extend(_draw_element(element))
    return item_ids


def _draw_element(element):
    if element["type"] == "group":
        push_transform(element)
        try:
            item_ids = []
            for child in element["contents"]:
                item_ids.extend(_draw_element(child))
            return item_ids
        finally:
            drop_transform()
    return [_draw_shape(element)]


def _draw_shape(shape):
    shape_type = shape["type"]
    if shape_type == "line":
        x1, y1 = local_to_world(shape["x1"], shape["y1"])
        x2, y2 = local_to_world(shape["x2"], shape["y2"])
        return g["canvas"].create_line(
            x1, y1, x2, y2,
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "rect":
        return _draw_box_shape(shape, "create_rectangle")
    if shape_type == "oval":
        return _draw_box_shape(shape, "create_oval")
    if shape_type == "polyline":
        points = []
        for x, y in shape["points"]:
            world_x, world_y = local_to_world(x, y)
            points.extend((world_x, world_y))
        return g["canvas"].create_line(
            *points,
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "text":
        return _draw_text(shape)
    raise ValueError(f"Unsupported VectorLoom Basic shape type: {shape_type!r}")


def _has_rotation():
    a, b, c, d, _e, _f = S[-1]["M"]
    return not math.isclose(b, 0, abs_tol=1e-12) or not math.isclose(c, 0, abs_tol=1e-12) or a < 0 or d < 0


def _world_angle():
    """Return the current frame's accumulated clockwise angle in degrees."""
    a, b, _c, _d, _e, _f = S[-1]["M"]
    return math.degrees(math.atan2(b, a))


def _draw_box_shape(shape, canvas_method_name):
    if not _has_rotation():
        x, y = local_to_world(shape["x"], shape["y"])
        canvas_method = getattr(g["canvas"], canvas_method_name)
        return canvas_method(
            x,
            y,
            x + shape["w"],
            y + shape["h"],
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if canvas_method_name == "create_rectangle":
        return _draw_rotated_rect(shape)
    return _draw_rotated_oval(shape)


def _draw_rotated_rect(shape):
    points = []
    for x, y in (
        (shape["x"], shape["y"]),
        (shape["x"] + shape["w"], shape["y"]),
        (shape["x"] + shape["w"], shape["y"] + shape["h"]),
        (shape["x"], shape["y"] + shape["h"]),
    ):
        world_x, world_y = local_to_world(x, y)
        points.extend((world_x, world_y))
    return g["canvas"].create_polygon(
        *points,
        **_polygon_options_for_shape(shape, _style_for(shape)),
    )


def _draw_rotated_oval(shape):
    points = []
    center_x = shape["x"] + shape["w"] / 2
    center_y = shape["y"] + shape["h"] / 2
    radius_x = shape["w"] / 2
    radius_y = shape["h"] / 2
    for index in range(48):
        radians = math.tau * index / 48
        world_x, world_y = local_to_world(
            center_x + radius_x * math.cos(radians),
            center_y + radius_y * math.sin(radians),
        )
        points.extend((world_x, world_y))
    return g["canvas"].create_polygon(
        *points,
        smooth=True,
        **_polygon_options_for_shape(shape, _style_for(shape)),
    )


def _draw_text(shape):
    options = _canvas_options_for_shape(shape, _style_for(shape))
    options["anchor"] = shape.get("anchor", "center")
    options["text"] = shape["text"]
    if "font" in shape:
        options["font"] = _font_spec(shape["font"])
    if "width" in shape:
        options["width"] = shape["width"]
    if "justify" in shape:
        options["justify"] = shape["justify"]
    angle = _world_angle() + shape.get("angle", 0)
    if angle:
        # Tk Canvas uses counterclockwise-positive angles; Vector-Loom uses clockwise-positive.
        options["angle"] = -angle
    x, y = local_to_world(shape["x"], shape["y"])
    return g["canvas"].create_text(x, y, **options)


def _style_for(shape):
    if "style" not in shape:
        return {}
    return styles[shape["style"]]


def _canvas_options_for_shape(shape, style):
    options = {}
    shape_type = shape["type"]
    if shape_type in ("line", "polyline"):
        if "stroke" in style:
            options["fill"] = style["stroke"] or ""
        if "width" in style:
            options["width"] = style["width"]
        if style.get("dash") is not None:
            options["dash"] = style["dash"]
    elif shape_type in ("rect", "oval"):
        if "stroke" in style:
            options["outline"] = style["stroke"] or ""
        if "fill" in style:
            options["fill"] = style["fill"] or ""
        if "width" in style:
            options["width"] = style["width"]
        if style.get("dash") is not None:
            options["dash"] = style["dash"]
    elif shape_type == "text" and "fill" in style:
        options["fill"] = style["fill"] or ""
    return options


def _polygon_options_for_shape(shape, style):
    options = {}
    if "stroke" in style:
        options["outline"] = style["stroke"] or ""
    if "fill" in style:
        options["fill"] = style["fill"] or ""
    if "width" in style:
        options["width"] = style["width"]
    if style.get("dash") is not None:
        options["dash"] = style["dash"]
    return options


def _font_spec(font):
    if isinstance(font, list):
        return tuple(font)
    return font

"""Canvas drawing context, designs, and the drawing-time transform stack."""

import math

from . import transform_stack


# Temporary compatibility names for callers of the proving-ground module.  The
# Transform Stack owns these operations; Canvas Context only uses them.
S = transform_stack.S
_identity_frame = transform_stack.identity_frame
_apply_matrix = transform_stack.apply_matrix
push_transform = transform_stack.push_transform
drop_transform = transform_stack.drop_transform
peek_transform = transform_stack.peek_transform
locate = transform_stack.locate
slide = transform_stack.slide
turn = transform_stack.turn
local_to_world = transform_stack.local_to_world
world_to_local = transform_stack.world_to_local


g = {
    "canvas": None,
}

reg = {
    "design-name": None,
    "instance-id": None,
    "connector": None,
}

styles = {}
designs = {}
connectors = {}


def set_canvas(canvas):
    """Point this drawing context at its current Canvas."""
    g["canvas"] = canvas


def clear_connectors():
    """Clear the connector records produced by earlier drawing."""
    connectors.clear()
    reg["connector"] = None


def select_connector(instance_id, connector_id):
    """Select and return one connector record by its instance and connector IDs."""
    record = connectors[(instance_id, connector_id)]
    reg["connector"] = record
    return record


def draw(design_name, instance_id=None, flags=None):
    """Draw one named design through the current transform stack frame."""
    if flags is None:
        flags = []
    reg["design-name"] = design_name
    reg["instance-id"] = instance_id
    design = designs[design_name]
    attached = "attach" in flags
    if attached:
        if reg["connector"] is None:
            raise RuntimeError("Cannot attach a design without a selected connector.")
        transform_stack.push_transform(reg["connector"])
    item_ids = []
    try:
        for element in design["contents"]:
            item_ids.extend(_draw_element(element, flags))
    finally:
        if attached:
            transform_stack.drop_transform()
    return item_ids


def _draw_element(element, flags):
    if element["type"] == "group":
        transform_stack.push_transform(element)
        try:
            item_ids = []
            for child in element["contents"]:
                item_ids.extend(_draw_element(child, flags))
            return item_ids
        finally:
            transform_stack.drop_transform()
    if element["type"] == "connector":
        if "dry-run" in flags:
            _require_instance_id_for_connector()
        else:
            _record_connector(element)
        return []
    if "dry-run" in flags:
        return []
    return [_draw_shape(element)]


def _require_instance_id_for_connector():
    if reg["instance-id"] is None:
        raise RuntimeError("A connector-producing draw requires instance_id.")


def _record_connector(connector):
    _require_instance_id_for_connector()
    transform_stack.push_transform(connector)
    try:
        frame = transform_stack.peek_transform()
        x, y, angle = _world_pose_from_matrix(frame["M"])
        record = {
            "instance-id": reg["instance-id"],
            "connector-id": connector["id"],
            "connector-role": connector["role"],
            "connector-tags": list(connector.get("tags", [])),
            "x": x,
            "y": y,
            "angle": angle,
            "M": frame["M"],
            "Minverse": frame["Minverse"],
        }
        connectors[(record["instance-id"], record["connector-id"])] = record
    finally:
        transform_stack.drop_transform()


def _world_pose_from_matrix(matrix):
    a, b, _c, _d, x, y = matrix
    return x, y, math.degrees(math.atan2(b, a))


def _draw_shape(shape):
    shape_type = shape["type"]
    tags = _canvas_tags_for_shape(shape)
    if shape_type == "line":
        x1, y1 = transform_stack.local_to_world(shape["x1"], shape["y1"])
        x2, y2 = transform_stack.local_to_world(shape["x2"], shape["y2"])
        return g["canvas"].create_line(
            x1, y1, x2, y2,
            tags=tags,
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "rect":
        return _draw_box_shape(shape, "create_rectangle")
    if shape_type == "oval":
        return _draw_box_shape(shape, "create_oval")
    if shape_type == "polyline":
        points = []
        for x, y in shape["points"]:
            world_x, world_y = transform_stack.local_to_world(x, y)
            points.extend((world_x, world_y))
        return g["canvas"].create_line(
            *points,
            tags=tags,
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "text":
        return _draw_text(shape)
    raise ValueError(f"Unsupported VectorLoom Basic shape type: {shape_type!r}")


def _has_rotation():
    a, b, c, d, _e, _f = transform_stack.peek_transform()["M"]
    return not math.isclose(b, 0, abs_tol=1e-12) or not math.isclose(c, 0, abs_tol=1e-12) or a < 0 or d < 0


def _world_angle():
    """Return the current frame's accumulated clockwise angle in degrees."""
    a, b, _c, _d, _e, _f = transform_stack.peek_transform()["M"]
    return math.degrees(math.atan2(b, a))


def _draw_box_shape(shape, canvas_method_name):
    if not _has_rotation():
        x, y = transform_stack.local_to_world(shape["x"], shape["y"])
        canvas_method = getattr(g["canvas"], canvas_method_name)
        return canvas_method(
            x,
            y,
            x + shape["w"],
            y + shape["h"],
            tags=_canvas_tags_for_shape(shape),
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
        world_x, world_y = transform_stack.local_to_world(x, y)
        points.extend((world_x, world_y))
    return g["canvas"].create_polygon(
        *points,
        tags=_canvas_tags_for_shape(shape),
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
        world_x, world_y = transform_stack.local_to_world(
            center_x + radius_x * math.cos(radians),
            center_y + radius_y * math.sin(radians),
        )
        points.extend((world_x, world_y))
    return g["canvas"].create_polygon(
        *points,
        smooth=True,
        tags=_canvas_tags_for_shape(shape),
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
    x, y = transform_stack.local_to_world(shape["x"], shape["y"])
    options["tags"] = _canvas_tags_for_shape(shape)
    return g["canvas"].create_text(x, y, **options)


def _canvas_tags_for_shape(shape):
    """Return the Canvas identification tags for one rendered primitive."""
    tags = ["design:" + reg["design-name"]]
    if "id" in shape:
        tags.append("shape:" + shape["id"])
    for declared_tag in shape.get("tags", []):
        tags.append("tag:" + declared_tag)
    if reg["instance-id"] is not None:
        tags.append("instance:" + reg["instance-id"])
    return tuple(tags)


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

"""The current Canvas, VectorLoom Basic library, and drawing location."""


g = {
    "canvas": None,
}

reg = {
    "x": 0,
    "y": 0,
}

styles = {}
definitions = {}


def set_canvas(canvas):
    """Point this drawing context at its current Canvas."""
    g["canvas"] = canvas


def locate(x, y):
    """Set the current origin for nearby drawing operations."""
    reg["x"] = x
    reg["y"] = y


def draw(drawing_name):
    """Draw one named definition relative to the current location."""
    definition = definitions[drawing_name]
    return [_draw_shape(shape) for shape in definition["contents"]]


def _draw_shape(shape):
    shape_type = shape["type"]
    if shape_type == "line":
        return g["canvas"].create_line(
            reg["x"] + shape["x1"],
            reg["y"] + shape["y1"],
            reg["x"] + shape["x2"],
            reg["y"] + shape["y2"],
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "rect":
        return _draw_box_shape(shape, "create_rectangle")
    if shape_type == "oval":
        return _draw_box_shape(shape, "create_oval")
    if shape_type == "polyline":
        points = []
        for x, y in shape["points"]:
            points.extend((reg["x"] + x, reg["y"] + y))
        return g["canvas"].create_line(
            *points,
            **_canvas_options_for_shape(shape, _style_for(shape)),
        )
    if shape_type == "text":
        return _draw_text(shape)
    raise ValueError(f"Unsupported VectorLoom Basic shape type: {shape_type!r}")


def _draw_box_shape(shape, canvas_method_name):
    x = reg["x"] + shape["x"]
    y = reg["y"] + shape["y"]
    canvas_method = getattr(g["canvas"], canvas_method_name)
    return canvas_method(
        x,
        y,
        x + shape["w"],
        y + shape["h"],
        **_canvas_options_for_shape(shape, _style_for(shape)),
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
    if "angle" in shape:
        options["angle"] = shape["angle"]
    return g["canvas"].create_text(
        reg["x"] + shape["x"],
        reg["y"] + shape["y"],
        **options,
    )


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


def _font_spec(font):
    if isinstance(font, list):
        return tuple(font)
    return font

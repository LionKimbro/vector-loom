# Module — Canvas Context

## Render Target

`canvas_context.py`

## OWNS

- The current Canvas at `g["canvas"]`, after a caller points this context at
  that Canvas.
- The named style open collection, `styles`.
- The named design open collection, `designs`.
- The current drawing location at `reg["x"]`, `reg["y"]`.
- Establishing that current location with `locate(x, y)`.
- Drawing one named VectorLoom Basic design relative to the current
  location with `draw(drawing_name)`.
- Translating each shape's design-local coordinates by the current
  register location.
- Resolving a shape's named `style` reference against `styles`.

## READS

- The VectorLoom Basic shape and style rules in
  `docs/raw/0015__vectorloom-basic.json`.

## CALLS

- The current Canvas's `create_line()`, `create_rectangle()`, `create_oval()`,
  and `create_text()` operations, as selected by the shape type.

## MAY SAFELY ASSUME

- A caller has first set a real `tkinter.Canvas` with `set_canvas(canvas)`.
- `locate(x, y)` establishes the current drawing location for a nearby,
  synchronous drawing flow.
- The named design exists in `designs`.
- Shapes and their named style references conform to VectorLoom Basic.

## ENSURES

- `locate(x, y)` changes the current origin used by later `draw()` calls.
- `draw("design-name")` creates the design's shapes on the current
  Canvas in `contents` order, relative to that current origin.
- Neither `locate()` nor `draw()` mutates a design.
- Later shapes in a design are drawn after earlier shapes and therefore
  appear above them on the Canvas.

## DOES NOT OWN

- Creating, placing, sizing, titling, or destroying the Canvas Host Window.
- Loading, saving, validating, or otherwise managing the VectorLoom Basic
  document.
- Deciding how styles and designs are populated; a later library-loading
  mechanism may populate these open collections.
- Choosing which drawing to place in a larger scene.
- Canvas interaction, input handling, or future editor behavior.
- Preserving a drawing location across delayed callbacks, threads, recursion, or
  uncontrolled re-entry; such work must establish its location again.

## Sketch

```python
g = {
    "canvas": None
}

reg = {  # registers
    "x": 0,
    "y": 0
}

styles = {}    # named VectorLoom Basic styles
designs = {}   # named VectorLoom Basic designs


def set_canvas(canvas):
    g["canvas"] = canvas

def locate(x, y):
    reg["x"] = x
    reg["y"] = y

def draw(design_name):
    Find design_name in designs.
    For each shape in its contents, in order:
        Look up the shape's named style in styles, if it has one.
        Draw the shape on g["canvas"], offsetting every local coordinate by
        reg["x"], reg["y"].
    Return the Canvas item ids, in contents order.

def _draw_shape(shape):
    line:     Canvas create_line with reg["x"], reg["y"] added to
              x1, y1, x2, y2.
    rect:     Canvas create_rectangle with reg["x"], reg["y"] added to
              x, y and then w, h applied.
    oval:     Canvas create_oval with reg["x"], reg["y"] added to
              x, y and then w, h applied.
    polyline: Canvas create_line with reg["x"], reg["y"] added to every
              point.
    text:     Canvas create_text with reg["x"], reg["y"] added to x, y,
              plus text layout fields.

def _canvas_options_for_shape(shape, style):
    Map VectorLoom Basic style fields to the selected Canvas primitive.
    A text shape uses the style's fill color as its Canvas text fill color.
```

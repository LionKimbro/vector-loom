# Module — Canvas Context

This module is the emerging core of a general Vector Loom Canvas
package. It holds the active Canvas and the current drawing context,
providing the place where Vector Loom drawings can be placed and
rendered as the system grows.


## Render Target

`canvas_context.py`

## See Also

- `../aspects/canvas-item-identification.md` — Canvas tags that preserve a
  rendered primitive's design, shape, semantic, and placement identity.

## OWNS

- The current Canvas at `g["canvas"]`, after a caller points this context at
  that Canvas.
- The named style open collection, `styles`.
- The named design open collection, `designs`.
- Traversing one named VectorLoom Basic design with `draw(design_name)`.
- Traversing nested group contents and maintaining their drawing order.
- Resolving each element-local coordinate through Transform Stack before
  passing it to the Canvas.
- Resolving a shape's named `style` reference against `styles`.

## READS

- The VectorLoom Basic shape and style rules in
  `docs/raw/0015__vectorloom-basic.json`.
- The Transform Stack contract in `pseudo-src/vectorloom/modules/transform-stack.md`.
  Both this module and Transform Stack write into `canvas_context.py`.

## CALLS

- The current Canvas's `create_line()`, `create_rectangle()`, `create_oval()`,
  and `create_text()` operations, as selected by the shape type.
- Transform Stack's `push_transform()`, `drop_transform()`, and
  `local_to_world()` operations.

## MAY SAFELY ASSUME

- A caller has first set a real `tkinter.Canvas` with `set_canvas(canvas)`.
- The named design exists in `designs`.
- Shapes and their named style references conform to VectorLoom Basic.
- Transform Stack has a valid current frame.

## ENSURES

- `draw("design-name")` creates the design's shapes on the current
  Canvas in `contents` order, resolving all element-local coordinates with
  `local_to_world()`.
- `draw()` pushes each group transform before traversing its contents and
  drops it afterward, even if drawing fails.
- `draw()` does not mutate a design and leaves Transform Stack at its incoming
  depth when it returns.
- Later shapes in a design are drawn after earlier shapes and therefore
  appear above them on the Canvas.

## DOES NOT OWN

- Creating, placing, sizing, titling, or destroying the Canvas Host Window.
- The transform stack, transform composition, or point conversion. Those are
  owned by Transform Stack even though both modules render into
  `canvas_context.py`.
- Loading, saving, validating, or otherwise managing the VectorLoom Basic
  document.
- Deciding how styles and designs are populated; a later library-loading
  mechanism may populate these open collections.
- Choosing which drawing to place in a larger scene.
- Canvas interaction, input handling, or future editor behavior.
- Preserving an externally chosen transform across delayed callbacks, threads,
  recursion, or uncontrolled re-entry.

## Sketch

```python
g = {
    "canvas": None
}

styles = {}    # named VectorLoom Basic styles
designs = {}   # named VectorLoom Basic designs


def set_canvas(canvas):
    g["canvas"] = canvas

def draw(design_name):
    Find design_name in designs.
    For each element in its contents, in order:
        _draw_element(element)
    Return the Canvas item ids, in contents order.


def _draw_element(element):
    If element.type is "group":
        transform_stack.push_transform(element)
        try:
            For each child in element.contents, in order:
                _draw_element(child)
        finally:
            transform_stack.drop_transform()
    Otherwise:
        _draw_shape(element)


def _draw_shape(shape):
    Resolve every shape coordinate with transform_stack.local_to_world().
    line:     Canvas create_line with both endpoints resolved to world.
    rect:     Canvas rendering policy receives its transformed geometry.
    oval:     Canvas rendering policy receives its transformed geometry.
    polyline: Canvas create_line with every point resolved to world.
    text:     Canvas create_text with its anchor point resolved to world,
              plus text layout fields and accumulated rotation.

def _canvas_options_for_shape(shape, style):
    Map VectorLoom Basic style fields to the selected Canvas primitive.
    A text shape uses the style's fill color as its Canvas text fill color.
```

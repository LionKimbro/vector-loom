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
- `../../../docs/raw/0015__vectorloom-basic.json` — the VectorLoom Basic shape,
  style, design, and group conventions.
- `../../../docs/raw/0017__connector-points.md` — connector-point roles, tags,
  and local-coordinate-frame semantics.
- `transform-stack.md` — Transform Stack's operations and coordinate-frame
  contract.


## OWNS

- The active Canvas at `g["canvas"]`.
- The named style and design open collections, `styles` and `designs`.
- The render-produced connector-record collection, `connectors`, and the
  currently selected connector at `reg["connector"]`.
- Drawing one named VectorLoom Basic design with
  `draw(design_name, instance_id=None, flags=None)`[^draw-flags], including nested-group
  traversal, transform resolution, and drawing order.
- Resolving named shape styles and constructing the Canvas tags for rendered
  primitives.
- Deriving and recording each connector's effective world coordinate frame;
  connectors do not produce Canvas items.
- Clearing and selecting connector records.


## CALLS

- The current Canvas's `create_line()`, `create_rectangle()`, `create_oval()`,
  and `create_text()` operations, as selected by the shape type.
- Transform Stack's transform functions, and `local_to_world()` operations.


## MAY SAFELY ASSUME

- A caller has first set a real `tkinter.Canvas` with `set_canvas(canvas)`.
- The named design exists in `designs`.
- Shapes and their named style references conform to VectorLoom Basic.
- Connector points conform to VectorLoom Basic, including their required ID,
  x, y, and role.
- Transform Stack has a valid current frame.


## ENSURES

- `draw("design-name", instance_id=None, flags=None)` creates the design's shapes on the current
  Canvas in `contents` order, resolving all element-local coordinates with
  `local_to_world()`.
- Every rendered primitive receives `design:<design-name>`, plus its optional
  `shape:`, declared `tag:`, and caller-supplied `instance:` Canvas tags.
- When `draw()` encounters a connector, it appends or updates the record at
  `connectors[(instance_id, connector_id)]`. Its `x`, `y`, `angle`, `M`, and
  `Minverse` use the exact Transform Stack frame keys and meanings: `M`
  converts connector-local coordinates to world/Canvas coordinates, and
  `Minverse` converts world/Canvas coordinates to connector-local coordinates.
  Its `x`, `y`, and `angle` are the effective world decomposition derived from
  `M`, rather than the connector's parent-relative source fields.
- A normal `draw()` that reaches a connector without an `instance_id` raises
  an error at that point. Shapes already drawn remain drawn.
- `draw(..., flags=["dry-run"])` performs a no-side-effect preflight traversal.
  It finds missing selection or instance errors before any Canvas item or
  connector record is created, but does not itself draw or record anything.
  It uses the ordinary recursive element traversal, carrying the flag only
  through recursive element dispatch rather than maintaining a separate
  traversal.
- `draw(..., flags=["attach"])` starts the design's local coordinate system at
  the currently selected connector's `M`: its local origin and angle continue
  from that connector. It raises an error if no connector is selected.
- `select_connector(instance_id, connector_id)` places that record in
  `reg["connector"]` and returns it.
- `clear_connectors()` clears `connectors` and clears `reg["connector"]`.
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
- A retained scene, durable instances, or later mutation behavior. The
  connector registry is an immediate-mode by-product of rendering.
- Preserving an externally chosen transform across delayed callbacks, threads,
  recursion, or uncontrolled re-entry.


## Sketch

```python
g = {
    "canvas": None
}

reg = {
    "design-name": None,
    "instance-id": None,
    "connector": None
}

styles = {}    # named VectorLoom Basic styles
designs = {}   # named VectorLoom Basic designs
connectors = {} # (instance-id, connector-id) -> most recently rendered record


def set_canvas(canvas):
    g["canvas"] = canvas

def clear_connectors():
    connectors.clear()
    reg["connector"] = None


def select_connector(instance_id, connector_id):
    record = connectors[(instance_id, connector_id)]
    reg["connector"] = record
    return record


def draw(design_name, instance_id=None, flags=None):
    reg["design-name"] = design_name
    reg["instance-id"] = instance_id
    Find the named design (in designs).
    
    If "attach" in flags:
        Require a connector is selected (in registers).
	Push the selected connector's transform, onto the transform_stack.
    
    try:
        For each element in its contents, in order:
            _draw_element(element, flags)
    finally:
        If "attach" in flags:
	    Restore the transform stack.
    
    Return the Canvas item ids, in contents order.


def _draw_element(element, flags):
    If element.type is "group":
        transform_stack.push_transform(element)
        try:
            For each child in element.contents, in order:
                _draw_element(child, flags)
        finally:
            transform_stack.drop_transform()
    Else if element.type is "connector":
        If "dry-run" is in flags:
            _require_instance_id_for_connector()
        Otherwise:
            _record_connector(element)
    Otherwise:
        If "dry-run" is not in flags:
            _draw_shape(element)


def _require_instance_id_for_connector():
    If reg["instance-id"] is None:
        raise an error that a connector-producing draw requires instance_id.


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


def _world_pose_from_matrix(M):
    # For M = (a, b, c, d, e, f), use e/f for the transformed local origin
    # and derive the effective clockwise angle from a/b.
    Return x, y, angle derived from M.


def _draw_shape(shape):
    Resolve every shape coordinate with transform_stack.local_to_world().
    tags = _canvas_tags_for_shape(shape)
    line:     Canvas create_line with both endpoints resolved to world,
              tags=tags.
    rect:     Canvas rendering policy receives its transformed geometry,
              tags=tags.
    oval:     Canvas rendering policy receives its transformed geometry,
              tags=tags.
    polyline: Canvas create_line with every point resolved to world,
              tags=tags.
    text:     Canvas create_text with its anchor point resolved to world,
              plus text layout fields, accumulated rotation, and tags=tags.

def _canvas_tags_for_shape(shape):
    tags = ["design:" + reg["design-name"]]
    if shape has an id:
        tags.append("shape:" + shape["id"])
    for declared_tag in shape.get("tags", []):
        tags.append("tag:" + declared_tag)
    if reg["instance-id"] is not None:
        tags.append("instance:" + reg["instance-id"])
    return tags

def _canvas_options_for_shape(shape, style):
    Map VectorLoom Basic style fields to the selected Canvas primitive.
    A text shape uses the style's fill color as its Canvas text fill color.
```

[^draw-flags]: Valid flags are `attach`, which begins drawing from the selected
connector's coordinate frame, and `dry-run`, which performs the same recursive
validation traversal without creating Canvas items or connector records.

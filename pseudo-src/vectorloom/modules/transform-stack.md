# Module — Transform Stack

This module manages the transforms used while drawing a design. It
converts between local coordinates and world coordinates as nested
drawing structures are traversed.


## Render Target

`canvas_context.py`

## OWNS

- The drawing-time transform stack, `S`.
- A non-droppable identity root frame at the bottom of `S`.
- Each frame’s local, parent-relative `x`, `y`, and `angle` values.
- Each frame’s derived local-to-world affine transform, `M`, and cached inverse,
  `Minverse`.
- Pushing and dropping nested local transforms.
- Mutating the top frame’s local position and angle.
- Converting points between the current local coordinate system and world
  coordinates.

## READS

- The VectorLoom transform and clockwise-angle conventions in
  `docs/raw/0015__vectorloom-basic.json`.

## MAY SAFELY ASSUME

- The root frame has no parent and represents world coordinates.
- Every non-root frame is positioned and oriented relative to the frame beneath
  it.
- Angles are degrees; positive angles are clockwise in screen coordinates.
- Scaling is not part of VectorLoom Basic yet, so every transform represented
  here is invertible.

## ENSURES

- `S` always contains at least the identity root frame.
- The top frame always has the form
  `{"x": x, "y": y, "angle": angle, "M": M, "Minverse": Minverse}`.
- `M` maps points in the top frame’s local coordinate system to world
  coordinates.
- `Minverse` maps world coordinates back to the top frame’s local coordinate
  system.
- A caller cannot mutate the returned result of `peek_transform()` in a way
  that leaves `M` or `Minverse` stale.

## DOES NOT OWN

- Canvas creation or Canvas drawing operations.
- Traversing a design or group’s contents.
- Shape geometry or rendering policy.
- Bounds queries yet; a later extension may use this stack as the home for
  transform-aware bounds operations.

## Transform Semantics

Each frame stores local values relative to its parent:

```python
{"x": 0, "y": 0, "angle": 0}
```

Its derived transform is composed from the frame below it:

```text
frame.M = parent.M × Translate(frame.x, frame.y) × Rotate(frame.angle)
```

For clockwise degrees in screen coordinates, applying a frame with origin
`(x, y)` and angle `a` to local point `(lx, ly)` has this effect:

```text
world_x = x + cos(a) × lx - sin(a) × ly
world_y = y + sin(a) × lx + cos(a) × ly
```

For nested frames, the parent’s accumulated `M` is applied as part of the
composition above. `Minverse` is derived whenever `M` is derived; it is never
independently edited.

## Sketch

```python
S = [identity_frame()]


def identity_frame():
    frame = {"x": 0, "y": 0, "angle": 0}
    derive_frame_transform(frame, parent_M=identity_matrix())
    return frame


def push_transform(transform):
    """Push a local transform relative to the current top frame."""
    frame = {
        "x": transform.get("x", 0),
        "y": transform.get("y", 0),
        "angle": transform.get("angle", 0),
    }
    derive_frame_transform(frame, parent_M=S[-1]["M"])
    S.append(frame)


def drop_transform():
    """Drop the current nested frame; the identity root cannot be dropped."""
    Require len(S) > 1.
    return S.pop()


def peek_transform():
    """Return a copy or read-only view of the current top frame."""
    Return a safe view of S[-1].


def locate(x, y):
    """Set the top frame's position relative to its parent."""
    S[-1]["x"] = x
    S[-1]["y"] = y
    rederive_top_frame()


def slide(dx, dy):
    """Move the top frame by a displacement expressed in parent coordinates."""
    S[-1]["x"] += dx
    S[-1]["y"] += dy
    rederive_top_frame()


def turn(delta):
    """Rotate the top frame clockwise by delta degrees in place."""
    S[-1]["angle"] += delta
    rederive_top_frame()


def local_to_world(local_x, local_y):
    """Apply the top frame's cached M to one local point."""
    Return apply_matrix(S[-1]["M"], local_x, local_y).


def world_to_local(world_x, world_y):
    """Apply the top frame's cached Minverse to one world point."""
    Return apply_matrix(S[-1]["Minverse"], world_x, world_y).


def rederive_top_frame():
    parent_M = identity_matrix() if len(S) == 1 else S[-2]["M"]
    derive_frame_transform(S[-1], parent_M)


def derive_frame_transform(frame, parent_M):
    local_M = translate(frame["x"], frame["y"]) × rotate(frame["angle"])
    frame["M"] = parent_M × local_M
    frame["Minverse"] = inverse(frame["M"])
```

## Use During Group Drawing

Canvas Context pushes a group’s `{x, y, angle}` before traversing the group’s
contents and drops it in a `finally` block afterward. It uses
`local_to_world()` for each shape point. This makes nested group transforms
temporary, composable, and unable to leak into later sibling elements.

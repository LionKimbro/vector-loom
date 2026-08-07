# Module — Transform Stack

This module manages the transforms used while drawing a design. It
converts between local coordinates and world coordinates as nested
drawing structures are traversed.


## Render Target

`canvas_context.py`

## See Also

- `../data-structures/transform-stack.md` — the Transform Stack's shape,
  semantic types, mutation authority, invariants, and lifetime.
- The VectorLoom transform and clockwise-angle conventions in
  `docs/raw/0015__vectorloom-basic.json`.


## OWNS

- The operations that maintain and use the Transform Stack structure.
- Pushing and dropping nested local transforms.
- Locating, sliding, and turning the current top frame.
- Converting points between the current local coordinate system and world
  coordinates.

## READS

## MAY SAFELY ASSUME

- The Transform Stack has been initialized according to its data-structure
  contract.
- Scaling is not part of VectorLoom Basic yet, so every transform handled here
  is invertible.

## ENSURES

- Each public operation preserves the Transform Stack structure's invariants.
- `local_to_world()` and `world_to_local()` use the current top frame.
- `peek_transform()` returns a safe view of the current top frame.

## DOES NOT OWN

- Canvas creation or Canvas drawing operations.
- Traversing a design or group’s contents.
- Shape geometry or rendering policy.
- Bounds queries yet; a later extension may use this stack as the home for
  transform-aware bounds operations.

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

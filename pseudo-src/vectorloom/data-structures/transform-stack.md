# Data Structure — Transform Stack

The Transform Stack tracks recursively nested coordinate frames while
a design is drawn. Each frame preserves a coordinate scheme relative
to the frame beneath it, while the top frame is the current place
where drawing work occurs.


## Owned By

`modules/canvas/transform-stack.md`

Only Transform Stack operations mutate this structure. Callers ask that module
to push, drop, locate, slide, or turn; they do not edit stack frames directly.


## Shape

```text
S = [root-frame, ..., top/current-frame]

frame = {
    "x": number (int or float),
    "y": number (int or float),
    "angle": number (int or float),
    "M": affine-transform,
    "Minverse": affine-transform
}
```

`S` is an ordered stack. The last entry is the current frame.

| Field | Logical type | Meaning |
| --- | --- | --- |
| `x`, `y` | document coordinate | This frame's local origin relative to its parent frame. |
| `angle` | clockwise degrees | This frame's local rotation relative to its parent frame. |
| `M` | local-to-world affine transform | Converts a point in this frame's local coordinates into world coordinates. |
| `Minverse` | world-to-local affine transform | Converts a world point into this frame's local coordinates. |

The concrete Python representation of an `affine-transform` is an
implementation detail of Transform Stack. Its semantic direction is part of
this structure's contract.

For the initial implementation, an affine transform uses the compact tuple:

```text
(a, b, c, d, e, f)
```

It represents this homogeneous 3×3 matrix:

```text
[a  c  e]
[b  d  f]
[0  0  1]
```


## Root Frame

The first frame is the non-droppable identity root frame:

```text
root-frame = {
    "x": 0,
    "y": 0,
    "angle": 0,
    "M": identity-transform,
    "Minverse": identity-transform
}
```

It represents world coordinates and has no parent frame.

## Transform Semantics

Each non-root frame stores local values relative to the frame immediately
beneath it. Its derived transform is composed as:

```text
frame.M = parent.M × Translate(frame.x, frame.y) × Rotate(frame.angle)
```

For clockwise degrees in screen coordinates, applying a frame with origin
`(x, y)` and angle `a` to local point `(lx, ly)` has this effect:

```text
world_x = x + cos(a) × lx - sin(a) × ly
world_y = y + sin(a) × lx + cos(a) × ly
```

For nested frames, the parent’s accumulated `M` participates in the
composition above. `Minverse` is derived whenever `M` is derived; it is never
edited independently.


## Invariants

- `S` always contains the identity root frame; its length is never zero.
- Every non-root frame is parent-relative to the frame immediately below it.
- Positive `angle` values are clockwise in screen coordinates.
- A frame's `M` equals its parent `M`, followed by the frame's translation and
  rotation.
- A frame's `Minverse` is derived from that frame's `M`; it is never edited as
  an independent value.
- `peek_transform()` exposes a safe copy or read-only view, so callers cannot
  leave `M` or `Minverse` stale.


## Mutation and Lifetime

- Program initialization creates `S` with exactly the root frame.
- `push_transform()` adds one nested frame for a local drawing context.
- `locate()`, `slide()`, and `turn()` mutate only the current top frame and
  immediately rederive its `M` and `Minverse`.
- `drop_transform()` removes only a non-root top frame.
- A drawing traversal pushes before entering a group and drops in a `finally`
  block when leaving it, so a group's coordinate system cannot leak to a
  sibling drawing.

## Used By

- Canvas Context uses the top frame when converting a shape's local points for
  Canvas drawing.
- Future bounds, hit-testing, and editor operations may use the same stack for
  transform-aware coordinate conversion.

# ADR 0002: Apply local rotation before parent-relative translation

- Date: 2026-08-06
- Status: Accepted

## Context

Nested elements and design instances need a predictable transform convention. In particular, an element's position should describe its local origin in its parent, rather than a vector that rotates around the parent's origin.

## Decision

Each nested element or design instance has a local transform relative to its parent. For a local point, apply transforms in this order:

1. Rotate around the element’s local origin.
2. Translate by the element’s `x` and `y` position in the parent coordinate system.

With column vectors:

```text
parent_point = Translate(x, y) × Rotate(angle) × local_point
```

## Consequences

- `(x, y)` places the element’s local origin in the parent coordinate system.
- Changing `angle` changes local orientation, but does not rotate the `(x, y)` translation vector around the parent origin.
- Renderers, hit testing, bounds calculations, and serialization must use this same composition order.

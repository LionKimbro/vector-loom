```text
date: 2026-08-07
title: Connector Points: Roles, Tags, and Semantics
purpose: specify how connector points will work
```

# Connector Points: Roles, Tags, and Semantics

Vector-Loom should support named, non-rendering coordinate points inside a design. These points participate in the same local coordinate and transform hierarchy as visible primitives and groups, so their position and orientation are automatically transformed along with the rest of the design. A connector point should minimally support `id`, `x`, `y`, `angle`, `role`, and `tags`.

A connector point is better understood as a small **local coordinate frame** rather than merely an `(x, y)` location. Its `x` and `y` identify the point relative to its parent coordinate system, and its `angle` identifies its local orientation. This allows another design instance to be aligned to it spatially, or allows a logical connection endpoint to have a meaningful orientation in the drawing.

The field `role` is singular and describes **what kind of relationship this point is intended to participate in**. The role vocabulary should remain open-ended, but Vector-Loom currently suggests two standard roles:

* `attachment` — a point intended for spatial attachment of another design instance.
* `port` — a point intended for creation or removal of a logical or routed connection to another port.

The distinction between these roles is semantic, not merely visual. An `attachment` participates in spatial assembly: for example, attaching the grip point of a sword design to the hand point of a person design. A `port` participates in logical connectivity: for example, wiring an output of one logic-gate design to an input of another. These mechanisms may later have different compatibility rules and different runtime behavior even though they share the same underlying coordinate-point representation.

The `tags` field provides additional classification and application-specific meaning. Tags should refine a connector's role rather than create a large role hierarchy. For example:

```json
{
  "id": "input-a",
  "x": 0,
  "y": 20,
  "angle": 180,
  "role": "port",
  "tags": ["input", "boolean"]
}
```

```json
{
  "id": "output",
  "x": 80,
  "y": 20,
  "angle": 0,
  "role": "port",
  "tags": ["output", "boolean"]
}
```

```json
{
  "id": "grip",
  "x": 12,
  "y": 40,
  "angle": 90,
  "role": "attachment",
  "tags": ["weapon-grip", "handheld"]
}
```

Thus Vector-Loom should not introduce roles such as `input-port` and `output-port` at this stage. Both are simply `role: "port"`, with `input` or `output` expressed through tags. This keeps the structural role vocabulary small while allowing applications to describe arbitrary distinctions such as `input`, `output`, `bidirectional`, `boolean`, `power`, `data`, `hand`, `grip`, or other domain-specific concepts.

Likewise, interaction concepts such as `hot-spot` should normally be tags rather than roles. A port may also be a hot spot; an attachment may also be a hot spot. `hot-spot` describes how an application may choose to interact with the point, while `role` describes what the point fundamentally exists to do in the design model.

For example:

```json
{
  "id": "input-a",
  "x": 0,
  "y": 20,
  "angle": 180,
  "role": "port",
  "tags": ["input", "boolean", "hot-spot"]
}
```

The same connector representation should work at any depth of the transform hierarchy. If a connector belongs to a rotated or translated group, Vector-Loom should be able to derive its effective position and angle in the enclosing design, assembly, or world coordinate system. This transformed coordinate frame is what later attachment and wiring mechanisms should operate on.

The immediate implementation goal should therefore be modest: introduce connector points as addressable, non-rendering elements; propagate their transforms correctly; allow them to carry `id`, `role`, and `tags`; and make their effective coordinate frame queryable by the host application. Actual attachment behavior, compatibility checking, wiring semantics, and editor interaction can be developed afterward.

## P.S. — Decisions and Further Direction

The serialized element discriminator will be simply `"connector"`.

Connector `id` is strictly required and must be unique within its containing
design. Connector `x` and `y` are strictly required. Connector `angle`
defaults to `0` when omitted.

A resolved connector will be addressed by its placed instance name together
with its connector ID:

```text
<instance-name> + <connector-id>
```

For example:

```text
find_connector("sword-17", "grip")
```

can establish the current resolved connector as working context for a nearby
operation. Its result needs to preserve the connector's role, tags, and
effective coordinate frame so later attachment or connection mechanisms can
reason about it.

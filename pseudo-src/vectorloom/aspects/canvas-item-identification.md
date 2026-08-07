# Aspect — Canvas Item Identification

This aspect preserves VectorLoom definition identity when a primitive is
realized as a live Tk Canvas item. It gives rendering, hit-testing, and future
interactive behavior a shared way to answer what design, shape, semantic tag,
and placed instance an item belongs to.

## Applies To

- VectorLoom Basic documents in `docs/raw/0015__vectorloom-basic.json`.
- Canvas Context when it creates primitive Canvas items.
- Callers that place a design and optionally name that particular placement.
- Future hit-testing, selection, interaction, and editor mechanisms.

## Canvas Tag Contract

When Canvas Context renders one primitive from a design, it attaches these Tk
Canvas tags to the resulting Canvas item:

| Source | Canvas tag | Presence |
| --- | --- | --- |
| Design key `foo` | `design:foo` | Always. |
| Primitive `id: "door"` | `shape:door` | When the primitive has an `id`. |
| Primitive `tags: ["interactive", "doorway"]` | `tag:interactive`, `tag:doorway` | One for each declared tag. |
| Caller-supplied placement name `house-17` | `instance:house-17` | When the placement has an instance name. |

## Meaning

- `design:` identifies the reusable design that supplied the primitive.
- `shape:` identifies the optional primitive ID within that design. It is not
  a Canvas-instance identifier by itself.
- `tag:` carries the primitive's declared semantic labels.
- `instance:` identifies one particular caller-placed copy of a design. Every
  primitive Canvas item created by that placement receives the same instance
  tag.

Tk's numeric Canvas item ID is separate: it is unique for the live Canvas but
is not a durable VectorLoom identity.

## Encoding

Canvas tags use the `prefix:value` form shown above. The prefix is the portion
before the first colon. This aspect does not yet restrict characters in the
value; readers that interpret namespaces split only on the first colon.

## Runtime Boundary

`id` and `tags` are serialized primitive data. `design:` is derived from the
design map key during rendering. `instance:` is runtime placement data supplied
by the caller and is not part of a VectorLoom Basic document.

Canvas Context receives the optional instance name through
`draw(design_name, instance_name=None)`. The supplied instance name applies to
every primitive Canvas item created by that one draw call.

## Consequences

- A design may be stamped more than once without losing template identity.
- Two Canvas items may both have `shape:door`, while distinct `instance:` tags
  distinguish their placed copies.
- Hit-testing can inspect an item's tags to route interaction to a shape,
  design, semantic category, or placed instance.

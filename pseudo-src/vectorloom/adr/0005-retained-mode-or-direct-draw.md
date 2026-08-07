# ADR 0005: Retained mode or direct draw

- Date: 2026-08-07
- Status: Undecided

## Context

Vector Loom may eventually need a retained assembly world: durable named design
instances with their own placement and transform state, which can be found,
attached, moved, rotated, or otherwise mutated.

It may instead remain, at least in some layers, a direct-draw runtime: a caller
supplies a design specification and placement, and Vector Loom renders it onto
a Canvas without retaining a durable instance record.

This choice affects connector lookup, attachment, mutation, and the meaning of
an instance name. The current small runtime is still developing the basic data
format and rendering concepts, so committing to either model now would be
premature.

## Decision

The architectural question remains undecided.

For the current runtime, keep a small direct-draw model. An `instance_name`
given to `draw()` is a render label: it is attached to the Canvas items as an
`instance:<name>` tag, but it is not a promise of durable instance state.

If retained instances become necessary, Vector Loom may introduce an explicit
instance or assembly world and change the surrounding design accordingly.

## Consequences

- Current drawing work can stay focused on design traversal, transforms, and
  Canvas rendering.
- Current APIs must not imply that an `instance_name` can later be found or
  mutated as a retained object.
- Attachment, connector addressing across placed instances, and mutation need
  further design before they become runtime capabilities.
- The future retained-mode decision remains open and may revise this direction.

## See Also

- [`0018__instance-assembly-and-mutation-direction.md`](../../../docs/raw/0018__instance-assembly-and-mutation-direction.md)

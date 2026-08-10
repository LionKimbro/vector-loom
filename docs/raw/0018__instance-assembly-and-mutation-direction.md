```text
date: 2026-08-07
title: Instance, Assembly, and Mutation Direction
purpose: Record the emerging need for durable placed instances, attachment, and
  a future mutation language.
```

# Instance, Assembly, and Mutation Direction

Connector lookup reveals that an `instance_name` passed to the current immediate
drawing operation is not yet a durable instance record. It currently labels
Canvas items but does not preserve a named placed design that can later be
found, moved, rotated, attached, or detached.

## Present Immediate-Mode Direction

For the time being, Vector Loom is taking an immediate-mode path. A render pass
may produce an ephemeral connector registry for the caller-provided instance
IDs it draws, but this registry is not a persistent scene or assembly world.
This document remains a provisional direction for the hypothetical future in
which durable placed instances and their mutation become necessary.

Attachment therefore requires a future instance or assembly world that retains
placed-instance identity and transform state. This is separate from the
reusable VectorLoom Basic design library: mutating a placed instance should not
silently edit the shared design definition from which it came.

## Connector Context

A connector lookup may establish the current resolved connector as working
context:

```text
select_connector("sword-17", "grip")
```

The resulting context can supply the connector's role, tags, and effective
coordinate frame to a nearby attachment or connection operation.

## Early Mutation Language

A future mutation language may naturally include operations such as:

```text
select(instance_name)
select_connector(instance_name, connector_id)  -> current connector context
attach(instance_name)
rotate(group_id, degrees, flags=["absolute"])
rotate(group_id, degrees, flags=["relative"])
```

These are directional examples, not settled API signatures.

## Open Attachment Question

The exact `attach()` argument shape remains open. Before it can be settled, the
system must say which connector on the moving instance is used as its source
attachment frame, and whether mutation targets a placed instance, a nested
group within that instance, or the reusable design definition itself.

The working direction is that these are instance-level mutations, not edits to
the shared reusable design.

## See Also

- [`ADR 0005: Retained mode or direct draw`](../../pseudo-src/vectorloom/adr/0005-retained-mode-or-direct-draw.md)
- [`canvas-context.md`](../../pseudo-src/vectorloom/modules/canvas-context.md)
  — the present immediate-mode connector registry.

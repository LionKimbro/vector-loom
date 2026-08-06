# ADR 0004: Defer the scope of element ID uniqueness

- Date: 2026-08-06
- Status: Deferred

## Context

Vector-Loom elements need IDs for addressing and assembly, but the required uniqueness scope depends on design instancing and hierarchy semantics that are not yet settled.

Candidate rules are:

1. IDs are unique among the immediate contents of one group.
2. IDs are unique throughout one design.
3. IDs are unique throughout an assembled hierarchy of attached design instances.

## Decision

Do not choose an element-ID uniqueness scope yet. Keep this question explicitly unresolved until the addressing, instancing, and assembly model is developed further.

## Consequences

- Current work must not depend on global uniqueness unless it establishes that requirement independently.
- APIs and storage formats should avoid prematurely baking in one candidate scope.
- A future ADR must settle the scope before cross-instance addressing or assembled-hierarchy identity becomes part of the public model.

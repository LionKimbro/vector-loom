# ADR 0001: Call reusable named structures “designs”

- Date: 2026-08-06
- Status: Accepted

## Context

Vector-Loom libraries contain reusable named structures that may be instantiated more than once. Existing language could imply that every reusable structure must be a visible drawing.

## Decision

Call these reusable named structures **designs**.

A design may be instantiated multiple times. A design is not necessarily a visible drawing: it may represent a structural or spatial mechanism, such as a joint, anchor structure, or arrangement of connectors, with little or no directly rendered geometry.

## Consequences

- Library, API, and documentation terminology should use “design” for the reusable named structure and “design instance” for a placement of that design.
- Rendering behavior must not be inferred from whether something is a design.

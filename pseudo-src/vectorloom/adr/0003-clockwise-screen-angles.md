# ADR 0003: Use clockwise degrees for angles

- Date: 2026-08-06
- Status: Accepted

## Context

Vector-Loom is screen-oriented: positive `x` extends to the right and positive `y` extends downward. Angle direction must be explicit so that APIs and renderers do not silently disagree.

## Decision

Express angles in degrees. Positive angles rotate **clockwise**.

## Consequences

- This convention matches Vector-Loom’s screen coordinate system.
- APIs, serialized designs, documentation, and tests must treat a positive angle as clockwise.
- Integrations using a mathematical y-up coordinate system must convert angle direction at their boundary.

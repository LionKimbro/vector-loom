# BAD Pseudocode System

This directory is a normative BAD design layer for a software project.
It is semantic pseudocode and bounded design, not executable Python.
The rendered application is planned for a project beneath `src/`.

## Layout

- `project-profile/` — target habitat, conventions, and project-wide assumptions.
- `modules/` — bounded sketches for renderable implementation regions.
- `interfaces/` — capabilities supplied by the host system, tools, frameworks, and libraries.
- `aspects/` — cross-cutting contracts and rules that apply across modules.

## Reading and Rendering Rule

Each module sketch names both its **render target**.  The render
target is where a future BAD render should place the implementation.
A render may make routine local decisions, but must not change a
boundary, ownership rule, or open decision without recording that
change explicitly.


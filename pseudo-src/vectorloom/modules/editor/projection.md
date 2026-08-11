# Module — Editor Projection

This module owns the visible editor: both library trees, Canvas realization,
inspector presentation, and editor-only overlays.

## Render Target

`src/vectorloom/editor/projection.py`

## OWNS

- Tree rows, inspector widgets, Canvas item handles, and realized camera.
- Rendering the current World Model library through Canvas Context.
- Editor-only group bounds/origin overlays and connector-point markers.
- White/blue/green/red visual assignment on a black Canvas background.

## READS

- Discrete Engine workspace state.
- World Model library state.
- Current Organism immediates.

## ENSURES

- White is ordinary drawing material; blue is selection/focal context; green
  marks connector points; red marks error or invalid interaction attention.
- The active focal container's local `(0, 0)` is centered on the Canvas.
- Projection does not mutate workspace or durable library state.

## DOES NOT OWN

- Input interpretation, committed selection, focal address truth, semantic
  events, world mutation, or history.

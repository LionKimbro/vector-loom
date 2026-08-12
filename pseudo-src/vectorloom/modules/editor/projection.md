# Module — Editor Projection

This module is the overall projection boundary for the visible editor.  It
coordinates its Tkinter-control and Canvas-surface parts.

## Render Target

`src/vectorloom/editor/projection.py`

## OWNS

- The complete visible realization of current editor state.
- Projection-cycle coordination between `projection-tkinter.md` and
  `projection-canvas.md`.

## READS

- Discrete Engine workspace state.
- World Model library state.
- Current Organism immediates.

## ENSURES

- Projection does not mutate workspace or durable library state.
- Every projection pass presents the same current state across the Tkinter
  controls and Canvas surface.

## DOES NOT OWN

- Input interpretation, committed selection, focal address truth, semantic
  events, world mutation, or history.
- The physical editor window and its Tk callback bindings; Editor Window owns
  those surfaces and supplies their widget handles.

## Pseudocode

```text
def project():
    project Tkinter controls
    project Canvas surface
```

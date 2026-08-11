# Module — Editor Discrete Engine

This module owns committed editor workspace state and the reducer law for
semantic events.  It is distinct from the durable Vector Loom library.

## Render Target

`src/vectorloom/editor/discrete_engine.py`

## OWNS

- Committed selection.
- Active design/style orientation, focal container address, active tool, and
  desired semantic camera.
- Reducing semantic events into replacement workspace state and explicit
  effects.

## Initial Workspace Shape

```python
workspace = {
    "selection": None,
    "primary-design-name": None,
    "active-style-name": None,
    "focal-address": ".",
    "active-tool": None,
    "desired-camera": None,
}
```

`"primary-design-name"` is the design currently being worked on and projected
on the central Canvas, or `None` when no design is open.  `"."` means the
editor-only root container of that primary design.

## Initial Semantic Events

```text
SET_SELECTION
SET_FOCAL_ADDRESS
SET_PRIMARY_DESIGN
SET_ACTIVE_STYLE
```

## DOES NOT OWN

- Raw pointer input, hit testing, gesture recognition, durable library data,
  Canvas/widget state, or checkpoint lineage.

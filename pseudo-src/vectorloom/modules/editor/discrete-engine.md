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
    "next-element-id": 1,
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
SET_ACTIVE_TOOL
REQUEST_CREATE_LINE
EXIT_EDITOR
```

`REQUEST_CREATE_LINE` is a completed line-drawing gesture.  The reducer does
not mutate the World Model itself.  It reads the active primary design and
focal address, assigns an element identity, and emits one directed World Model
effect:

```python
def reduce_request_create_line(event):
    design_name = workspace["primary-design-name"]
    focal_address = workspace["focal-address"]
    element_id = f"element-{workspace['next-element-id']}"
    workspace["next-element-id"] += 1

    emit_effect({
        "owner": "world-model",
        "type": "ADD_LINE",
        "design-name": design_name,
        "focal-address": focal_address,
        "element-id": element_id,
        "start-local": event["start-local"],
        "end-local": event["end-local"],
    })
```

`REQUEST_CREATE_LINE` must identify a drawable focal container and a
non-degenerate line.  The reducer assigns the element identity and emits
`ADD_LINE`; otherwise, it emits no effect.

`EXIT_EDITOR` is posted directly by the Editor Window close callback.  It
emits an explicit Editor Window destroy effect.  The Runtime routes that
effect; the reducer does not destroy Tk widgets directly.

## DOES NOT OWN

- Raw pointer input, hit testing, gesture recognition, durable library data,
  Canvas/widget state, or checkpoint lineage.

```text
date: 2026-08-11
title: Vector Loom Editor CIRA Frame Rendered
purpose: Record the rendered, behavior-light editor frame and its initial
  raw-input verification surface.
```

# Vector Loom Editor CIRA Frame Rendered

The initial CIRA editor frame has been rendered beneath `src/vectorloom/editor/`.
It is an architectural and visual test surface, not yet an editor capable of
loading or changing a Vector Loom file.

## Rendered Modules

```text
src/vectorloom/editor/
  editor_bootstrap.py
  editor_window.py
  event_queue.py
  interaction_runtime.py
  tokenizers.py
  judge.py
  organisms.py
  discrete_engine.py
  world_model.py
  history_manager.py
  projection.py
```

The editor is available through the `vectorloom-editor` project script and
`python -m vectorloom.editor`.  The existing `vectorloom` entry point continues
to run the kinetic demonstration.

## Current Visible Test Surface

The Editor Window creates a resizable three-pane Toplevel:

- Designs and Styles Treeviews in the left pane;
- a black Canvas in the center pane;
- a right inspector frame used temporarily for the ten most recent drained raw
  input records.

While no library is loaded, Projection supplies temporary `(no designs loaded)`
and `(no styles loaded)` Treeview rows so their raw-selection adapters can also
be exercised.

Canvas, Treeview, and keyboard callbacks post normalized raw records to the
FIFO input queue.  Adjacent pointer-motion records coalesce without crossing
another event record.  The window-close callback posts the already-semantic
`EXIT_EDITOR` request directly to the semantic-event queue.  Projection
displays the raw queue's recent diagnostic history because the pending queue is
normally empty by the time the projection pass occurs.

## CIRA Status

- Interaction Runtime establishes RAW/DERIVED snapshots and the CIRA cycle.
- Tokenizer and Organism registries are intentionally empty.
- Discrete Engine supports the initial workspace orientation events.
- World Model, History Manager, and Projection exist as bounded shells.
- No library loading, editing, selection interpretation, drawing tool, history
  action, or durable mutation behavior is rendered yet.

## Verification

Focused tests cover raw-event coalescing, workspace reduction, and an editor
interaction cycle without requiring a live Tk window.

## See Also

- `../../pseudo-src/vectorloom/modules/editor/readme.md`
- `0021__vectorloom-tkinter-project-structure-direction.md`

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
- The temporary diagnostic presentation of the ten most recent raw input
  records in the otherwise-reserved inspector frame.
- Status-bar text describing the committed active drawing tool.

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

## Temporary Input-Queue Diagnostic

Before the inspector has a selected-item form, Projection uses its reserved
right-hand `inspector-frame` to show a lightweight input diagnostic.  This is a
temporary testing measure for verifying Editor Window callback wiring and raw
event ordering.

While no library is loaded, Projection also places one temporary non-library
placeholder row in each Treeview: `(no designs loaded)` and `(no styles
loaded)`.  This permits Treeview-selection adapter testing without inventing
durable library data.

Projection reads Event Queue's `recent-events` diagnostic history.  It must not
read pending queue records as though they were a stable view: Interaction
Runtime drains those records before Projection runs, so the pending queue will
normally be empty.

```python
def project_temporary_input_queue_diagnostic():
    clear every child widget from editor_window.widgets["inspector-frame"]

    create a label: "Recent raw input"
    for event in event_queue.recent_events[-10:]:
        create one left-aligned label containing a compact representation of event
```

This diagnostic does not change selection, workspace state, World Model data,
or the queue itself.  It will be removed or moved into a later debug view when
the selected-item inspector is designed.

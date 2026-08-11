# Module — Editor Window

This module owns the editor's Tk widgets and translates toolkit activity into
raw input records.  Its central layout is a left library pane, center Canvas,
and right selected-item pane.

## Render Target

`src/vectorloom/editor/editor_window.py`

## OWNS

- The editor Toplevel and its widget handles.
- The left Designs and Styles trees, center Canvas, and right inspector frame.
- Tk bindings and thin callback adapters for Canvas, tree, inspector, and
  window keyboard input.

## CALLS

- `event_queue` posting operations.
- `tk_runtime.now_ms()` while creating time-bearing raw input records.

## ENSURES

- The Canvas background is black.
- Tk callbacks post raw facts only; they do not select items, mutate the
  library, interpret gestures, or render projection.

## DOES NOT OWN

- RAW state, tokenization, semantic events, editor selection, focal address,
  durable library data, or Canvas projection.

## Initial Layout

```text
Designs tree / Styles tree | Canvas | selected-item inspector
```

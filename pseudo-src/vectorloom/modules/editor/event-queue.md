# Module — Editor Input Event Queue

This module owns pending normalized raw input.  It is the boundary between Tk
callbacks and the editor CIRA Runtime.

## Render Target

`src/vectorloom/editor/event_queue.py`

## OWNS

- FIFO storage for pending raw input records.
- Posting records and draining them in order.
- Coalescing adjacent Canvas pointer-motion records while preserving sample
  order.

## ENSURES

- Queue records describe toolkit facts, not semantic meaning.
- A tree-selection callback may identify a widget and selected row address,
  but must not declare `SET_SELECTION` itself.

## DOES NOT OWN

- RAW snapshots, tokenization, gesture episodes, semantic events, reduction,
  world mutation, or projection.

## Initial Record Kinds

```text
POINTER_MOTION, BUTTON_1_PRESSED, BUTTON_1_RELEASED,
POINTER_LEFT_CANVAS, KEY_PRESSED, KEY_RELEASED, WIDGET_ACTIVATED
```

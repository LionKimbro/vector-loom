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
POINTER_LEFT_CANVAS, KEY_PRESSED, KEY_RELEASED,
TREE_SELECTION_CHANGED, WIDGET_ACTIVATED, WINDOW_CLOSE_REQUESTED
```

`TREE_SELECTION_CHANGED` reports the physical Treeview and its selected item
identifiers.  It does not itself assert the corresponding Vector Loom address
or committed editor selection.

## Sketch

```python
event_queue = []


def post_pointer_motion(x, y, ms):
    sample = {"x": x, "y": y, "ms": ms}

    if event_queue and event_queue[-1]["type"] == "POINTER_MOTION":
        event_queue[-1]["samples"].append(sample)
        return

    event_queue.append({"type": "POINTER_MOTION", "samples": [sample]})


def post_event(event):
    event_queue.append(event)


def drain_events():
    pending = list(event_queue)
    event_queue.clear()
    return pending
```

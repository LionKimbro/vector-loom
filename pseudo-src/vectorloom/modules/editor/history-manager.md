# Module — Editor History Manager

This module owns checkpoint lineage for undo and redo.  It is present in the
frame, but no checkpoint packet format or user-visible undo behavior is
designed yet.

## Render Target

`src/vectorloom/editor/history_manager.py`

## OWNS

- Checkpoint storage, cursor, redo truncation, and retrieval.
- Undo/redo lineage expressed as opaque World Model revision identifiers.
- State-jump packets containing a World Model revision identifier and Discrete
  Engine workspace state.

## DOES NOT OWN

- Event reduction, raw interaction history, world mutation law, or projection.
- Revision data, revision-identifier meaning, or reconstruction of a library
  state from a revision identifier.

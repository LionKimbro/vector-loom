# Module — Editor History Manager

This module owns checkpoint lineage for undo and redo.  It is present in the
frame, but no checkpoint packet format or user-visible undo behavior is
designed yet.

## Render Target

`src/vectorloom/editor/history_manager.py`

## OWNS

- Checkpoint storage, cursor, redo truncation, and retrieval.
- Later state-jump packets containing the needed World Model revision and
  Discrete Engine workspace state.

## DOES NOT OWN

- Event reduction, raw interaction history, world mutation law, or projection.

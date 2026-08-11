# Module — Editor World Model

This module owns the durable Vector Loom library the editor is viewing and
eventually changing.

## Render Target

`src/vectorloom/editor/world_model.py`

## OWNS

- The loaded library's designs and styles.
- Applying lawful world-mutation effects produced by the Discrete Engine.
- The future revision representation needed to reconstruct durable library
  state.

## MAY SAFELY ASSUME

- VectorLoom Basic reader/validation will provide a lawful library before
  editing begins.

## DOES NOT OWN

- Ordinary selection, focal group, tool, camera, raw interaction, Canvas
  overlays, or History Manager lineage.

## Open Boundary

The specific load/save and revision strategy is not decided by this frame.

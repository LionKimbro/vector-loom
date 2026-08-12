# Module — Editor World Model

This module owns the durable Vector Loom library the editor is viewing and
eventually changing.

## Render Target

`src/vectorloom/editor/world_model.py`

## OWNS

- The loaded library's designs and styles.
- The current durable-library revision.
- Revision identifiers, the revision store, and reconstruction of a library
  state from a revision identifier.
- Applying lawful world-mutation effects produced by the Discrete Engine.
- Replacing the current library with a specified reconstructed revision.

## MAY SAFELY ASSUME

- VectorLoom Basic reader/validation will provide a lawful library before
  editing begins.

## DOES NOT OWN

- Ordinary selection, focal group, tool, camera, raw interaction, Canvas
  overlays, or History Manager lineage.
- Undo/redo position, redo truncation, or choosing which prior/next revision
  should be restored.

## Open Boundary

The specific load/save and revision strategy is not decided by this frame.

## Pseudocode

### Handle Add Line

```text
def handle_add_line(effect):
    locate the named design and its focal-address
    make a line with effect.element-id, effect.start-local, and effect.end-local
    append the committed line to that root/group container's ordered children
```

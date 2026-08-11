# Vector Loom Editor — CIRA Frame

These bounded sketches establish the editor's CIRA frame before editor
behavior is designed.  They are deliberately light: they assign authority and
the interaction-cycle order, but do not yet define drawing tools, file loading,
mutation law, or a persistent history strategy.

```text
Tk callbacks
  → Event Queue
  → Interaction Runtime
  → Tokenizers → Judge → Organisms
  → Discrete Engine
  → effects routed to World Model / History Manager / Projection
```

The editor-only root container of a selected design has address `"."`.  It is
not a serialized Vector Loom group.  A nested structural address begins with
that root, such as `.6` or `.6.0`.

## Current Module Set

- `editor-bootstrap.md` — configures the shared App Shell for the editor.
- `editor-window.md` — owns the three-pane Tk window and thin input adapters.
- `event-queue.md` — raw input FIFO and motion coalescing.
- `interaction-runtime.md` — drives the CIRA cycle and routes effects.
- `tokenizers.md` — produces perceptual facts from RAW input.
- `judge.md` — coordinates interaction-resource leases.
- `organisms.md` — owns continuous interaction episodes.
- `discrete-engine.md` — owns committed editor workspace state and reduction.
- `world-model.md` — owns the durable Vector Loom library.
- `history-manager.md` — owns checkpoint lineage.
- `projection.md` — owns the visible panes and Canvas overlays.

## See Also

- `../../../../docs/raw/0021__vectorloom-tkinter-project-structure-direction.md`
- `C:\lion\github\reducer-core-architecture\docs\raw\0004__cira_agentic-implementation-brief.json`
- `C:\lion\github\blackboard-judge-architecture-demo\docs\pseudocode`

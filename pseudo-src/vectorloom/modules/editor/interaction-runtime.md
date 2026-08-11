# Module — Editor Interaction Runtime

This module drives the editor's CIRA cycle.  It owns the order in which raw
input becomes perception, continuous behavior, discrete meaning, effects, and
visible projection.

## Render Target

`src/vectorloom/editor/interaction_runtime.py`

## OWNS

- `raw`, `raw_prev`, `derived`, and `derived_prev` runtime snapshots.
- The semantic-event queue.
- Update-cycle ordering, effect routing, and continuity-reset choreography.

## CALLS

- Event Queue drain.
- Tokenizer pass, Judge maintenance, and Organism evaluation.
- Discrete Engine reduction.
- World Model, History Manager, and Projection effect handlers.

## ENSURES

```text
drain raw input
→ preserve prior RAW and DERIVED snapshots
→ populate RAW
→ tokenize DERIVED
→ maintain Judge and evaluate Organisms
→ drain semantic events through Discrete Engine
→ route effects
→ render Projection
```

## DOES NOT OWN

- Perceptual fact definitions, gesture behavior, semantic transition law,
  durable library state, history lineage, or Canvas/widget manifestation.

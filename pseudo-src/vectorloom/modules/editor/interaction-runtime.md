# Module — Editor Interaction Runtime

This module drives the editor's CIRA cycle.  It owns the order in which raw
input becomes perception, continuous behavior, discrete meaning, effects, and
visible projection.

## Render Target

`src/vectorloom/editor/interaction_runtime.py`

## OWNS

- `raw`, `raw_prev`, `derived`, and `derived_prev` runtime snapshots.
- The semantic-event queue.
- The ephemeral runtime-stage register.
- Update-cycle ordering, effect routing, and continuity-reset choreography.

## RAW Snapshot Shape

`raw` holds current input facts, not queued event records:

```python
raw = {
    "x": 0,
    "y": 0,
    "ms": None,
    "inside-canvas": False,
    "button-1-down": False,
    "keys-down": [],
    "last-event-type": None,
    "last-tree-selection": None,
    "last-widget-activation": None,
}
```

The queue is only an input transport.  Runtime drains it, applies each record
to this persistent snapshot, and then runs one CIRA cycle for that resulting
RAW state.  A coalesced pointer-motion packet runs one cycle per recorded
sample, in order.

## CALLS

- Event Queue drain.
- Tokenizer pass, Judge maintenance, and Organism evaluation.
- Discrete Engine reduction.
- World Model, History Manager, and Projection effect handlers.
- Editor Window's destroy operation when routing an `editor-window` effect.

## ENSURES

- The runtime-stage register is clear before the next update cycle, including
  when a stage raises an error.

## DOES NOT OWN

- Perceptual fact definitions, gesture behavior, semantic transition law,
  durable library state, history lineage, or Canvas/widget manifestation.

## Pseudocode

```text
drain raw input
→ for each normalized record:
    stage APPLYING-RAW: preserve prior RAW and DERIVED snapshots; apply record
    stage TOKENIZING: tokenize DERIVED
    stage JUDGING: maintain Judge
    stage ORGANISMS: evaluate Organisms
    stage REDUCING: drain semantic events through Discrete Engine
    stage ROUTING-EFFECTS: route directed effects to their owning machines
    stage PROJECTING: render Projection
→ clear runtime stage
```

```text
def run a runtime stage(stage-name, work):
    set runtime stage to stage-name
    perform work
    clear runtime stage even if work failed
```

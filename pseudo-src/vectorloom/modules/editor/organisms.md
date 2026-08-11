# Module — Editor Interaction Organisms

This module owns continuous editor interaction episodes.  It will contain
finite-state machines such as click selection, drawing, drag, pan, and later
resize; it starts as a registered but behavior-light frame.

## Render Target

`src/vectorloom/editor/organisms.py`

## OWNS

- Organism registry, FSM states, held values, and episode-local data.
- Emission of semantic events and one-frame Projection immediates.

## READS

- RAW and DERIVED facts.
- World Model geometry, Discrete Engine workspace state, and Projection's
  realized camera as observations.
- Judge permission decisions.

## ENSURES

- Organisms do not perform private hit testing, mutate world/workspace state,
  or draw Canvas items.
- Completed interaction meaning becomes a semantic event; in-progress feedback
  becomes an immediate.

## Initial Frame

The initial registry may be empty.  Add an organism only with a bounded sketch
for its tokenizer facts, Judge resources, semantic events, and immediates.

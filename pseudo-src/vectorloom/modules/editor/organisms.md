# Module — Editor Interaction Organisms

This module owns continuous editor interaction episodes.  It will contain
finite-state machines such as click selection, drawing, drag, pan, and later
resize; its initial registry is empty.

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

The initial registry is empty.  `EXIT_EDITOR` is posted directly because a
window-close request is already semantic meaning, not a continuous gesture.

Add each later organism only with a bounded sketch for its tokenizer facts,
Judge resources, semantic events, and immediates.

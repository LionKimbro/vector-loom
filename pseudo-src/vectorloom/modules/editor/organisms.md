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

## DOES NOT OWN

- Perceptual fact derivation, resource arbitration, workspace state, World
  Model mutation, or Canvas realization.

## Pseudocode

### Line Drawing

```text
organism LINE-DRAWING:
    state IDLE:
        if active tool is line and Button 1 went down:
            ask Judge whether Line Drawing may acquire pointer-drawing
            if Judge accepts:
                acquire pointer-drawing
                remember the current focal-local pointer location as start-local
                become DRAWING
                issue line-draft from start-local to start-local
        stop

    state DRAWING:
        if Button 1 is down:
            issue line-draft from start-local to the current focal-local pointer location
            stop
        else:  # Button 1 is up
            emit REQUEST_CREATE_LINE with start-local and the current focal-local pointer location
            withdraw line-draft
            release pointer-drawing
            forget held values
            become IDLE
```

### Exit Editor

```text
organism EXIT-EDITOR:
    state IDLE:
        if exit-editor was requested:
            emit EXIT_EDITOR
```

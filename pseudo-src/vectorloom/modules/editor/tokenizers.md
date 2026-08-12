# Module — Editor Tokenizers

This module owns `derived`: the editor's current perceptual interpretation of
RAW input.

## Render Target

`src/vectorloom/editor/tokenizers.py`

## OWNS

- Ordered tokenizer registration.
- Canvas-pointer, button-edge, click, drag-threshold, and target facts.
- Perceptual hit testing against the current projected camera and World Model
  geometry.

## ENSURES

- Each cycle begins with an empty current `derived` mapping.
- Organisms receive one complete shared perception.
- Tokenizers do not emit semantic events, effects, or Canvas commands.

## DOES NOT OWN

- Gesture state, resource claims, committed selection, focal address, durable
  mutation, or projection.

## Pseudocode

### Tokenize Button 1 Edges

Button 1 edge facts are derived from the two RAW snapshots.  The names describe
physical state transitions, rather than Tk callback names:

```python
def tokenize_button_1_edges():
    button-1-went-down is true if Button 1 was up last turn, but is down this turn
    button-1-went-up is true if Button 1 was down last turn, but is up this turn
```

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

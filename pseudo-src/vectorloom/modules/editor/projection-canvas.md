# Module — Editor Projection: Canvas Surface

This is the Canvas-surface part of Editor Projection.  It defaults to the
overall boundary, reads, and exclusions declared in `projection.md`.

## Render Target

Contributes to `src/vectorloom/editor/projection.py`.

## OWNS

- Canvas item handles and realized camera.
- Rendering the current World Model library through Canvas Context.
- Editor-only group bounds/origin overlays and connector-point markers.
- White/blue/green/red visual assignment on a black Canvas background.
- Focal-local and Canvas coordinate conversion used by editor presentation.

## ENSURES

- The active focal container's local `(0, 0)` is centered on the Canvas.
- White is ordinary drawing material; blue is selection/focal context; green
  marks connector points; red marks error or invalid interaction attention.
- A temporary immediate is never a durable Canvas or World Model element.

## DOES NOT OWN

- Canvas widget handle; Editor Window owns the physical Canvas.
- Vector Loom's reusable Canvas drawing operations; Canvas Context owns those.
- Input interpretation, World Model mutation, or durable geometry.

## Pseudocode

```text
def project Canvas surface:
    render the committed focal design through Canvas Context
    render editor-only focal, group, connector-point, and selection overlays
    if Line Drawing has line-draft immediate:
        draw it in blue after the committed Canvas material


def canvas_to_focal_local(canvas-x, canvas-y):
    use the realized camera and focal transform
    return focal-local (x, y)
```

# Module — Canvas Host Demo

This module is the current Vector Loom proving-ground experiment. It uses the
Canvas Host Window's Canvas to install and animate a disposable transform
laboratory, testing Canvas Context and Transform Stack together.

## Render Target

`src/vectorloom/demo/canvas_host_demo.py`

## See Also

- `../tk-runtime/canvas-host-window.md` — the physical window and Canvas this demo uses.
- `../canvas/canvas-context.md` — design traversal and Canvas drawing.
- `../canvas/transform-stack.md` — nested coordinate-frame operations.

## OWNS

- The periodic callback that advances this demo.
- Registration and unregistration of that callback with Tk Runtime.
- The demo's animation state and disposable transform groups.
- Installing this demo's disposable styles and design into Canvas Context.
- Clearing and redrawing the Canvas for each experimental frame.

## READS

- Canvas Host Window's `g["canvas"]`.
- Tk Runtime's periodic callback slot while registering or unregistering this
  demo.
- Canvas Context and Transform Stack while drawing the experiment.

## CALLS

- Canvas Host Window's `set_close_callback()`.
- Canvas Context's `set_canvas()`, `draw()`, and Transform Stack operations.
- The Canvas's `delete("all")` operation before each experimental redraw.

## MAY SAFELY ASSUME

- Canvas Host Window has been created and has a live Canvas at `g["canvas"]`.
- Canvas Context and Transform Stack have disposable style, design, and
  transform state during this early proving-ground phase.

## ENSURES

- `start_canvas_host_demo()` displays a transform laboratory centered in the
  Canvas and registers the demo's periodic callback.
- Every timer tick advances orbital, spin, counter-spin, and bobbing state,
  then redraws the laboratory.
- `stop_canvas_host_demo()` unregisters this demo's callback, so a later timer
  tick cannot target a Canvas that the host is destroying.
- The experiment uses Canvas Context and Transform Stack rather than direct
  Canvas primitive calls, apart from clearing the disposable Canvas.

## DOES NOT OWN

- Creating, sizing, titling, or destroying the Canvas Host Window.
- Tk Runtime's timer scheduling policy.
- Canvas Context's drawing rules, Transform Stack's transform rules, or
  durable VectorLoom library data.

## Sketch

```python
from math import cos, sin, tau

demo_g = {
    "orbit-angle": 0,
    "spin-angle": 0,
    "counter-spin-angle": 0,
    "bob-phase": 0,
    "orbit-group": None,
    "spin-group": None,
    "counter-spin-group": None
}

def start_canvas_host_demo():
    canvas_host_window.set_close_callback(stop_canvas_host_demo)
    Set Tk Runtime's periodic callback to periodic_timer_callback.
    Call canvas_context.set_canvas(canvas_host_window.g["canvas"]).

    canvas_context.styles["orbit-guide"] = {
        "stroke": "#8a8a8a", "width": 1, "dash": "4 4"
    }
    canvas_context.styles["arm"] = {"stroke": "#315f97", "width": 3}
    canvas_context.styles["body"] = {
        "stroke": "#182c44", "fill": "#83c5e8", "width": 2
    }
    canvas_context.styles["rotor"] = {"stroke": "#9e3d3d", "width": 3}
    canvas_context.styles["counter-rotor"] = {
        "stroke": "#4d8c51", "width": 2
    }

    demo_g["orbit-group"] = {
        "type": "group", "id": "orbit", "angle": 0, "contents": []
    }
    demo_g["spin-group"] = {
        "type": "group", "id": "spinner", "x": 150, "angle": 0,
        "contents": []
    }
    demo_g["counter-spin-group"] = {
        "type": "group", "id": "counter-spinner", "angle": 0,
        "contents": [
            {"type": "line", "x1": -30, "y1": 0,
             "x2": 30, "y2": 0, "style": "counter-rotor"},
            {"type": "line", "x1": 0, "y1": -30,
             "x2": 0, "y2": 30, "style": "counter-rotor"},
        ],
    }
    demo_g["spin-group"]["contents"] = [
        {"type": "rect", "x": -22, "y": -16, "w": 44, "h": 32,
         "style": "body"},
        {"type": "line", "x1": -45, "y1": 0,
         "x2": 45, "y2": 0, "style": "rotor"},
        {"type": "line", "x1": 0, "y1": -45,
         "x2": 0, "y2": 45, "style": "rotor"},
        demo_g["counter-spin-group"],
    ]
    demo_g["orbit-group"]["contents"] = [
        {"type": "line", "x1": 0, "y1": 0,
         "x2": 150, "y2": 0, "style": "arm"},
        demo_g["spin-group"],
    ]
    canvas_context.designs["kinetic-transform-lab"] = {
        "contents": [
            {"type": "oval", "x": -150, "y": -150, "w": 300, "h": 300,
             "style": "orbit-guide"},
            {"type": "oval", "x": -8, "y": -8, "w": 16, "h": 16,
             "style": "body"},
            demo_g["orbit-group"],
        ],
    }
    redraw_kinetic_transform_experiment()

def stop_canvas_host_demo():
    If Tk Runtime's periodic callback is periodic_timer_callback:
        Set it to None.
    Clear demo_g's transform-group references.

def periodic_timer_callback():
    demo_g["orbit-angle"] = (demo_g["orbit-angle"] + 2) % 360
    demo_g["spin-angle"] = (demo_g["spin-angle"] + 9) % 360
    demo_g["counter-spin-angle"] = (demo_g["counter-spin-angle"] - 14) % 360
    demo_g["bob-phase"] = (demo_g["bob-phase"] + 0.08) % tau

    demo_g["orbit-group"]["angle"] = demo_g["orbit-angle"]
    demo_g["spin-group"]["angle"] = demo_g["spin-angle"]
    demo_g["counter-spin-group"]["angle"] = demo_g["counter-spin-angle"]
    redraw_kinetic_transform_experiment()

def redraw_kinetic_transform_experiment():
    canvas_host_window.g["canvas"].delete("all")

    bob_x = 20 * sin(demo_g["bob-phase"])
    bob_y = 12 * cos(demo_g["bob-phase"] * 2)
    Push a Transform Stack frame at 380 + bob_x, 270 + bob_y.
    try:
        canvas_context.draw("kinetic-transform-lab")
    finally:
        Drop the Transform Stack frame.
```

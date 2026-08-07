# Module — Canvas Host Window

The program is for developing Vector-Loom data modeling and basic
rendering.  The tk-runtime, app-shell, timer -- those modules are
the background host material.  This is the first module that's
actually dedicated to the specific application: A harness for testing,
demoing, and developing Vector-Loom.

Specifically, this module builds the Toplevel window that hosts the
Canvas that Vector-Loom will be developed in, and it also sets up the
specific demo material.


## Render Target

`canvas_host_window.py`

## OWNS

- The tkinter.Toplevel that contains the main Canvas.
- Creating and placing the main Canvas widget in that Toplevel.
- Any chrome widgets that help use and debug what is going on.
- The primary tick callback.
- Animation state and a disposable kinetic transform experiment using Canvas
  Context.

## READS

- Configuration data, potentially, in Tk Runtime.
- The Tk Runtime `g["root"]` value, on occasion.
- Canvas Context and Transform Stack when performing the kinetic transform
  experiment.

## WRITES

- Tk Runtime's `periodic-callback` during setup.
- Tk Runtime's `periodic-callback`, setting it to `None` when this window
  closes.
- The disposable Canvas between animation frames.

## CALLS

- Tkinter functions for creating and manipulating widgets.
- `canvas_context.set_canvas(canvas)` when starting the experiment.
- Transform Stack's `push_transform()` and `drop_transform()` through
  Canvas Context's shared render target.
- `canvas_context.draw(design_name)` for the kinetic transform experiment.
- The Canvas's `delete("all")` operation before each experimental redraw.

## MAY SAFELY ASSUME

- Canvas Context and Transform Stack are available and have disposable style,
  design, and transform state during this early proving-ground phase.

## ENSURES

- `create_canvas_host_window()` creates the Canvas Host Window and makes its
  Canvas available at `g["canvas"]`.
- `populate_canvas_context_and_start_kinetic_transform_experiment()` displays
  a transform laboratory centered in the Canvas.
- Every timer tick advances orbital, spin, counter-spin, and bobbing state,
  then redraws the laboratory.
- Closing the window unregisters the periodic callback before destroying the
  Canvas, so no later timer tick can target a destroyed Tk widget.
- The experiment is expressed through Canvas Context and Transform Stack rather
  than direct Canvas primitive calls from this module, apart from clearing the
  disposable Canvas between frames.

## DOES NOT OWN

- Anything about application setup outside of itself.
- Durable VectorLoom library data, document loading, saving, or validation.
- Canvas Context's drawing rules, Transform Stack's transform rules, or the
  meaning of their style and design registries.

## Sketch

```python
from math import cos, sin, tau


g = {
    "window": None,
    "canvas": None,
    "chrome": None,
    "status": None,
    "orbit-angle": 0,
    "spin-angle": 0,
    "counter-spin-angle": 0,
    "bob-phase": 0,
    "orbit-group": None,
    "spin-group": None,
    "counter-spin-group": None,
}


def periodic_timer_callback():
    g["orbit-angle"] = (g["orbit-angle"] + 2) % 360
    g["spin-angle"] = (g["spin-angle"] + 9) % 360
    g["counter-spin-angle"] = (g["counter-spin-angle"] - 14) % 360
    g["bob-phase"] = (g["bob-phase"] + 0.08) % tau

    g["orbit-group"]["angle"] = g["orbit-angle"]
    g["spin-group"]["angle"] = g["spin-angle"]
    g["counter-spin-group"]["angle"] = g["counter-spin-angle"]
    redraw_kinetic_transform_experiment()


def register_periodic_timer_callback():
    Set Tk Runtime's global periodic callback to periodic_timer_callback.


def create_canvas_host_window():
    note: use the grid packer

    Create the Toplevel.
    Give it the title "Experimental Vector-Loom Canvas".

    Put a Canvas at the top and make it at least 760x550 pixels in size.

    Put a Frame in a row beneath it. This will contain chrome in the future.
    Make a status bar at the bottom with "Canvas window created." as its
    initial text.

    Register close_canvas_host_window() for WM_DELETE_WINDOW.

    Store the Toplevel, Canvas, Frame, and status bar in g.


def close_canvas_host_window():
    Set Tk Runtime's periodic callback to None.
    Clear Canvas Host's stored window, Canvas, chrome, status, and experiment
    group references.
    Destroy the captured Toplevel.


def populate_canvas_context_and_start_kinetic_transform_experiment():
    Call canvas_context.set_canvas(g["canvas"]), giving Canvas Context
    ownership of drawing through that Canvas.

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

    g["orbit-group"] = {
        "type": "group", "id": "orbit", "angle": 0, "contents": []
    }
    g["spin-group"] = {
        "type": "group", "id": "spinner", "x": 150, "angle": 0,
        "contents": []
    }
    g["counter-spin-group"] = {
        "type": "group", "id": "counter-spinner", "angle": 0,
        "contents": [
            {"type": "line", "x1": -30, "y1": 0,
             "x2": 30, "y2": 0, "style": "counter-rotor"},
            {"type": "line", "x1": 0, "y1": -30,
             "x2": 0, "y2": 30, "style": "counter-rotor"},
        ],
    }
    g["spin-group"]["contents"] = [
        {"type": "rect", "x": -22, "y": -16, "w": 44, "h": 32,
         "style": "body"},
        {"type": "line", "x1": -45, "y1": 0,
         "x2": 45, "y2": 0, "style": "rotor"},
        {"type": "line", "x1": 0, "y1": -45,
         "x2": 0, "y2": 45, "style": "rotor"},
        g["counter-spin-group"],
    ]
    g["orbit-group"]["contents"] = [
        {"type": "line", "x1": 0, "y1": 0,
         "x2": 150, "y2": 0, "style": "arm"},
        g["spin-group"],
    ]
    canvas_context.designs["kinetic-transform-lab"] = {
        "contents": [
            {"type": "oval", "x": -150, "y": -150, "w": 300, "h": 300,
             "style": "orbit-guide"},
            {"type": "oval", "x": -8, "y": -8, "w": 16, "h": 16,
             "style": "body"},
            g["orbit-group"],
        ],
    }
    redraw_kinetic_transform_experiment()


def redraw_kinetic_transform_experiment():
    g["canvas"].delete("all")

    bob_x = 20 * sin(g["bob-phase"])
    bob_y = 12 * cos(g["bob-phase"] * 2)
    canvas_context.push_transform({"x": 380 + bob_x, "y": 270 + bob_y})
    try:
        canvas_context.draw("kinetic-transform-lab")
    finally:
        canvas_context.drop_transform()
```

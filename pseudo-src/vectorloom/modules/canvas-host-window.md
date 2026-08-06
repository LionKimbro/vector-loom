# Module — Canvas Host Window

This program is for developing Vector-Loom data modeling, and basic rendering.

This represents the Toplevel and the Canvas that will be used to present
the Vector-Loom data to the user.


## Render Target

`canvas_host_window.py`

## OWNS

- The tkinter.Toplevel that contains the main Canvas.
- Creating and placing the main Canvas widget in that Toplevel.
- Any chrome widgets that help use and debug what's going on.
- The primary tick callback
- Initial, disposable drawing experiments using Canvas Context.

## READS

- configuration data, potentially, in tk-runtime
- the tk-runtime g["root"] value, on occasion
- the current Canvas Context machine when performing a drawing experiment.

## WRITES

- directly to the tk-runtime's "periodic-callback", during setup

## CALLS

- tkinter functions for creating and manipulating widgets
- `canvas_context.set_canvas(canvas)` when starting its initial drawing
  experiment.
- `canvas_context.locate(x, y)` and `canvas_context.draw(drawing_name)` for
  initial drawing experiments.

## MAY SAFELY ASSUME

- Canvas Context is available and has an empty or disposable style and drawing
  registry during this early proving-ground phase.

## ENSURES

- `create_canvas_host_window()` creates the Canvas Host Window and makes its
  Canvas available at `g["canvas"]`.
- `populate_canvas_context_and_draw_initial_crosshair_experiment()` displays a
  simple X centered at `[50, 50]`.
- The experiment is expressed through Canvas Context rather than direct Canvas
  primitive calls from this module.

## DOES NOT OWN

- Anything about the setup, outside of itself.
- Durable VectorLoom library data, document loading, saving, or validation.
- Canvas Context's drawing rules or the meaning of its style and drawing
  registries.


## Sketch

```python
g = {
    "window": None,
    "canvas": None,
    "chrome": None,
    "status": None
}

def periodic_timer_callback():
    pass  # doesn't do anything, presently

def register_periodic_timer_callback():
    set the tk-runtime's global variable to periodic_timer_callback


def create_canvas_host_window():
    note: use the grid packer
    
    create the toplevel
    give it the title "Experimental Vector-Loom Canvas"

    put a Canvas at the top,
    make it at least 760x550 (px) in size.

    Put a Frame in a row beneath it,
    this will contain chrome in the future.
    (But right now, it's blank.)

    Make a status bar at the bottom.
    Put "Canvas window created." into it as the initial text.

    Store the Toplevel, Canvas, Frame, and status bar in g.

def populate_canvas_context_and_draw_initial_crosshair_experiment():
    Call canvas_context.set_canvas(g["canvas"]), giving Canvas Context
    ownership of drawing through that Canvas.

    For the initial disposable drawing experiment:
        canvas_context.styles["experiment-ink"] = {
            "stroke": "#222222",
            "width": 2
        }
        canvas_context.designs["experiment-x"] = {
            "contents": [
                {"type": "line", "x1": -20, "y1": -20,
                 "x2": 20, "y2": 20, "style": "experiment-ink"},
                {"type": "line", "x1": -20, "y1": 20,
                 "x2": 20, "y2": -20, "style": "experiment-ink"}
            ]
        }
        canvas_context.locate(50, 50)
        canvas_context.draw("experiment-x")
```

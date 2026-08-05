# Module — Canvas Host Window

This program is for developing Vector-Loom data modeling, and basic rendering.

This represents the Toplevel and the Canvas that will be used to present
the Vector-Loom data to the user.


## Render Target

`canvas_host_window.py`

## OWNS

- The tkinter.Toplevel that contains the main Canvas.
- The Canvas itself.
- Any chrome widgets that help use and debug what's going on.
- The primary tick callback

## READS

- configuration data, potentially, in tk-runtime
- the tk-runtime g["root"] value, on occasion
- the vectorloom data, wherever it is

## WRITES

- directly to the tk-runtime's "periodic-callback", during setup

## CALLS

- tkinter functions for creating and manipulating widgets

## MAY SAFELY ASSUME

## ENSURES

## DOES NOT OWN

- Anything about the setup, outside of itself.
- The data that is visualized within the Canvas.


## Sketch

```python

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
```

# Module — Canvas Host Window

This module is the physical home for Vector Loom's main Canvas. It creates and
maintains the Toplevel window and its supporting widgets, without deciding what
particular Vector Loom material the Canvas displays.

## Render Target

`canvas_host_window.py`

## OWNS

- The tkinter.Toplevel that contains the main Canvas.
- Creating, placing, and retaining the main Canvas widget.
- Chrome and status widgets that belong to the host window.
- The host window's close lifecycle and its generic close-callback seam.

## READS

- The Tk Runtime `g["root"]` value when creating the Toplevel.

## CALLS

- Tkinter functions for creating, placing, and destroying widgets.
- Its registered close callback, if a caller installed one.

## MAY SAFELY ASSUME

- A caller creates the host before asking an application-specific mechanism to
  use `g["canvas"]`.

## ENSURES

- `create_canvas_host_window()` creates the Canvas Host Window and makes its
  Canvas available at `g["canvas"]`.
- Closing the host calls the registered close callback before destroying the
  window, so a user of the Canvas can clean up its own runtime work.

## DOES NOT OWN

- Application setup outside of itself.
- The drawing, animation, or experiment currently displayed on the Canvas.
- Timer callback meaning or registration.
- Canvas Context's drawing rules, Transform Stack's transform rules, or
  durable VectorLoom library data.

## Sketch

```python
g = {
    "window": None,
    "canvas": None,
    "chrome": None,
    "status": None,
    "close-callback": None
}

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

def set_close_callback(callback):
    Set g["close-callback"] to callback.

def close_canvas_host_window():
    Capture g["window"] and g["close-callback"].
    If the callback exists, call it before destroying the window.
    Clear Canvas Host's stored widget references and close callback.
    Destroy the captured Toplevel.
```

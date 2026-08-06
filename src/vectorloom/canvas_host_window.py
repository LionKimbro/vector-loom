"""The visible Vector-Loom Canvas host and kinetic transform experiment."""

from math import cos, sin, tau
import tkinter as tk

from . import canvas_context
from . import tk_runtime


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
    """Advance and redraw the disposable kinetic transform experiment."""
    g["orbit-angle"] = (g["orbit-angle"] + 2) % 360
    g["spin-angle"] = (g["spin-angle"] + 9) % 360
    g["counter-spin-angle"] = (g["counter-spin-angle"] - 14) % 360
    g["bob-phase"] = (g["bob-phase"] + 0.08) % tau

    g["orbit-group"]["angle"] = g["orbit-angle"]
    g["spin-group"]["angle"] = g["spin-angle"]
    g["counter-spin-group"]["angle"] = g["counter-spin-angle"]
    redraw_kinetic_transform_experiment()


def register_periodic_timer_callback():
    """Install this window's timer callback into the shared Tk runtime."""
    tk_runtime.g["periodic-callback"] = periodic_timer_callback


def create_canvas_host_window():
    """Create the Toplevel, Canvas, chrome row, and status bar."""
    window = tk.Toplevel(tk_runtime.g["root"])
    window.title("Experimental Vector-Loom Canvas")
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    canvas = tk.Canvas(window, width=760, height=550)
    canvas.grid(row=0, column=0, sticky="nsew")

    chrome = tk.Frame(window)
    chrome.grid(row=1, column=0, sticky="ew")

    status = tk.Label(window, anchor="w", text="Canvas window created.")
    status.grid(row=2, column=0, sticky="ew")
    window.protocol("WM_DELETE_WINDOW", close_canvas_host_window)

    g.update({
        "window": window,
        "canvas": canvas,
        "chrome": chrome,
        "status": status,
    })


def close_canvas_host_window():
    """Stop host animation before destroying its Canvas-owning window."""
    tk_runtime.g["periodic-callback"] = None
    window = g["window"]
    g.update({
        "window": None,
        "canvas": None,
        "chrome": None,
        "status": None,
        "orbit-group": None,
        "spin-group": None,
        "counter-spin-group": None,
    })
    if window is not None:
        window.destroy()


def populate_canvas_context_and_start_kinetic_transform_experiment():
    """Install and start an animated test of nested local transforms."""
    canvas_context.set_canvas(g["canvas"])
    canvas_context.styles.update({
        "orbit-guide": {"stroke": "#8a8a8a", "width": 1, "dash": "4 4"},
        "arm": {"stroke": "#315f97", "width": 3},
        "body": {"stroke": "#182c44", "fill": "#83c5e8", "width": 2},
        "rotor": {"stroke": "#9e3d3d", "width": 3},
        "counter-rotor": {"stroke": "#4d8c51", "width": 2},
    })

    orbit_group = {"type": "group", "id": "orbit", "angle": 0, "contents": []}
    spin_group = {
        "type": "group",
        "id": "spinner",
        "x": 150,
        "angle": 0,
        "contents": [],
    }
    counter_spin_group = {
        "type": "group",
        "id": "counter-spinner",
        "angle": 0,
        "contents": [
            {"type": "line", "x1": -30, "y1": 0, "x2": 30, "y2": 0, "style": "counter-rotor"},
            {"type": "line", "x1": 0, "y1": -30, "x2": 0, "y2": 30, "style": "counter-rotor"},
        ],
    }
    spin_group["contents"] = [
        {"type": "rect", "x": -22, "y": -16, "w": 44, "h": 32, "style": "body"},
        {"type": "line", "x1": -45, "y1": 0, "x2": 45, "y2": 0, "style": "rotor"},
        {"type": "line", "x1": 0, "y1": -45, "x2": 0, "y2": 45, "style": "rotor"},
        counter_spin_group,
    ]
    orbit_group["contents"] = [
        {"type": "line", "x1": 0, "y1": 0, "x2": 150, "y2": 0, "style": "arm"},
        spin_group,
    ]
    canvas_context.designs["kinetic-transform-lab"] = {
        "contents": [
            {"type": "oval", "x": -150, "y": -150, "w": 300, "h": 300, "style": "orbit-guide"},
            {"type": "oval", "x": -8, "y": -8, "w": 16, "h": 16, "style": "body"},
            orbit_group,
        ],
    }
    g.update({
        "orbit-angle": 0,
        "spin-angle": 0,
        "counter-spin-angle": 0,
        "bob-phase": 0,
        "orbit-group": orbit_group,
        "spin-group": spin_group,
        "counter-spin-group": counter_spin_group,
    })
    redraw_kinetic_transform_experiment()


def redraw_kinetic_transform_experiment():
    """Clear and draw one kinetic-transform animation frame."""
    g["canvas"].delete("all")
    bob_x = 20 * sin(g["bob-phase"])
    bob_y = 12 * cos(g["bob-phase"] * 2)
    canvas_context.push_transform({"x": 380 + bob_x, "y": 270 + bob_y})
    try:
        canvas_context.draw("kinetic-transform-lab")
    finally:
        canvas_context.drop_transform()

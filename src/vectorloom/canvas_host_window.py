"""The initial visible Vector Loom Canvas host window."""

import tkinter as tk

from . import tk_runtime


g = {
    "window": None,
    "canvas": None,
    "chrome": None,
    "status": None,
}


def periodic_timer_callback():
    """Advance the Canvas host's future interaction cycle.

    The initial proving-ground window has no continuous behavior yet.
    """


def register_periodic_timer_callback():
    """Install this window's timer callback into the shared Tk runtime."""
    tk_runtime.g["periodic-callback"] = periodic_timer_callback


def create_canvas_host_window():
    """Create the initial Toplevel, Canvas, chrome row, and status bar."""
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

    g.update({
        "window": window,
        "canvas": canvas,
        "chrome": chrome,
        "status": status,
    })

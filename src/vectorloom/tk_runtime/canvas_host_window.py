"""The visible Canvas host window for Vector Loom-owned applications."""

import tkinter as tk

from . import tk_runtime


g = {
    "window": None,
    "canvas": None,
    "chrome": None,
    "status": None,
    "close-callback": None,
}


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
    canvas.bind("<Button-1>", handle_when_user_clicks_canvas_for_tag_inspection)
    window.protocol("WM_DELETE_WINDOW", close_canvas_host_window)
    g.update({"window": window, "canvas": canvas, "chrome": chrome, "status": status})


def handle_when_user_clicks_canvas_for_tag_inspection(event):
    """Display the clicked Canvas item's tags in the host status bar."""
    item_ids = g["canvas"].find_withtag("current")
    if not item_ids:
        g["status"].configure(text="No Canvas item under pointer.")
        return
    tags = g["canvas"].gettags(item_ids[0])
    if not tags:
        g["status"].configure(text="Canvas item has no tags.")
        return
    g["status"].configure(text=" | ".join(tags))


def set_close_callback(callback):
    """Set the callback run before this host destroys its Canvas."""
    g["close-callback"] = callback


def close_canvas_host_window():
    """Run cleanup, clear retained widgets, then destroy the host window."""
    window = g["window"]
    callback = g["close-callback"]
    if callback is not None:
        callback()
    g.update({"window": None, "canvas": None, "chrome": None, "status": None, "close-callback": None})
    if window is not None:
        window.destroy()

"""The shared Tk runtime machine for Vector Loom."""

import time
import tkinter as tk


g = {
    "root": None,
    "periodic-callback": None,
}

config = {
    "quit-when-no-toplevels-remain": True,
    "periodic-timer-interval-in-ms": 50,
}


def reset():
    """Restore the Tk runtime's initial state without rebinding its bundles."""
    g.update({
        "root": None,
        "periodic-callback": None,
    })
    config.update({
        "quit-when-no-toplevels-remain": True,
        "periodic-timer-interval-in-ms": 50,
    })


def create_and_withdraw_root():
    """Create the hidden Tk root that owns Vector Loom's Toplevel windows."""
    g["root"] = tk.Tk()
    g["root"].withdraw()


def has_active_toplevels():
    """Return whether the root currently has a live direct Toplevel child."""
    return any(
        isinstance(widget, tk.Toplevel) and widget.winfo_exists()
        for widget in g["root"].winfo_children()
    )


def now_ms():
    """Return a monotonic timestamp suitable for Tk callback adapters."""
    return int(time.monotonic() * 1000)


def perform_periodic_callback_per_timer():
    """Run the current application callback, if application setup installed one."""
    callback = g["periodic-callback"]
    if callback is not None:
        callback()

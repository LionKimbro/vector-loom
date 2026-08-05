"""Recurring Tk timer machine."""

from . import tk_runtime


g = {
    "timer-handle": None,
}


def start_timer():
    """Start or replace the recurring timer."""
    if g["timer-handle"] is not None:
        cancel_timer()
    _schedule_next()


def cancel_timer():
    """Cancel the scheduled callback.

    Calling this without a valid timer handle is a programmer error.  The Tk
    call is deliberately unguarded so the error remains visible.
    """
    tk_runtime.g["root"].after_cancel(g["timer-handle"])
    g["timer-handle"] = None


def _on_timer():
    g["timer-handle"] = None
    tk_runtime.perform_periodic_callback_per_timer()

    if tk_runtime.config["quit-when-no-toplevels-remain"]:
        if not tk_runtime.has_active_toplevels():
            tk_runtime.g["root"].quit()
            return

    _schedule_next()


def _schedule_next():
    interval = tk_runtime.config["periodic-timer-interval-in-ms"]
    g["timer-handle"] = tk_runtime.g["root"].after(interval, _on_timer)

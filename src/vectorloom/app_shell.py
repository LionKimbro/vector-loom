"""Application composition for the initial Vector Loom runtime."""

from . import canvas_host_window
from . import timer
from . import tk_runtime


def main():
    """Compose Vector Loom, then enter Tk's event loop."""
    tk_runtime.create_and_withdraw_root()
    timer.start_timer()
    _perform_app_specific_setup()
    tk_runtime.g["root"].mainloop()


def _perform_app_specific_setup():
    """Install the first Canvas host window and its periodic callback."""
    canvas_host_window.register_periodic_timer_callback()
    canvas_host_window.create_canvas_host_window()
    canvas_host_window.populate_canvas_context_and_start_kinetic_transform_experiment()

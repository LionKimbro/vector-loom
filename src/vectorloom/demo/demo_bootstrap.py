"""Application composition for the current Vector Loom demonstration."""

from ..tk_runtime import app_shell, canvas_host_window
from . import canvas_host_demo


def main():
    """Configure and start the kinetic Canvas demonstration."""
    app_shell.config["app-specific-setup"] = set_up_demo_application
    app_shell.main()


def set_up_demo_application():
    """Create the demo host, then install its Canvas drawing experiment."""
    canvas_host_window.create_canvas_host_window()
    canvas_host_demo.start_canvas_host_demo()

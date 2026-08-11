"""Application composition for the Vector Loom editor."""

from ..tk_runtime import app_shell
from ..tk_runtime import tk_runtime
from . import editor_window
from . import interaction_runtime


def main():
    """Configure and start the Vector Loom editor application."""
    app_shell.config["app-specific-setup"] = set_up_editor_application
    app_shell.main()


def set_up_editor_application():
    """Create the editor window and install its CIRA update cycle."""
    editor_window.create_editor_window()
    interaction_runtime.initialize_editor_runtime()
    tk_runtime.g["periodic-callback"] = interaction_runtime.run_update_cycle

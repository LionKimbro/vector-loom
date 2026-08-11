"""Shared startup shell for Vector Loom's own Tkinter applications."""

from . import timer
from . import tk_runtime


config = {
    "app-specific-setup": None,
}


def main():
    """Start the application configured in this App Shell's config bundle."""
    app_specific_setup = config["app-specific-setup"]
    if app_specific_setup is None:
        raise RuntimeError(
            "App Shell needs config['app-specific-setup'] before main()."
        )
    tk_runtime.create_and_withdraw_root()
    app_specific_setup()
    timer.start_timer()
    tk_runtime.g["root"].mainloop()

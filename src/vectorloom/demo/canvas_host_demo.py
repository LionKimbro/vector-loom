"""The kinetic transform proving-ground demonstration."""

from math import cos, sin, tau

from ..canvas import canvas_context, transform_stack
from ..tk_runtime import canvas_host_window, tk_runtime


g = {
    "orbit-angle": 0,
    "spin-angle": 0,
    "counter-spin-angle": 0,
    "bob-phase": 0,
    "orbit-group": None,
    "spin-group": None,
    "counter-spin-group": None,
}


def start_canvas_host_demo():
    """Install the kinetic drawing experiment into the existing Canvas host."""
    canvas_host_window.set_close_callback(stop_canvas_host_demo)
    tk_runtime.g["periodic-callback"] = periodic_timer_callback
    canvas_context.set_canvas(canvas_host_window.g["canvas"])
    canvas_context.styles.update({
        "orbit-guide": {"stroke": "#8a8a8a", "width": 1, "dash": "4 4"},
        "arm": {"stroke": "#315f97", "width": 3},
        "body": {"stroke": "#182c44", "fill": "#83c5e8", "width": 2},
        "rotor": {"stroke": "#9e3d3d", "width": 3},
        "counter-rotor": {"stroke": "#4d8c51", "width": 2},
    })
    _build_kinetic_transform_design()
    redraw_kinetic_transform_experiment()


def stop_canvas_host_demo():
    """Unregister this demo and clear its disposable drawing state."""
    if tk_runtime.g["periodic-callback"] is periodic_timer_callback:
        tk_runtime.g["periodic-callback"] = None
    g.update({"orbit-group": None, "spin-group": None, "counter-spin-group": None})


def _build_kinetic_transform_design():
    orbit_group = {"type": "group", "id": "orbit", "angle": 0, "contents": []}
    spin_group = {"type": "group", "id": "spinner", "x": 150, "angle": 0, "contents": []}
    counter_spin_group = {
        "type": "group", "id": "counter-spinner", "angle": 0,
        "contents": [
            {"type": "line", "x1": -30, "y1": 0, "x2": 30, "y2": 0, "style": "counter-rotor"},
            {"type": "line", "x1": 0, "y1": -30, "x2": 0, "y2": 30, "style": "counter-rotor"},
        ],
    }
    spin_group["contents"] = [
        {"id": "body", "type": "rect", "x": -22, "y": -16, "w": 44, "h": 32, "style": "body"},
        {"type": "line", "x1": -45, "y1": 0, "x2": 45, "y2": 0, "style": "rotor"},
        {"type": "line", "x1": 0, "y1": -45, "x2": 0, "y2": 45, "style": "rotor"},
        counter_spin_group,
    ]
    orbit_group["contents"] = [
        {"type": "line", "x1": 0, "y1": 0, "x2": 150, "y2": 0, "style": "arm"}, spin_group,
    ]
    canvas_context.designs["kinetic-transform-lab"] = {
        "contents": [
            {"id": "orbit-guide", "type": "oval", "x": -150, "y": -150, "w": 300, "h": 300, "style": "orbit-guide"},
            {"type": "oval", "x": -8, "y": -8, "w": 16, "h": 16, "style": "body"}, orbit_group,
        ],
    }
    g.update({"orbit-angle": 0, "spin-angle": 0, "counter-spin-angle": 0, "bob-phase": 0,
              "orbit-group": orbit_group, "spin-group": spin_group, "counter-spin-group": counter_spin_group})


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


def redraw_kinetic_transform_experiment():
    """Clear and draw one kinetic-transform animation frame."""
    canvas_host_window.g["canvas"].delete("all")
    bob_x = 20 * sin(g["bob-phase"])
    bob_y = 12 * cos(g["bob-phase"] * 2)
    transform_stack.push_transform({"x": 380 + bob_x, "y": 270 + bob_y})
    try:
        canvas_context.draw("kinetic-transform-lab")
    finally:
        transform_stack.drop_transform()

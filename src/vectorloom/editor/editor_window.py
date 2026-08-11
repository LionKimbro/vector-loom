"""The physical three-pane Tk window for the Vector Loom editor."""

import tkinter as tk
from tkinter import ttk

from ..tk_runtime import tk_runtime
from . import event_queue


TOOL_SPECS = (
    ("select", "[s]", "Select items."),
    ("line", "[L]", "Draw lines."),
    ("rectangle", "[R]", "Draw rectangles."),
    ("oval", "[O]", "Draw ovals."),
    ("polyline", "[P]", "Draw polylines."),
    ("text", "[T]", "Draw text."),
    ("group", "[g]", "Draw groups."),
    ("connector", "[c]", "Draw connectors."),
)


widgets = {
    "window": None,
    "pane-row": None,
    "library-pane": None,
    "designs-frame": None,
    "designs-tree": None,
    "styles-frame": None,
    "styles-tree": None,
    "canvas-pane": None,
    "tools-frame": None,
    "canvas": None,
    "inspector-pane": None,
    "inspector-frame": None,
    "status": None,
}

tool_buttons = {}
tooltip = {"window": None}


def create_editor_window():
    """Create the empty editor window and install its raw-input adapters."""
    window = tk.Toplevel(tk_runtime.g["root"])
    window.title("Vector Loom Editor")
    window.minsize(1000, 650)
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)
    widgets["window"] = window
    create_three_panes(window)
    create_status_bar(window)
    register_thin_input_handlers()


def create_three_panes(window):
    """Create the adjustable library, Canvas, and inspector panes."""
    pane_row = ttk.Panedwindow(window, orient="horizontal")
    pane_row.grid(row=0, column=0, sticky="nsew")
    widgets["pane-row"] = pane_row
    create_library_pane(pane_row)
    create_canvas_pane(pane_row)
    create_inspector_pane(pane_row)


def create_library_pane(pane_row):
    """Create the left pane containing the Designs and Styles controls."""
    library_pane = ttk.Frame(pane_row, padding=6)
    library_pane.columnconfigure(0, weight=1)
    library_pane.rowconfigure(0, weight=1)
    library_pane.rowconfigure(1, weight=1)
    pane_row.add(library_pane, weight=1)
    widgets["library-pane"] = library_pane
    create_designs_tree(library_pane)
    create_styles_tree(library_pane)


def create_designs_tree(library_pane):
    """Create the empty Designs Treeview in the upper library region."""
    designs_frame = ttk.LabelFrame(library_pane, text="Designs", padding=4)
    designs_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 3))
    designs_frame.rowconfigure(0, weight=1)
    designs_frame.columnconfigure(0, weight=1)
    designs_tree = ttk.Treeview(designs_frame, show="tree")
    designs_tree.grid(row=0, column=0, sticky="nsew")
    widgets["designs-frame"] = designs_frame
    widgets["designs-tree"] = designs_tree


def create_styles_tree(library_pane):
    """Create the empty Styles Treeview in the lower library region."""
    styles_frame = ttk.LabelFrame(library_pane, text="Styles", padding=4)
    styles_frame.grid(row=1, column=0, sticky="nsew", pady=(3, 0))
    styles_frame.rowconfigure(0, weight=1)
    styles_frame.columnconfigure(0, weight=1)
    styles_tree = ttk.Treeview(styles_frame, show="tree")
    styles_tree.grid(row=0, column=0, sticky="nsew")
    widgets["styles-frame"] = styles_frame
    widgets["styles-tree"] = styles_tree


def create_canvas_pane(pane_row):
    """Create the center black drawing Canvas."""
    canvas_pane = ttk.Frame(pane_row, padding=6)
    canvas_pane.rowconfigure(0, weight=1)
    canvas_pane.columnconfigure(1, weight=1)
    pane_row.add(canvas_pane, weight=3)
    tools_frame = ttk.Frame(canvas_pane)
    tools_frame.grid(row=0, column=0, sticky="ns", padx=(0, 6))
    widgets["tools-frame"] = tools_frame
    create_drawing_tool_buttons(tools_frame)
    canvas = tk.Canvas(canvas_pane, background="black", highlightthickness=0)
    canvas.grid(row=0, column=1, sticky="nsew")
    widgets["canvas-pane"] = canvas_pane
    widgets["canvas"] = canvas


def create_drawing_tool_buttons(tools_frame):
    """Create the direct-semantic drawing-tool controls."""
    tool_buttons.clear()
    for row, (tool_name, label, description) in enumerate(TOOL_SPECS):
        button = ttk.Button(
            tools_frame,
            text=label,
            command=lambda selected_tool=tool_name: handle_drawing_tool_button(
                selected_tool,
            ),
        )
        button.grid(row=row, column=0, sticky="ew", pady=(0, 3))
        button.bind(
            "<Enter>",
            lambda event, text=description: show_tooltip(event.widget, text),
        )
        button.bind("<Leave>", hide_tooltip)
        tool_buttons[tool_name] = button


def handle_drawing_tool_button(tool_name):
    """Post a direct semantic request to make one tool active."""
    from . import interaction_runtime

    interaction_runtime.post_semantic_event({
        "type": "SET_ACTIVE_TOOL",
        "tool": tool_name,
    })


def show_tooltip(widget, text):
    """Display a small tooltip immediately beside a drawing-tool button."""
    hide_tooltip()
    window = tk.Toplevel(widget)
    window.overrideredirect(True)
    x = widget.winfo_rootx() + widget.winfo_width() + 6
    y = widget.winfo_rooty()
    window.geometry(f"+{x}+{y}")
    ttk.Label(window, text=text, padding=(4, 2)).grid()
    tooltip["window"] = window


def hide_tooltip(event=None):
    """Remove the currently shown drawing-tool tooltip, if any."""
    window = tooltip["window"]
    tooltip["window"] = None
    if window is not None:
        window.destroy()


def create_inspector_pane(pane_row):
    """Create the right pane whose contents Projection will later own."""
    inspector_pane = ttk.Frame(pane_row, padding=6)
    inspector_pane.rowconfigure(0, weight=1)
    inspector_pane.columnconfigure(0, weight=1)
    pane_row.add(inspector_pane, weight=1)
    inspector_frame = ttk.Frame(inspector_pane)
    inspector_frame.grid(row=0, column=0, sticky="nsew")
    widgets["inspector-pane"] = inspector_pane
    widgets["inspector-frame"] = inspector_frame


def create_status_bar(window):
    """Create the status-bar surface whose text Projection will later set."""
    status = ttk.Label(window, anchor="w", text="Editor window created.")
    status.grid(row=1, column=0, sticky="ew")
    widgets["status"] = status


def register_thin_input_handlers():
    """Bind Tk activity to callbacks that post raw facts and nothing else."""
    canvas = widgets["canvas"]
    window = widgets["window"]
    designs_tree = widgets["designs-tree"]
    styles_tree = widgets["styles-tree"]
    canvas.bind("<Motion>", handle_pointer_motion)
    canvas.bind("<ButtonPress-1>", handle_button_1_press)
    canvas.bind("<ButtonRelease-1>", handle_button_1_release)
    canvas.bind("<Leave>", handle_pointer_leave)
    window.bind("<KeyPress>", handle_key_press)
    window.bind("<KeyRelease>", handle_key_release)
    designs_tree.bind("<<TreeviewSelect>>", handle_designs_tree_selection)
    styles_tree.bind("<<TreeviewSelect>>", handle_styles_tree_selection)
    window.protocol("WM_DELETE_WINDOW", handle_window_close_request)


def handle_pointer_motion(event):
    """Post the current Canvas-pointer location as a raw motion fact."""
    event_queue.post_pointer_motion(event.x, event.y, tk_runtime.now_ms())


def handle_button_1_press(event):
    """Post a raw primary-button press at the Canvas location."""
    event_queue.post_event({
        "type": "BUTTON_1_PRESSED",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_button_1_release(event):
    """Post a raw primary-button release at the Canvas location."""
    event_queue.post_event({
        "type": "BUTTON_1_RELEASED",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_pointer_leave(event):
    """Post the last Canvas location when the pointer leaves the Canvas."""
    event_queue.post_event({
        "type": "POINTER_LEFT_CANVAS",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_key_press(event):
    """Post a raw keyboard press without interpreting its meaning."""
    event_queue.post_event({
        "type": "KEY_PRESSED",
        "keysym": event.keysym,
        "char": event.char,
        "ms": tk_runtime.now_ms(),
    })


def handle_key_release(event):
    """Post a raw keyboard release without interpreting its meaning."""
    event_queue.post_event({
        "type": "KEY_RELEASED",
        "keysym": event.keysym,
        "char": event.char,
        "ms": tk_runtime.now_ms(),
    })


def handle_designs_tree_selection(event):
    """Post the physical Designs Treeview selection as a raw fact."""
    post_tree_selection_change("designs-tree")


def handle_styles_tree_selection(event):
    """Post the physical Styles Treeview selection as a raw fact."""
    post_tree_selection_change("styles-tree")


def post_tree_selection_change(tree_name):
    """Post the selected physical item identifiers from one library Treeview."""
    tree = widgets[tree_name]
    event_queue.post_event({
        "type": "TREE_SELECTION_CHANGED",
        "tree": tree_name,
        "item-iids": list(tree.selection()),
        "ms": tk_runtime.now_ms(),
    })


def handle_inspector_widget_activated(widget_name, value):
    """Post a future inspector-control activation without acting on it."""
    event_queue.post_event({
        "type": "WIDGET_ACTIVATED",
        "widget": widget_name,
        "value": value,
        "ms": tk_runtime.now_ms(),
    })


def handle_window_close_request():
    """Post the already-semantic editor exit request to the discrete queue."""
    from . import interaction_runtime

    interaction_runtime.post_semantic_event({"type": "EXIT_EDITOR"})


def destroy_editor_window():
    """Destroy the editor Toplevel after the runtime routes its close effect."""
    window = widgets["window"]
    hide_tooltip()
    tool_buttons.clear()
    widgets.update({
        "window": None,
        "pane-row": None,
        "library-pane": None,
        "designs-frame": None,
        "designs-tree": None,
        "styles-frame": None,
        "styles-tree": None,
        "canvas-pane": None,
        "tools-frame": None,
        "canvas": None,
        "inspector-pane": None,
        "inspector-frame": None,
        "status": None,
    })
    if window is not None:
        window.destroy()

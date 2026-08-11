# Module — Editor Window

This module owns the editor's physical Tk window and its three-pane layout. It
creates empty control surfaces and translates toolkit activity into raw input
records; Projection later owns the rows, Canvas drawing, and inspector
contents shown inside those controls.

## Render Target

`src/vectorloom/editor/editor_window.py`

## OWNS

- The editor Toplevel and its widget handles.
- The left library pane, center Canvas pane, and right inspector pane.
- The two library Treeview controls: Designs above Styles.
- Tk bindings and thin callback adapters for Canvas, tree, inspector, and
  window keyboard input.
- A bottom status-bar widget reserved for structural and transient messages.

## CALLS

- `event_queue` posting operations.
- `tk_runtime.now_ms()` while creating time-bearing raw input records.

## ENSURES

- The visible editor window is a `tkinter.Toplevel` owned by the hidden Tk
  root.
- The Canvas background is black.
- The left library pane places the Designs Treeview above the Styles Treeview.
- Tk callbacks post raw facts only; they do not select items, mutate the
  library, interpret gestures, or render projection.

## DOES NOT OWN

- Tree rows, Canvas drawing, inspector values, or status meaning.  Projection
  owns those visible manifestations.
- RAW state, tokenization, semantic events, editor selection, focal address,
  durable library data, or Canvas projection.

## Widget Registers

```python
widgets = {
    "window": None,
    "pane-row": None,
    "library-pane": None,
    "designs-frame": None,
    "designs-tree": None,
    "styles-frame": None,
    "styles-tree": None,
    "canvas-pane": None,
    "canvas": None,
    "inspector-pane": None,
    "inspector-frame": None,
    "status": None,
}
```

The Treeview item identifiers and their displayed rows belong to Projection.
Editor Window retains only the Treeview widget handles.

## Layout

```text
┌────────────── Library ──────────────┬──────── Canvas ────────┬── Inspector ──┐
│ Designs                             │                        │               │
│ ┌─────────────────────────────────┐ │                        │               │
│ │ ttk.Treeview                    │ │     tkinter.Canvas     │ tkinter.Frame │
│ └─────────────────────────────────┘ │   black background      │               │
│ Styles                              │                        │               │
│ ┌─────────────────────────────────┐ │                        │               │
│ │ ttk.Treeview                    │ │                        │               │
│ └─────────────────────────────────┘ │                        │               │
└─────────────────────────────────────┴────────────────────────┴───────────────┘
┌──────────────────────────────────── status bar ──────────────────────────────┐
└──────────────────────────────────────────────────────────────────────────────┘
```

The three horizontal panes use a `ttk.Panedwindow`, so the user may adjust
their widths.  The library pane uses grid rows with equal expanding weight for
its Designs and Styles regions.

## Sketch

```python
def create_editor_window():
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
    pane_row = ttk.Panedwindow(window, orient="horizontal")
    pane_row.grid(row=0, column=0, sticky="nsew")
    widgets["pane-row"] = pane_row

    create_library_pane(pane_row)
    create_canvas_pane(pane_row)
    create_inspector_pane(pane_row)


def create_library_pane(pane_row):
    library_pane = ttk.Frame(pane_row, padding=6)
    library_pane.columnconfigure(0, weight=1)
    library_pane.rowconfigure(0, weight=1)
    library_pane.rowconfigure(1, weight=1)
    pane_row.add(library_pane, weight=1)
    widgets["library-pane"] = library_pane

    create_designs_tree(library_pane)
    create_styles_tree(library_pane)


def create_designs_tree(library_pane):
    designs_frame = ttk.LabelFrame(library_pane, text="Designs", padding=4)
    designs_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 3))
    designs_frame.rowconfigure(0, weight=1)
    designs_frame.columnconfigure(0, weight=1)

    designs_tree = ttk.Treeview(designs_frame, show="tree")
    designs_tree.grid(row=0, column=0, sticky="nsew")
    widgets["designs-frame"] = designs_frame
    widgets["designs-tree"] = designs_tree


def create_styles_tree(library_pane):
    styles_frame = ttk.LabelFrame(library_pane, text="Styles", padding=4)
    styles_frame.grid(row=1, column=0, sticky="nsew", pady=(3, 0))
    styles_frame.rowconfigure(0, weight=1)
    styles_frame.columnconfigure(0, weight=1)

    styles_tree = ttk.Treeview(styles_frame, show="tree")
    styles_tree.grid(row=0, column=0, sticky="nsew")
    widgets["styles-frame"] = styles_frame
    widgets["styles-tree"] = styles_tree


def create_canvas_pane(pane_row):
    canvas_pane = ttk.Frame(pane_row, padding=6)
    canvas_pane.rowconfigure(0, weight=1)
    canvas_pane.columnconfigure(0, weight=1)
    pane_row.add(canvas_pane, weight=3)

    canvas = tk.Canvas(
        canvas_pane,
        background="black",
        highlightthickness=0,
    )
    canvas.grid(row=0, column=0, sticky="nsew")
    widgets["canvas-pane"] = canvas_pane
    widgets["canvas"] = canvas


def create_inspector_pane(pane_row):
    inspector_pane = ttk.Frame(pane_row, padding=6)
    inspector_pane.rowconfigure(0, weight=1)
    inspector_pane.columnconfigure(0, weight=1)
    pane_row.add(inspector_pane, weight=1)

    inspector_frame = ttk.Frame(inspector_pane)
    inspector_frame.grid(row=0, column=0, sticky="nsew")
    widgets["inspector-pane"] = inspector_pane
    widgets["inspector-frame"] = inspector_frame


def create_status_bar(window):
    status = ttk.Label(window, anchor="w", text="Editor window created.")
    status.grid(row=1, column=0, sticky="ew")
    widgets["status"] = status


def register_thin_input_handlers():
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
    event_queue.post_pointer_motion(event.x, event.y, tk_runtime.now_ms())


def handle_button_1_press(event):
    event_queue.post_event({
        "type": "BUTTON_1_PRESSED",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_button_1_release(event):
    event_queue.post_event({
        "type": "BUTTON_1_RELEASED",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_pointer_leave(event):
    event_queue.post_event({
        "type": "POINTER_LEFT_CANVAS",
        "x": event.x,
        "y": event.y,
        "ms": tk_runtime.now_ms(),
    })


def handle_key_press(event):
    event_queue.post_event({
        "type": "KEY_PRESSED",
        "keysym": event.keysym,
        "char": event.char,
        "ms": tk_runtime.now_ms(),
    })


def handle_key_release(event):
    event_queue.post_event({
        "type": "KEY_RELEASED",
        "keysym": event.keysym,
        "char": event.char,
        "ms": tk_runtime.now_ms(),
    })


def handle_designs_tree_selection(event):
    post_tree_selection_change("designs-tree")


def handle_styles_tree_selection(event):
    post_tree_selection_change("styles-tree")


def post_tree_selection_change(tree_name):
    tree = widgets[tree_name]
    event_queue.post_event({
        "type": "TREE_SELECTION_CHANGED",
        "tree": tree_name,
        "item-iids": list(tree.selection()),
        "ms": tk_runtime.now_ms(),
    })


def handle_inspector_widget_activated(widget_name, value):
    event_queue.post_event({
        "type": "WIDGET_ACTIVATED",
        "widget": widget_name,
        "value": value,
        "ms": tk_runtime.now_ms(),
    })


def handle_window_close_request():
    event_queue.post_event({
        "type": "WINDOW_CLOSE_REQUESTED",
        "window": "editor",
        "ms": tk_runtime.now_ms(),
    })
```

## Projection Seam

Projection later performs these operations against the stored widget handles:

```text
replace Designs Treeview rows from the World Model's designs
replace Styles Treeview rows from the World Model's styles
draw the focal design and editor overlays on Canvas
replace inspector-frame contents for committed selection
set status-bar text and presentation
```

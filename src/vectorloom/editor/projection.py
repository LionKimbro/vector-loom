"""Visible projection for the Vector Loom editor."""

from tkinter import ttk

from . import editor_window
from . import event_queue
from . import world_model


def project():
    """Refresh the editor's temporary library and input diagnostic views."""
    if editor_window.widgets["window"] is None:
        return
    _project_library_trees()
    project_temporary_input_queue_diagnostic()


def _project_library_trees():
    library = world_model.g.get("library")
    if library is None:
        library = {}

    _replace_tree_rows(
        editor_window.widgets["designs-tree"],
        library.get("designs", {}),
        "design",
    )
    _replace_tree_rows(
        editor_window.widgets["styles-tree"],
        library.get("styles", {}),
        "style",
    )


def _replace_tree_rows(tree, entries, entry_kind):
    child_iids = tree.get_children()
    if child_iids:
        tree.delete(*child_iids)

    if isinstance(entries, dict):
        names = entries.keys()
    else:
        names = ()

    if not names:
        tree.insert(
            "",
            "end",
            iid=f"{entry_kind}:empty",
            text=f"(no {entry_kind}s loaded)",
        )
        return

    for name in names:
        tree.insert("", "end", iid=f"{entry_kind}:{name}", text=str(name))


def project_temporary_input_queue_diagnostic():
    """Show recently drained raw records until the real inspector exists."""
    inspector_frame = editor_window.widgets["inspector-frame"]
    for child in inspector_frame.winfo_children():
        child.destroy()

    ttk.Label(inspector_frame, text="Recent raw input").grid(
        row=0,
        column=0,
        sticky="w",
    )

    for index, event in enumerate(event_queue.recent_events[-10:], start=1):
        ttk.Label(
            inspector_frame,
            anchor="w",
            justify="left",
            text=_compact_event_text(event),
        ).grid(row=index, column=0, sticky="ew")


def _compact_event_text(event):
    text = repr(event)
    if len(text) > 120:
        return f"{text[:117]}..."
    return text

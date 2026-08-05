"""Vector Loom editor: a CIRA-structured structural editor hosted on TkVillage.

Modules map to CIRA subsystems:
    continuity  - Continuity Engine (RAW, tokenizers, Judge, organisms)
    discrete    - Discrete Engine (pure reducer, editor state)
    world       - World Model (document store + mutation ops + save)
    history     - History Manager (checkpoints, undo/redo)
    projection  - Projection (widgets, render, overlays, inspector)
    app         - Runtime (TkVillage glue, on_tick continuity driver, effects)
    events      - shared semantic-event / effect vocabulary

A specialized workbench is a new window kind that reuses world/history/discrete
and adds its own organisms, projection overlays, and command templates.
"""


def main(argv=None):
    from .app import main as _main
    return _main(argv)


def run_editor(doc_path):
    from .app import run_editor as _run_editor
    return _run_editor(doc_path)

__all__ = ["main", "run_editor"]

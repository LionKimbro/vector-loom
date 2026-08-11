"""Checkpoint lineage holder for future editor undo and redo."""

import copy


g = {
    "checkpoints": [],
    "cursor": None,
}


def clear_history():
    """Discard every checkpoint and return to an empty lineage."""
    g["checkpoints"].clear()
    g["cursor"] = None


def add_checkpoint(packet):
    """Append a checkpoint, discarding any redo branch first."""
    cursor = g["cursor"]
    if cursor is not None:
        del g["checkpoints"][cursor + 1:]
    g["checkpoints"].append(copy.deepcopy(packet))
    g["cursor"] = len(g["checkpoints"]) - 1


def can_undo():
    """Return whether a prior checkpoint exists."""
    return g["cursor"] is not None and g["cursor"] > 0


def can_redo():
    """Return whether a later checkpoint exists."""
    return g["cursor"] is not None and g["cursor"] < len(g["checkpoints"]) - 1


def get_undo_checkpoint():
    """Move to and return the prior checkpoint, if one exists."""
    if not can_undo():
        return None
    g["cursor"] -= 1
    return copy.deepcopy(g["checkpoints"][g["cursor"]])


def get_redo_checkpoint():
    """Move to and return the next checkpoint, if one exists."""
    if not can_redo():
        return None
    g["cursor"] += 1
    return copy.deepcopy(g["checkpoints"][g["cursor"]])


def apply_effect(effect):
    """Reserve effect routing for the later designed checkpoint protocol."""
    raise ValueError(f"History effects are not designed yet: {effect['type']}")

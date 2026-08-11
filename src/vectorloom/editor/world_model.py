"""Durable Vector Loom library observed and eventually changed by the editor."""

import copy


g = {
    "library": None,
}


def set_library(library):
    """Install the already-validated Vector Loom library being edited."""
    g["library"] = library


def clear_library():
    """Remove the current library from the editor world."""
    g["library"] = None


def get_library_snapshot():
    """Return an isolated snapshot for a future history checkpoint."""
    return copy.deepcopy(g["library"])


def apply_effect(effect):
    """Apply a future lawful durable-library mutation effect."""
    raise ValueError(f"World mutation effects are not designed yet: {effect['type']}")

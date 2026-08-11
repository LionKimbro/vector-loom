"""CIRA update machine for the Vector Loom editor."""

import copy

from ..tk_runtime import tk_runtime
from . import discrete_engine, editor_window, event_queue, history_manager, judge, organisms
from . import projection, tokenizers, world_model


g = {
    "semantic-events": [],
}

raw = {}
raw_prev = {}
derived = {}
derived_prev = {}


def _make_initial_raw():
    return {
        "x": 0,
        "y": 0,
        "ms": None,
        "inside-canvas": False,
        "button-1-down": False,
        "keys-down": [],
        "last-event-type": None,
        "last-tree-selection": None,
        "last-widget-activation": None,
    }


def initialize_interaction_runtime():
    """Reset the editor interaction registers to their empty initial state."""
    g["semantic-events"].clear()
    raw.clear()
    raw.update(_make_initial_raw())
    raw_prev.clear()
    derived.clear()
    derived_prev.clear()
    discrete_engine.initialize_discrete_engine()
    world_model.clear_library()
    history_manager.clear_history()
    tokenizers.initialize_tokenizers()
    judge.initialize_judge()
    organisms.initialize_organisms()


def initialize_editor_runtime():
    """Initialize this editor's CIRA runtime.

    The longer name is the public composition entry point; the shorter
    machine name remains available for direct use in focused tests.
    """
    initialize_interaction_runtime()


def post_semantic_event(event):
    """Queue one already-interpreted editor event for the next reduction."""
    g["semantic-events"].append(dict(event))


def run_update_cycle():
    """Drain raw input, then run one CIRA cycle per record or motion sample."""
    pending = event_queue.drain_events()
    if not pending:
        _run_cycle({"type": "TIME_PASSES", "ms": tk_runtime.now_ms()})
        return

    for event in pending:
        if event["type"] == "POINTER_MOTION":
            for sample in event["samples"]:
                _run_cycle({"type": "POINTER_MOTION", **sample})
        else:
            _run_cycle(event)


def _run_cycle(raw_event):
    """Advance the CIRA machinery after one event updates the RAW snapshot."""
    raw_prev.clear()
    raw_prev.update(copy.deepcopy(raw))
    derived_prev.clear()
    derived_prev.update(copy.deepcopy(derived))

    _apply_raw_event(raw_event)
    tokenizers.run_tokenizers()
    judge.maintain_judge()
    organisms.evaluate_organisms()
    judge.maintain_judge()

    effects = discrete_engine.reduce_events(_drain_semantic_events())
    route_effects(effects)
    projection.project()


def _apply_raw_event(event):
    """Update current raw facts from one normalized input event."""
    raw["last-event-type"] = event["type"]
    raw["last-tree-selection"] = None
    raw["last-widget-activation"] = None

    if "ms" in event:
        raw["ms"] = event["ms"]

    if event["type"] == "POINTER_MOTION":
        raw.update({"x": event["x"], "y": event["y"], "inside-canvas": True})
    elif event["type"] == "BUTTON_1_PRESSED":
        raw.update({"x": event["x"], "y": event["y"], "inside-canvas": True, "button-1-down": True})
    elif event["type"] == "BUTTON_1_RELEASED":
        raw.update({"x": event["x"], "y": event["y"], "inside-canvas": True, "button-1-down": False})
    elif event["type"] == "POINTER_LEFT_CANVAS":
        raw.update({"x": event["x"], "y": event["y"], "inside-canvas": False})
    elif event["type"] == "KEY_PRESSED":
        keys_down = set(raw["keys-down"])
        keys_down.add(event["keysym"])
        raw["keys-down"] = sorted(keys_down)
    elif event["type"] == "KEY_RELEASED":
        keys_down = set(raw["keys-down"])
        keys_down.discard(event["keysym"])
        raw["keys-down"] = sorted(keys_down)
    elif event["type"] == "TREE_SELECTION_CHANGED":
        raw["last-tree-selection"] = {
            "tree": event["tree"],
            "item-iids": list(event["item-iids"]),
        }
    elif event["type"] == "WIDGET_ACTIVATED":
        raw["last-widget-activation"] = {
            "widget": event["widget"],
            "value": event["value"],
        }
    elif event["type"] == "TIME_PASSES":
        return
    else:
        raise ValueError(f"Unknown editor raw event: {event['type']}")


def route_effects(effects):
    """Deliver explicit reducer effects to their owning machines."""
    for effect in effects:
        owner = effect["owner"]
        if owner == "world-model":
            world_model.apply_effect(effect)
        elif owner == "history-manager":
            history_manager.apply_effect(effect)
        elif owner == "editor-window":
            editor_window.destroy_editor_window()
        elif owner == "projection":
            continue
        else:
            raise ValueError(f"Unknown editor effect owner: {owner}")


def _drain_semantic_events():
    events = list(g["semantic-events"])
    g["semantic-events"].clear()
    return events

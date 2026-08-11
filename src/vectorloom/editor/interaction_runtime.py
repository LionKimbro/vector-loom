"""CIRA update machine for the Vector Loom editor."""

import copy

from . import discrete_engine, event_queue, history_manager, judge, organisms
from . import projection, tokenizers, world_model


g = {
    "semantic-events": [],
}

raw = {}
raw_prev = {}
derived = {}
derived_prev = {}


def initialize_interaction_runtime():
    """Reset the editor interaction registers to their empty initial state."""
    g["semantic-events"].clear()
    raw.clear()
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


def run_interaction_cycle():
    """Advance one complete CIRA editor interaction cycle."""
    raw_prev.clear()
    raw_prev.update(copy.deepcopy(raw))
    derived_prev.clear()
    derived_prev.update(copy.deepcopy(derived))

    raw.clear()
    raw.update({"events": event_queue.drain_events()})
    tokenizers.run_tokenizers()
    judge.maintain_judge()
    organisms.evaluate_organisms()
    judge.maintain_judge()

    effects = discrete_engine.reduce_events(_drain_semantic_events())
    route_effects(effects)
    projection.project()


def run_update_cycle():
    """Run the editor's periodic Tk-runtime callback cycle."""
    run_interaction_cycle()


def route_effects(effects):
    """Deliver explicit reducer effects to their owning machines."""
    for effect in effects:
        owner = effect["owner"]
        if owner == "world-model":
            world_model.apply_effect(effect)
        elif owner == "history-manager":
            history_manager.apply_effect(effect)
        elif owner == "projection":
            continue
        else:
            raise ValueError(f"Unknown editor effect owner: {owner}")


def _drain_semantic_events():
    events = list(g["semantic-events"])
    g["semantic-events"].clear()
    return events

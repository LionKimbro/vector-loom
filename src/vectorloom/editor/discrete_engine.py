"""Committed editor workspace state and semantic reducer law."""


workspace = {}


def initialize_discrete_engine():
    """Reset the committed, non-durable editor workspace."""
    workspace.clear()
    workspace.update({
        "selection": None,
        "primary-design-name": None,
        "active-style-name": None,
        "focal-address": ".",
        "active-tool": None,
        "desired-camera": None,
    })


def reduce_events(events):
    """Reduce semantic events into replacement workspace state and effects."""
    effects = []
    for event in events:
        _reduce_event(event, effects)
    return effects


def _reduce_event(event, effects):
    event_type = event["type"]
    if event_type == "SET_SELECTION":
        workspace["selection"] = event.get("selection")
    elif event_type == "SET_FOCAL_ADDRESS":
        workspace["focal-address"] = event["address"]
    elif event_type == "SET_PRIMARY_DESIGN":
        workspace["primary-design-name"] = event.get("design-name")
        workspace["focal-address"] = "."
    elif event_type == "SET_ACTIVE_STYLE":
        workspace["active-style-name"] = event.get("style-name")
    elif event_type == "SET_ACTIVE_TOOL":
        workspace["active-tool"] = event.get("tool")
    elif event_type == "EXIT_EDITOR":
        effects.append({"owner": "editor-window", "type": "DESTROY_EDITOR_WINDOW"})
        return
    else:
        raise ValueError(f"Unknown editor semantic event: {event_type}")
    effects.append({"owner": "projection", "type": "WORKSPACE_CHANGED"})

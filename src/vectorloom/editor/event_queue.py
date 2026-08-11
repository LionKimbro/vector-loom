"""The raw-input queue between editor Tk callbacks and the CIRA runtime."""


event_queue = []
recent_events = []


def post_pointer_motion(x, y, ms):
    """Post a Canvas motion sample, coalescing it with adjacent motion."""
    sample = {"x": x, "y": y, "ms": ms}
    if event_queue and event_queue[-1]["type"] == "POINTER_MOTION":
        event_queue[-1]["samples"].append(sample)
        return
    event_queue.append({"type": "POINTER_MOTION", "samples": [sample]})


def post_event(event):
    """Append one normalized raw input record to the pending FIFO queue."""
    event_queue.append(event)


def drain_events():
    """Return pending records in order and retain the latest ten for diagnosis."""
    pending = list(event_queue)
    event_queue.clear()
    recent_events.extend(pending)
    del recent_events[:-10]
    return pending

"""Continuous editor interaction organisms."""


IDLE = "IDLE"

organisms = []


def initialize_organisms():
    """Reset the initially empty editor interaction-organism registry."""
    organisms.clear()


def register_organism(name, fn):
    """Register one bounded interaction finite-state machine."""
    organisms.append({
        "NAME": name,
        "ACTIVE": True,
        "STATE": IDLE,
        "HELD": {},
        "DATA": {},
        "FN": fn,
    })


def clear_organism(organism):
    """Return an organism to its reusable idle state."""
    organism.update({"STATE": IDLE, "HELD": {}, "DATA": {}})


def evaluate_organisms():
    """Let every active organism observe the shared current-cycle facts."""
    for organism in organisms:
        if organism["ACTIVE"]:
            organism["FN"](organism)


def get_active_organism_names():
    """Return names of organisms currently holding an interaction episode."""
    return {
        organism["NAME"]
        for organism in organisms
        if organism["STATE"] != IDLE
    }

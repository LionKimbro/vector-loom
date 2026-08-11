"""Resource-only coordination authority for editor interaction organisms."""

from . import organisms


CHECK = "CHECK"
COMMIT = "COMMIT"

coordination = {}


def initialize_judge():
    """Reset inspectable resource-lease state."""
    coordination.clear()
    coordination.update({
        "pointer-owner": None,
        "active-gesture": None,
        "resource-holds": {},
        "leases": {},
        "judge-notes": [],
    })


def get_permission(organism_name, request, resources):
    """Return whether one organism may inspect or claim resources."""
    for resource in resources:
        owner = coordination["resource-holds"].get(resource)
        if owner not in (None, organism_name):
            coordination["judge-notes"].append(
                f"denied {request}: {resource} held by {owner}"
            )
            return False
    if request == CHECK:
        return True
    if request != COMMIT:
        return False
    coordination["leases"][organism_name] = list(resources)
    for resource in resources:
        coordination["resource-holds"][resource] = organism_name
    if "pointer" in resources:
        coordination["pointer-owner"] = organism_name
        coordination["active-gesture"] = organism_name
    return True


def maintain_judge():
    """Release leases held by organisms that have returned to idle."""
    active_names = organisms.get_active_organism_names()
    for name in list(coordination["leases"]):
        if name not in active_names:
            for resource in coordination["leases"].pop(name):
                if coordination["resource-holds"].get(resource) == name:
                    coordination["resource-holds"].pop(resource)
    if coordination["pointer-owner"] not in active_names:
        coordination["pointer-owner"] = None
        coordination["active-gesture"] = None

"""History Manager: checkpoint lineage and undo/redo via state jumps.

History stores full document snapshots paired with the selection at that moment.
A snapshot-based world-revision strategy is one of the valid CIRA history
policies and is the simplest correct choice for documents of this size.

The key discipline: a checkpoint is pushed once per *completed* semantic edit
(a whole drag, an add, a delete), never per interaction frame. So undo/redo
navigates completed edits, exactly as CIRA prescribes.
"""

import copy


# doc_path -> {"stack": [snapshot, ...], "index": int}
# snapshot = {"doc": <deep copy>, "selection": <path or None>}
_HISTORY = {}


def init(doc_path, doc, selection=None):
    """Seed history with the loaded document as the first checkpoint."""
    _HISTORY[doc_path] = {"stack": [_snapshot(doc, selection)], "index": 0}


def push(doc_path, doc, selection):
    """Record a checkpoint after a completed edit, truncating any redo tail."""
    h = _HISTORY[doc_path]
    h["stack"] = h["stack"][: h["index"] + 1]
    h["stack"].append(_snapshot(doc, selection))
    h["index"] = len(h["stack"]) - 1


def undo(doc_path):
    """Step back one checkpoint. Returns a restored snapshot or None."""
    h = _HISTORY[doc_path]
    if h["index"] <= 0:
        return None
    h["index"] -= 1
    return _restore(h["stack"][h["index"]])


def redo(doc_path):
    """Step forward one checkpoint. Returns a restored snapshot or None."""
    h = _HISTORY[doc_path]
    if h["index"] >= len(h["stack"]) - 1:
        return None
    h["index"] += 1
    return _restore(h["stack"][h["index"]])


def can_undo(doc_path):
    h = _HISTORY[doc_path]
    return h["index"] > 0


def can_redo(doc_path):
    h = _HISTORY[doc_path]
    return h["index"] < len(h["stack"]) - 1


def _snapshot(doc, selection):
    return {"doc": copy.deepcopy(doc), "selection": selection}


def _restore(snap):
    # Deep-copy on the way out so the live document can be mutated freely without
    # corrupting the stored checkpoint.
    return {"doc": copy.deepcopy(snap["doc"]), "selection": snap["selection"]}

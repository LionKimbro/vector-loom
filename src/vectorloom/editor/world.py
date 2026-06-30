"""World Model: the durable document and the operations that mutate it.

The World Model owns modeled reality. Per CIRA, only world-mutation effects
routed by the runtime reach these functions; the Discrete Engine describes
mutations, it does not perform them. Documents are kept in a process-level store
keyed by path (the "world" of the editor session).

All paths here are *editable* node paths: dotted ids through the group tree
(e.g. "root", "root.box", "root.sub.box"). Render paths that point inside an
instance's def ("root.launch=folder_node.body") are collapsed to the nearest
editable node with editable_path().
"""

import json
import os
import tempfile

from .. import geometry as geo
from .. import model
from .. import symbols as S


# Document store: path -> canonical document.
_DOCS = {}


# --------------------------------------------------------------------------
# store
# --------------------------------------------------------------------------

def load(doc_path):
    """Load and normalize a document from disk into the store."""
    _DOCS[doc_path] = model.load_file(doc_path)
    return _DOCS[doc_path]


def get(doc_path):
    return _DOCS[doc_path]


def set_document(doc_path, doc):
    _DOCS[doc_path] = doc


def save(doc_path, doc):
    """Atomically write the canonical document to disk as pretty JSON.

    Canonical documents normalize idempotently, so this round-trips cleanly:
    the file written here reloads to an identical document.
    """
    text = json.dumps(doc, indent=2)
    directory = os.path.dirname(os.path.abspath(doc_path))
    fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            fp.write(text)
            fp.write("\n")
        os.replace(tmp, doc_path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# --------------------------------------------------------------------------
# path utilities
# --------------------------------------------------------------------------

def editable_path(render_path):
    """Collapse a render path to the nearest editable node path.

    Cuts at the first instance boundary ('=') and drops any connector suffix
    (':name'), so geometry drawn from a def resolves to the instance node, which
    is the thing a user can actually select and move.
    """
    return render_path.split("=")[0].split(":")[0]


def find_node(doc, path):
    """Return the node at an editable path, or None if it does not resolve."""
    parts = path.split(".")
    node = doc["root"]
    if not parts or parts[0] != node["id"]:
        return None
    for seg in parts[1:]:
        if node["type"] != S.GROUP:
            return None
        node = _child_by_id(node, seg)
        if node is None:
            return None
    return node


def get_parent(doc, path):
    """Return (parent_group, last_id) for a path, or (None, None) for root."""
    parts = path.split(".")
    if len(parts) <= 1:
        return None, None
    parent = find_node(doc, ".".join(parts[:-1]))
    return parent, parts[-1]


def is_group(doc, path):
    node = find_node(doc, path)
    return bool(node) and node["type"] == S.GROUP


# --------------------------------------------------------------------------
# mutations
# --------------------------------------------------------------------------

def move_node(doc, path, world_dx, world_dy):
    """Shift a node by a document-world delta, converting it into the node's
    parent-local frame so the move is correct even inside scaled/rotated groups.
    """
    node = find_node(doc, path)
    if node is None:
        return
    parent_m = _parent_frame(doc, path)
    local_dx, local_dy = geo.apply_vector(geo.invert(parent_m), world_dx, world_dy)
    _shift_local(node, local_dx, local_dy)


def add_child(doc, parent_path, raw_node):
    """Normalize a loose node and append it to a parent group. Falls back to the
    root group when the parent is not a group. Returns the new node's path."""
    parent = find_node(doc, parent_path)
    if parent is None or parent["type"] != S.GROUP:
        parent = doc["root"]
        parent_path = doc["root"]["id"]
    node = model.normalize_node(raw_node, doc["styles"])
    parent["children"].append(node)
    return f"{parent_path}.{node['id']}"


def delete_node(doc, path):
    """Remove a node from its parent. Root cannot be deleted."""
    parent, last_id = get_parent(doc, path)
    if parent is None:
        return False
    parent["children"] = [c for c in parent["children"] if c["id"] != last_id]
    return True


def replace_node(doc, path, raw_node):
    """Replace the node at path with a normalized version of raw_node, keeping
    its id stable so the selection path stays valid."""
    parent, last_id = get_parent(doc, path)
    raw = dict(raw_node)
    raw["id"] = last_id if parent is not None else doc["root"]["id"]
    node = model.normalize_node(raw, doc["styles"])
    if parent is None:
        doc["root"] = node
        return
    parent["children"] = [node if c["id"] == last_id else c for c in parent["children"]]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _child_by_id(group, node_id):
    for child in group["children"]:
        if child["id"] == node_id:
            return child
    return None


def _parent_frame(doc, path):
    """Accumulate the transform of the node's parent frame (no camera)."""
    parts = path.split(".")
    node = doc["root"]
    m = geo.IDENTITY
    for seg in parts[1:]:
        m = geo.compose(m, _node_transform(node))
        node = _child_by_id(node, seg)
        if node is None:
            break
    return m


def _node_transform(node):
    if node["type"] in (S.GROUP, S.INSTANCE):
        t = node["transform"]
        return geo.from_trs(t["tx"], t["ty"], t["sx"], t["sy"], t["rotate"])
    return geo.IDENTITY


def _shift_local(node, dx, dy):
    kind = node["type"]
    if kind in (S.GROUP, S.INSTANCE):
        node["transform"]["tx"] += dx
        node["transform"]["ty"] += dy
    elif kind == S.LINE:
        node["x1"] += dx
        node["y1"] += dy
        node["x2"] += dx
        node["y2"] += dy
    elif kind == S.POLYLINE:
        node["points"] = [[p[0] + dx, p[1] + dy] for p in node["points"]]
    else:  # rect, oval, port, text
        node["x"] += dx
        node["y"] += dy

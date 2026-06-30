"""The castle gate for Vector Loom documents.

External documents may be written loosely by a human or an agent. This module
normalizes any accepted shape into one canonical structure, validates it, and
hands the trusted interior to the runtime. After normalize_document(), the rest
of the program assumes every node has its full canonical shape: no optional
fields, no missing ids, no string-vs-dict ambiguity.

Canonical document:

    {
      "format": "vectorloom",
      "version": "1",
      "meta":   {...arbitrary...},
      "styles": {name: canonical_style},
      "defs":   {name: canonical_node},
      "root":   canonical_group
    }

Canonical style: {"stroke", "fill", "width", "dash"} with concrete values.
"""

import json

from . import symbols as S


class VloomError(Exception):
    """Raised when a document cannot be normalized or validated."""


def load_file(path):
    """Read a .vloom.json file and return a normalized document."""
    with open(path, "r", encoding="utf-8") as fp:
        raw = json.load(fp)
    return normalize_document(raw)


DEFAULT_STYLE = {"stroke": "#222222", "fill": None, "width": 1.0, "dash": None}
DEFAULT_WIRE_STYLE = {"stroke": "#1565c0", "fill": None, "width": 2.0, "dash": None}

# Per-process counter used only to fabricate ids for nodes that lack one.
_id_counter = {"n": 0}


def _next_id(kind):
    _id_counter["n"] += 1
    return f"{kind}_{_id_counter['n']}"


# --------------------------------------------------------------------------
# public entry points
# --------------------------------------------------------------------------

def normalize_document(raw):
    """Normalize a raw document dict into canonical form.

    Accepts a document with at least a `root` node. Format marker, version,
    styles, defs, and meta are all optional and filled with sane defaults.
    """
    if not isinstance(raw, dict):
        raise VloomError("document must be a JSON object")

    styles = _normalize_styles(raw.get("styles", {}))
    defs = {}
    for name, node in raw.get("defs", {}).items():
        defs[name] = _normalize_node(node, styles)

    root_raw = raw.get("root")
    if root_raw is None:
        raise VloomError("document has no 'root'")
    root = _normalize_node(root_raw, styles)
    if root["type"] != S.GROUP:
        # Wrap a bare primitive root in a group so the tree is uniform.
        root = {
            "type": S.GROUP,
            "id": _next_id(S.GROUP),
            "transform": _identity_transform(),
            "style": dict(DEFAULT_STYLE),
            "connectors": {},
            "children": [root],
        }

    connections = [_normalize_connection(c, styles) for c in raw.get("connections", [])]

    doc = {
        "format": S.FORMAT_KEY,
        "version": str(raw.get("version", S.FORMAT_VERSION)),
        "meta": dict(raw.get("meta", {})),
        "styles": styles,
        "defs": defs,
        "root": root,
        "connections": connections,
    }
    validate_document(doc)
    return doc


def normalize_node(raw, styles=None):
    """Normalize a single raw node into canonical form (public castle gate for
    the editor, which fabricates new nodes as loose shorthand)."""
    return _normalize_node(raw, styles or {})


def normalize_connection(raw, styles=None):
    """Normalize a single raw connection (public castle gate for the editor)."""
    return _normalize_connection(raw, styles or {})


def _normalize_connection(raw, styles):
    """A connection joins two connectors, each referenced by node path + name.

    Endpoints are resolved to world positions at render time; an unresolvable
    endpoint simply does not draw, so connections survive edits to the tree.
    """
    if "from" not in raw or "to" not in raw:
        raise VloomError("connection requires 'from' and 'to' endpoints")
    return {
        "id": raw.get("id") or _next_id("conn"),
        "from": _normalize_endpoint(raw["from"]),
        "to": _normalize_endpoint(raw["to"]),
        "style": _merge_style(DEFAULT_WIRE_STYLE, raw["style"]) if isinstance(raw.get("style"), dict)
        else dict(styles[raw["style"]]) if isinstance(raw.get("style"), str) and raw["style"] in styles
        else dict(DEFAULT_WIRE_STYLE),
    }


def _normalize_endpoint(raw):
    return {"node": str(raw["node"]), "name": str(raw["name"])}


def validate_document(doc):
    """Check structural invariants. Raises VloomError on the first problem.

    Validation only inspects; it performs no work. The runtime trusts a
    document that survives this pass.
    """
    def_names = set(doc["defs"].keys())
    _validate_node(doc["root"], def_names)
    for name, node in doc["defs"].items():
        _validate_node(node, def_names)


# --------------------------------------------------------------------------
# styles
# --------------------------------------------------------------------------

def _normalize_styles(raw_styles):
    out = {}
    for name, spec in raw_styles.items():
        out[name] = _merge_style(DEFAULT_STYLE, spec)
    return out


def _merge_style(base, spec):
    """Return a concrete style dict from a base plus a spec dict."""
    style = dict(base)
    if not spec:
        return style
    for key in ("stroke", "fill", "width", "dash"):
        if key in spec:
            style[key] = spec[key]
    if "width" in style and style["width"] is not None:
        style["width"] = float(style["width"])
    return style


def _resolve_node_style(raw_node, styles):
    """Resolve a node's effective style.

    Precedence, lowest to highest: the named style referenced by `style` (when
    a string), then an inline `style` dict, then shorthand keys placed directly
    on the node (stroke, fill, width, dash).
    """
    style = dict(DEFAULT_STYLE)
    ref = raw_node.get("style")
    if isinstance(ref, str):
        if ref not in styles:
            raise VloomError(f"unknown style reference: {ref!r}")
        style = dict(styles[ref])
    elif isinstance(ref, dict):
        style = _merge_style(style, ref)
    shorthand = {k: raw_node[k] for k in ("stroke", "fill", "width", "dash") if k in raw_node}
    return _merge_style(style, shorthand)


# --------------------------------------------------------------------------
# nodes
# --------------------------------------------------------------------------

def _normalize_node(raw, styles):
    if not isinstance(raw, dict):
        raise VloomError(f"node must be an object, got {type(raw).__name__}")
    kind = raw.get("type")
    if kind not in S.NODE_KINDS:
        raise VloomError(f"unknown node type: {kind!r}")

    node = {"type": kind, "id": raw.get("id") or _next_id(kind), "style": _resolve_node_style(raw, styles)}

    # Every node carries a transform, so move/resize/rotate are uniform. For
    # group/instance the x/y/scale shorthand means translate/scale; for
    # primitives x/y are geometry, so their transform comes only from an explicit
    # canonical `transform` dict (default identity).
    node["transform"] = _normalize_transform(raw, allow_shorthand=kind in (S.GROUP, S.INSTANCE))

    if kind == S.GROUP:
        node["connectors"] = _normalize_connectors(raw.get("connectors", {}))
        node["children"] = [_normalize_node(c, styles) for c in raw.get("children", [])]
    elif kind == S.INSTANCE:
        if "def" not in raw:
            raise VloomError("instance node requires a 'def' name")
        node["def"] = raw["def"]
        node["connectors"] = _normalize_connectors(raw.get("connectors", {}))
    elif kind == S.RECT or kind == S.OVAL:
        node["x"] = float(raw.get("x", 0.0))
        node["y"] = float(raw.get("y", 0.0))
        node["w"] = float(raw.get("w", 0.0))
        node["h"] = float(raw.get("h", 0.0))
    elif kind == S.LINE:
        node["x1"] = float(raw.get("x1", 0.0))
        node["y1"] = float(raw.get("y1", 0.0))
        node["x2"] = float(raw.get("x2", 0.0))
        node["y2"] = float(raw.get("y2", 0.0))
    elif kind == S.POLYLINE:
        node["points"] = [[float(p[0]), float(p[1])] for p in raw.get("points", [])]
        node["closed"] = bool(raw.get("closed", False))
    elif kind == S.PORT:
        node["x"] = float(raw.get("x", 0.0))
        node["y"] = float(raw.get("y", 0.0))
        node["name"] = raw.get("name", node["id"])
        node["direction"] = raw.get("direction", S.DIR_NONE)
        node["role"] = raw.get("role", S.ROLE_ANCHOR)
        node["radius"] = float(raw.get("radius", 4.0))
    elif kind == S.TEXT:
        # Text is experimental: tkinter Canvas text does not scale or rotate
        # consistently. Provided for labels; a stroke-font may replace it later.
        node["x"] = float(raw.get("x", 0.0))
        node["y"] = float(raw.get("y", 0.0))
        node["text"] = str(raw.get("text", ""))
        node["size"] = float(raw.get("size", 12.0))
        node["anchor"] = raw.get("anchor", "nw")

    return node


def _normalize_transform(raw, allow_shorthand=True):
    """Read translate/scale/rotate components.

    Honors an already-canonical `transform` dict so that normalizing a canonical
    document is idempotent (this is what lets a document round-trip). When
    allow_shorthand is true (group/instance), x/y/scale on the node also seed the
    transform; for primitives those keys are geometry, so allow_shorthand is
    false and the transform defaults to identity.
    """
    t = raw.get("transform")
    if isinstance(t, dict):
        return {
            "tx": float(t.get("tx", 0.0)),
            "ty": float(t.get("ty", 0.0)),
            "sx": float(t.get("sx", 1.0)),
            "sy": float(t.get("sy", 1.0)),
            "rotate": float(t.get("rotate", 0.0)),
        }
    if not allow_shorthand:
        return _identity_transform()
    tx = float(raw.get("x", raw.get("tx", 0.0)))
    ty = float(raw.get("y", raw.get("ty", 0.0)))
    scale = raw.get("scale")
    if scale is None:
        sx = float(raw.get("sx", 1.0))
        sy = float(raw.get("sy", 1.0))
    else:
        sx = sy = float(scale)
    rotate = float(raw.get("rotate", 0.0))
    return {"tx": tx, "ty": ty, "sx": sx, "sy": sy, "rotate": rotate}


def _identity_transform():
    return {"tx": 0.0, "ty": 0.0, "sx": 1.0, "sy": 1.0, "rotate": 0.0}


def _normalize_connectors(raw_connectors):
    out = {}
    for name, spec in raw_connectors.items():
        out[name] = {
            "x": float(spec.get("x", 0.0)),
            "y": float(spec.get("y", 0.0)),
            "direction": spec.get("direction", S.DIR_NONE),
            "role": spec.get("role", S.ROLE_ANCHOR),
        }
    return out


# --------------------------------------------------------------------------
# validation helpers
# --------------------------------------------------------------------------

def _validate_node(node, def_names):
    kind = node["type"]
    if kind == S.INSTANCE and node["def"] not in def_names:
        raise VloomError(f"instance references unknown def: {node['def']!r}")
    if kind == S.GROUP:
        for child in node["children"]:
            _validate_node(child, def_names)

"""Shared editor vocabulary: semantic event names and effect names.

Kept in one place so the Continuity Engine (which emits events), the Discrete
Engine (which consumes them and emits effects), and the Runtime (which routes
effects) all agree on stable symbolic strings. Following Lion's symbols
convention: uppercase names bound to identical string constants.
"""

# --- semantic events (Continuity / GUI -> Discrete Engine) ---
SET_SELECTION = "SET_SELECTION"
NODE_MOVED = "NODE_MOVED"
NODE_TRANSFORMED = "NODE_TRANSFORMED"   # resize/rotate commit: carries a screen-space transform
NODE_FIELD_CHANGED = "NODE_FIELD_CHANGED"
NODE_ADDED = "NODE_ADDED"
NODE_DELETED = "NODE_DELETED"
SAVE_FILE = "SAVE_FILE"
LOAD_FILE = "LOAD_FILE"
UNDO = "UNDO"
REDO = "REDO"

# --- handle modes (Discrete-owned per-selection focus) ---
# Selecting a node lands in RESIZE; re-clicking it toggles RESIZE <-> ROTATE.
# MODE_SELECT is the no-selection sentinel.
MODE_SELECT = "SELECT"
MODE_RESIZE = "RESIZE"
MODE_ROTATE = "ROTATE"
HANDLE_MODE_CYCLE = {MODE_RESIZE: MODE_ROTATE, MODE_ROTATE: MODE_RESIZE}

# camera events (not undoable; emit no checkpoint)
PAN_BY = "PAN_BY"
ZOOM_AT = "ZOOM_AT"
FIT_REQUESTED = "FIT_REQUESTED"

# --- effects (Discrete Engine -> Runtime) ---
# Domain effects are routed by the editor runtime, not by TkVillage.
WORLD_MUTATE = "WORLD_MUTATE"   # fields: op, plus op-specific data
CHECKPOINT = "CHECKPOINT"       # snapshot current world + selection into history
STATE_JUMP = "STATE_JUMP"       # fields: direction ("undo" | "redo")
SAVE = "SAVE"                   # write current document to disk
RELOAD = "RELOAD"               # reload document from disk, reset history

# world-mutation ops
OP_MOVE = "move"
OP_ADD = "add"
OP_DELETE = "delete"
OP_REPLACE = "replace"
OP_CONNECT = "connect"
OP_TRANSFORM = "transform"   # bake a screen-space transform into a node

# --- immediates (Continuity -> Projection, single frame, volatile) ---
DRAG_PREVIEW = "DRAG_PREVIEW"      # move: carries path, sdx, sdy
TRANSFORM_PREVIEW = "TRANSFORM_PREVIEW"  # resize/rotate: carries path + screen transform
HOVER = "HOVER"
SNAP = "SNAP"   # a connector pair is within snap range during a drag

# handle kinds (projection affordances, hit-tested by continuity)
HANDLE_RESIZE = "resize"
HANDLE_ROTATE = "rotate"

"""Shared editor vocabulary: semantic event names and effect names.

Kept in one place so the Continuity Engine (which emits events), the Discrete
Engine (which consumes them and emits effects), and the Runtime (which routes
effects) all agree on stable symbolic strings. Following Lion's symbols
convention: uppercase names bound to identical string constants.
"""

# --- semantic events (Continuity / GUI -> Discrete Engine) ---
SET_SELECTION = "SET_SELECTION"
NODE_MOVED = "NODE_MOVED"
NODE_FIELD_CHANGED = "NODE_FIELD_CHANGED"
NODE_ADDED = "NODE_ADDED"
NODE_DELETED = "NODE_DELETED"
SAVE_FILE = "SAVE_FILE"
LOAD_FILE = "LOAD_FILE"
UNDO = "UNDO"
REDO = "REDO"

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

# --- immediates (Continuity -> Projection, single frame, volatile) ---
DRAG_PREVIEW = "DRAG_PREVIEW"
HOVER = "HOVER"
SNAP = "SNAP"   # a connector pair is within snap range during a drag

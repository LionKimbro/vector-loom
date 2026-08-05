"""Stable symbolic constants for Vector Loom.

Following Lion's symbols convention: uppercase identifiers bound to identical
string constants, so typos surface as NameErrors and node kinds read clearly.
"""

# --- format marker ---
FORMAT_KEY = "vectorloom"
FORMAT_VERSION = "1"

# --- node kinds (the "type" field of a node) ---
GROUP = "group"
RECT = "rect"
OVAL = "oval"
LINE = "line"
POLYLINE = "polyline"
PORT = "port"
INSTANCE = "instance"
TEXT = "text"

NODE_KINDS = {GROUP, RECT, OVAL, LINE, POLYLINE, PORT, INSTANCE, TEXT}

# --- port roles / directions (advisory; the runtime does not constrain them) ---
ROLE_INPUT = "input"
ROLE_OUTPUT = "output"
ROLE_BIDIRECTIONAL = "bidirectional"
ROLE_ANCHOR = "anchor"

DIR_LEFT = "left"
DIR_RIGHT = "right"
DIR_UP = "up"
DIR_DOWN = "down"
DIR_NONE = "none"

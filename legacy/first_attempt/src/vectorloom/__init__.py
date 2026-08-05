"""Vector Loom: a data format, runtime, and editor for 2-D nestable vector structures.

Public surface:
    normalize_document, validate_document, load_file, VloomError   (model)
    render_document, document_bounds                               (render)
    view_document                                                  (viewer)
"""

from .model import (
    VloomError,
    load_file,
    normalize_document,
    validate_document,
)
from .render import document_bounds, render_document

__all__ = [
    "VloomError",
    "document_bounds",
    "load_file",
    "normalize_document",
    "render_document",
    "validate_document",
]

"""A minimal standalone viewer for Vector Loom documents.

This is a plain-tkinter inspection tool, not the reducer-core editor. It exists
to satisfy the "build the renderer before the editor" path: load a document,
fit it, and let you pan and zoom to confirm the runtime renders correctly.

    python -m vectorloom.viewer examples/folder_node.vloom.json

Controls: drag to pan, mouse wheel to zoom, 'f' to fit, 'q' to quit.
"""

import sys
import tkinter as tk

from . import geometry as geo
from . import model
from . import render


def view_document(doc, title="Vector Loom Viewer"):
    """Open a window showing a normalized document. Blocks until closed."""
    root = tk.Tk()
    root.title(title)
    canvas = tk.Canvas(root, width=900, height=640, background="#fafafa", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    vw = {"doc": doc, "canvas": canvas, "scale": 1.0, "ox": 0.0, "oy": 0.0, "drag": None}

    canvas.bind("<ButtonPress-1>", lambda e: _on_press(vw, e))
    canvas.bind("<B1-Motion>", lambda e: _on_drag(vw, e))
    canvas.bind("<MouseWheel>", lambda e: _on_wheel(vw, e))        # Windows / macOS
    canvas.bind("<Button-4>", lambda e: _on_wheel(vw, e, 120))     # X11 scroll up
    canvas.bind("<Button-5>", lambda e: _on_wheel(vw, e, -120))    # X11 scroll down
    root.bind("f", lambda e: (_fit(vw), _redraw(vw)))
    root.bind("q", lambda e: root.destroy())
    canvas.bind("<Configure>", lambda e: _redraw(vw))

    root.after(50, lambda: (_fit(vw), _redraw(vw)))
    root.mainloop()


def _base_transform(vw):
    return geo.compose(geo.translate(vw["ox"], vw["oy"]), geo.scale(vw["scale"], vw["scale"]))


def _redraw(vw):
    canvas = vw["canvas"]
    canvas.delete("all")
    render.render_document(canvas, vw["doc"], _base_transform(vw))


def _fit(vw):
    """Center and scale the document to fill most of the canvas."""
    canvas = vw["canvas"]
    bounds = render.document_bounds(vw["doc"])
    cw = canvas.winfo_width() or 900
    ch = canvas.winfo_height() or 640
    if not bounds:
        vw["scale"], vw["ox"], vw["oy"] = 1.0, cw / 2.0, ch / 2.0
        return
    minx, miny, maxx, maxy = bounds
    span_x = max(maxx - minx, 1.0)
    span_y = max(maxy - miny, 1.0)
    margin = 0.85
    vw["scale"] = min(cw * margin / span_x, ch * margin / span_y)
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0
    vw["ox"] = cw / 2.0 - cx * vw["scale"]
    vw["oy"] = ch / 2.0 - cy * vw["scale"]


def _on_press(vw, event):
    vw["drag"] = (event.x, event.y, vw["ox"], vw["oy"])


def _on_drag(vw, event):
    if not vw["drag"]:
        return
    sx, sy, ox, oy = vw["drag"]
    vw["ox"] = ox + (event.x - sx)
    vw["oy"] = oy + (event.y - sy)
    _redraw(vw)


def _on_wheel(vw, event, delta=None):
    """Zoom about the cursor so the point under the pointer stays put."""
    step = delta if delta is not None else event.delta
    factor = 1.1 if step > 0 else (1.0 / 1.1)
    # Keep the world point under the cursor fixed across the zoom.
    wx = (event.x - vw["ox"]) / vw["scale"]
    wy = (event.y - vw["oy"]) / vw["scale"]
    vw["scale"] *= factor
    vw["ox"] = event.x - wx * vw["scale"]
    vw["oy"] = event.y - wy * vw["scale"]
    _redraw(vw)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m vectorloom.viewer <document.vloom.json>")
        return 1
    doc = model.load_file(argv[0])
    view_document(doc, title=f"Vector Loom — {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

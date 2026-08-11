# Vector Loom Pseudocode Migration Structure

Status: working migration map, 2026-08-10.

This document records the currently envisioned home for the existing Vector
Loom BAD pseudocode.  It is a planning aid only: it does not move, replace, or
invalidate any current sketch.  A sketch moves only after its new responsibility
and boundary are clear.

## Architectural Direction

Vector Loom is a Tkinter-Canvas-specific system.  It is not currently being
split into a general vector runtime plus a Tkinter adapter.

The useful separation is between:

1. **Tk runtime environment** -- machinery that runs one of Vector Loom's own
   programs: its hidden Tk root, timer, application composition, Toplevel
   windows, and main loop.
2. **Canvas drawing library** -- Vector Loom drawing code that renders onto a
   caller-provided `tkinter.Canvas`.  This is the client-facing library for an
   application that already has its own Python and Tkinter environment.

The demo, future viewer, and future editor are programs that compose these two
areas.  An external client may use the Canvas drawing library without using
Vector Loom's Tk runtime environment.

## Intended BAD Module Tree

```text
pseudo-src/vectorloom/
  modules/
    tk-runtime/
      tk-runtime.md
      timer.md
      canvas-host-window.md
      app-shell.md
    canvas/
      canvas-context.md
      transform-stack.md
    demo/
      demo-bootstrap.md
      canvas-host-demo.md
    viewer/
      viewer-bootstrap.md
    editor/
      editor-bootstrap.md
  aspects/
    canvas-item-identification.md
  data-structures/
    transform-stack.md
```

`viewer/` and `editor/` are placeholders for later work.  Their presence in
this map does not authorize their implementation.

## Current Sketches and Rough Target Homes

| Current path | Intended target path | Migration note |
| --- | --- | --- |
| `project-profile/project-profile.md` | `../../project/project-profile.md` | Review before moving: it contains older direction that must not silently govern the new structure. |
| `modules/tk-runtime.md` | `modules/tk-runtime/tk-runtime.md` | Shared hidden-root and root-level Tk policy. |
| `modules/timer.md` | `modules/tk-runtime/timer.md` | Shared periodic timer service. |
| `modules/canvas-host-window.md` | `modules/tk-runtime/canvas-host-window.md` | A Vector Loom-owned Toplevel/Canvas host for its own programs; external clients do not need it. |
| `modules/app-shell.md` | `modules/tk-runtime/app-shell.md` | Refactor from demo-specific startup to a common shell configured through its own `config["app-specific-setup"]` value. |
| `modules/transform-stack.md` | `modules/canvas/transform-stack.md` | Keeps its transform-only responsibility, but travels with Vector Loom Canvas drawing rather than a proposed general core. |
| `modules/canvas-context.md` | `modules/canvas/canvas-context.md` | Remains the actual Tk Canvas renderer: it owns `draw()`, Canvas calls, tags, styles/designs for now, and the connector registry. |
| `modules/canvas-host-demo.md` | `modules/demo/canvas-host-demo.md` | Becomes demo content/setup, rather than behavior App Shell starts unconditionally. |
| none yet | `modules/demo/demo-bootstrap.md` | Composes the runtime host, Canvas Context, and kinetic demo. |
| none yet | `modules/viewer/viewer-bootstrap.md` | Future viewer composition point. |
| none yet | `modules/editor/editor-bootstrap.md` | Future editor composition point. |
| `aspects/canvas-item-identification.md` | unchanged | Cross-cutting Canvas tag contract; update only its references as needed. |
| `data-structures/transform-stack.md` | unchanged | Update its `Owned By` reference after the Transform Stack sketch moves. |

## Shared Application Shell Shape

`modules/tk-runtime/app-shell.md` should own its application-composition
configuration separately from Tk Runtime's lower-level configuration.  Its
initial fixed-shape configuration bundle is:

```python
config = {
    "app-specific-setup": None,
}
```

The demo, viewer, or editor bootstrap sets
`app_shell.config["app-specific-setup"]` to its own nullary setup function,
then calls `app_shell.main()`.

At the beginning of `main()`, App Shell reads that value and raises a clear
exception if it is still `None`.  This makes the missing configuration visible
at the application boundary before Tk startup begins, while keeping the chosen
setup function inspectable during the program's lifetime.

After that check, the common startup sequence is:

```text
create and withdraw Tk root
→ run the selected program bootstrap
→ start the periodic timer
→ enter Tk mainloop
```

Each program bootstrap owns its application-specific composition.  It may
create windows, give a Canvas to Canvas Context, install a periodic callback,
and register cleanup behavior.  The shared App Shell must not import or know
whether the selected program is the demo, viewer, or editor.

Tk Runtime retains its separate `config` bundle for lower-level runtime policy,
such as timer interval and whether no remaining Toplevel windows should end the
main loop.  App Shell configuration must not be mixed into that bundle.

## Canvas Boundary

The Canvas drawing library is for callers with an existing Canvas:

```text
client-owned Tk root / window / Canvas
  → vectorloom canvas drawing library
  → Canvas Context draws Vector Loom designs onto that Canvas
```

Canvas Context is not a thin wrapper or a generic renderer adapter.  It is the
actual Vector Loom Tk Canvas renderer.  It calls Canvas creation methods,
creates Canvas tags, resolves styles, and records immediate-mode connectors.
Transform Stack supports that renderer and remains alongside it in `canvas/`.

## Deliberate Deferrals

- Do not create a generic vector-rendering core merely to separate Tk from
  non-Tk code.
- Do not move rendered Python modules until the corresponding target BAD
  sketch is ready.
- Do not begin viewer or editor implementation from this map.
- Do not decide the format-loader or durable editor-state architecture here.

```text
date: 2026-08-10
title: Vector Loom Tkinter Project Structure Direction
purpose: Replace the proposed general-core/Tkinter split with the settled
  Tk-runtime-environment and Canvas-drawing-library structure.
supersedes: 0020__vectorloom-project-structure-direction.md
```

# Vector Loom Tkinter Project Structure Direction

Vector Loom is a Tkinter-Canvas-specific vector format, drawing runtime, and
future editor.  It is not currently organized as a general vector-rendering
core with a Tkinter adapter.

This document replaces the target package boundaries in
`0020__vectorloom-project-structure-direction.md`.  The earlier document
correctly established the need to separate reusable work from application
programs; the specific `core/` and `tkinter/` split is now superseded.

## The Two Reusable Areas

Vector Loom has two distinct reusable areas.

### Tk Runtime Environment

The Tk runtime environment runs Vector Loom's own programs.  It owns the
hidden Tk root, periodic timer, shared App Shell, and generic Canvas Host
Window.  The demo, future viewer, and future editor use this environment to
run as standalone applications.

### Canvas Drawing Library

The Canvas drawing library renders Vector Loom designs onto a caller-provided
`tkinter.Canvas`.  It is for clients that already own their Python/Tkinter
environment and want Vector Loom to act as a guest.

Canvas Context is the actual Tk Canvas renderer.  It looks up designs, walks
their groups, resolves styles and transforms, calls Canvas creation methods,
adds Canvas tags, and records immediate-mode connector records.  It does not
create a Tk root, Toplevel, timer, or main loop.

Transform Stack belongs with the Canvas drawing library.  Although it does not
call Canvas methods itself, it exists to support Vector Loom Canvas drawing;
there is no present need to make it a general graphics core.

## Intended Repository Tree

```text
vectorloom/
  docs/
    raw/
    architecture/
    guides/
    reference/

  pseudo-src/
    project/
      project-profile.md
    vectorloom/
      aspects/
      data-structures/
      interfaces/
      modules/
        tk-runtime/
        canvas/
        demo/
        viewer/
        editor/

  src/
    vectorloom/
      tk_runtime/
      canvas/
      demo/
      formats/       # later
      viewer/        # later
      editor/        # later

  tests/
```

The `formats/`, `viewer/`, and `editor/` homes are future work.  Their
appearance in this tree does not authorize their implementation.

## Current BAD and Source Homes

```text
pseudo-src/vectorloom/modules/tk-runtime/
  tk-runtime.md
  timer.md
  canvas-host-window.md
  app-shell.md

pseudo-src/vectorloom/modules/canvas/
  canvas-context.md
  transform-stack.md

pseudo-src/vectorloom/modules/demo/
  demo-bootstrap.md
  canvas-host-demo.md
```

The corresponding rendered Python is now present under:

```text
src/vectorloom/tk_runtime/
src/vectorloom/canvas/
src/vectorloom/demo/
```

## Application Composition

`tk_runtime/app_shell` is shared application infrastructure.  It has its own
fixed-shape configuration bundle:

```python
config = {
    "app-specific-setup": None,
}
```

A demo, viewer, or editor bootstrap sets `app-specific-setup`, then calls
`app_shell.main()`.  App Shell raises a clear exception if it was not
configured.  Once configured, its common startup order is:

```text
create and withdraw Tk root
→ run configured application-specific setup
→ start periodic timer
→ enter Tk main loop
```

App Shell must not import or know which application it is running.  A bootstrap
owns its own windows, Canvas setup, periodic callback, and cleanup choices.

## Migration Status

The proving-ground runtime has been rendered into the three current source
packages.  The kinetic transform demonstration is now a demo application that
composes Tk Runtime and Canvas drawing, rather than behavior baked into App
Shell.

The historical flat source paths and flat BAD module paths have been retired.
The focused runtime suite covers Canvas drawing, Transform Stack, demo
composition, and App Shell configuration/startup order.

## Deliberate Deferrals

- Do not introduce a general vector-rendering core merely for abstraction.
- Do not define the public client-facing Canvas API until it is needed.
- Do not implement viewer or editor behavior yet.
- Do not decide durable editor state, retained instances, or mutation
  architecture here.
- Begin editor-directed work with a narrow VectorLoom Basic format reader,
  then use it to build an editor shell that loads and previews a named design.

## See Also

- `0015__vectorloom-basic.json` — current VectorLoom Basic document format.
- `0017__connector-points.md` — connector semantics and direction.
- `0018__instance-assembly-and-mutation-direction.md` — provisional future
  direction for durable instances and mutation.
- `0020__vectorloom-project-structure-direction.md` — superseded project
  structure direction.
- `../../pseudo-src/project/project-profile.md` — current project profile.

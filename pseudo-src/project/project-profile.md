# Project Profile — Vector Loom

## Target

- Language: Python 3.10 or later.
- Host platform: Windows 11 desktop application.
- Rendered package target: `src/vectorloom/`.
- User-interface toolkit: Python Tkinter.
- Direct-manipulation and client drawing surface: `tkinter.Canvas`.
- Test target: ordinary Python tests under `tests/`.

## Purpose

Vector Loom develops a Tkinter-Canvas-specific vector format, drawing runtime,
and future editor.  It is intentionally useful in two different Tkinter use
contexts:

1. **Vector Loom applications** -- the demo, future viewer, and future editor
   use Vector Loom's Tk runtime environment to create a root, windows, timer,
   and main loop.
2. **Client applications** -- a client that already owns a Python/Tkinter
   application can give Vector Loom a live `tkinter.Canvas` and use its Canvas
   drawing library as a guest, without adopting Vector Loom's application
   runtime.

Vector Loom is not currently a toolkit-neutral vector graphics system.  Useful
generality may be scavenged later from proven parts, when a real second use
requires it.

## Current Package Direction

```text
src/vectorloom/
  tk_runtime/  # Vector Loom's own Tk application runtime environment
  canvas/      # Vector Loom drawing onto a supplied tkinter.Canvas
  demo/        # Current proving-ground program composition
  formats/     # Later Vector Loom file reading and validation
  viewer/      # Later read-only Vector Loom application
  editor/      # Later Vector Loom authoring application
```

`tk_runtime/` and `canvas/` are the current migration focus.  `formats/`,
`viewer/`, and `editor/` are planned homes, not active implementation work.

## Project-Wide Assumptions and Rules

- Tkinter widgets, callbacks, and Canvas operations run on the Tkinter main
  thread.
- Vector Loom's own applications use the shared App Shell to create the hidden
  root, run their application-specific setup, start the timer, and enter the
  main loop.
- The App Shell does not know which application it starts; a program bootstrap
  configures its nullary setup function.
- Canvas Context is the actual Tk Canvas renderer.  It is permitted to call
  Canvas methods and must not create a root, Toplevel, timer, or main loop.
- A client application remains authoritative for its own Tk environment when
  it uses the Canvas drawing library as a guest.
- Canvas items are projection artifacts, not durable Vector Loom state.

## Governing References

### B.A.D. Method (Bounded Agentic Development)

- `C:\lion\github\bad-development-ruminition\docs\distillation\basic-method.md`

### Project Folder Structure

- `C:\lion\github\lions-documents\raw\0012__python-2026-03-project-structure-agent-guide-short.md`

### Programming Guidelines

- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0100_globals.style-card.md`
- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0210_function_names.style-card.md`
- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0220_function_arguments.style-card.md`
- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0400_machines.style-card.md`
- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0410_registers.style-card.md`
- `C:\lion\github\lions-documents\coding-guidelines\style-cards\0800_python_rules.style-card.md`
- `C:\lion\github\lions-documents\raw\0010__lions-tkinter-development-conventions_v1.json`

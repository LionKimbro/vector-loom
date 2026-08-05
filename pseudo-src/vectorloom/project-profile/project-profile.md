# Project Profile — VectorLoom proving ground

## Target

- Language: Python 3.10 or later.
- Host platform: Windows 11 desktop application.
- Rendered package target: `src/vectorloom/`.
- User-interface toolkit: Python Tkinter.
- Direct-manipulation surface: `tkinter.Canvas`.
- Tk root policy: create and withdraw the root; visible application windows are
  `tkinter.Toplevel` windows.
- Test target: ordinary Python tests under `tests/`


## Purpose

Big Picture:
  Vector Loom is intended to help me make graphical applications with reusable content.
  This repository should develop three things:
  1. a data format for vector structures: 2d Canvas-comaptible tkinter structured and composable vector graphics
  2. a runtime for using these data formats
  3. an editr (or collection of editors) for authoring such data

Small Picture:
  Right now, we're just making a small core, in order to develop the concept:
  1. Designing a subset of the data format to come.
  2. Implementing a small run-time for testing the data format and it's rendering.

In short order, we should be adding composability, and then an editor.
There will likely eventually be multiple project targets, not just src/vectorloom/.
  src/vectorloom/  -- a visusalization runtime
  src/vectorloom-edit/  -- an editor

But for right now, it's just a small experimental runtime.


## Project-Wide Assumptions and Rules

- Tkinter widgets, their callbacks, and all Canvas operations run on the
  Tkinter main thread.
- Callbacks are thin adapters: they normalize toolkit input and advance or
  request the interaction cycle; they do not contain gesture identification behavior.
- The world model is authoritative for durable state.  Canvas items are
  projection artifacts, never the source of semantic truth.
- Raw input, perceptual facts, behavior, coordination, durable world
  mutation, and projection have separate owners.


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


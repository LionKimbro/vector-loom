```text
date: 2026-08-10
title: Vector Loom Project Structure Direction
purpose: Establish the BAD-first project structure for the reusable runtime,
  future editor, and future viewer.
```

# Vector Loom Project Structure Direction

Vector Loom is becoming a reusable technology with several ways to use it. The
project should separate the reusable runtime from the programs that present,
inspect, and edit Vector Loom designs.

The primary design work remains in `pseudo-src/`. Rendered Python under `src/`
follows that design; it does not become the primary architectural authority.

## Names

A **Python package** is importable code, such as `vectorloom`. A **Vector Loom
file** is a user's collection of Vector Loom designs, styles, and later related
assets and metadata.

Initially, the project should be one Python distribution containing the one
top-level import package `vectorloom`. It may provide several runnable entry
points. Separate Python distributions are a later option, not a current need.

## Intended Repository Tree

```text
vectorloom/
  README.md
  pyproject.toml

  docs/
    getting-started/       # What Vector Loom is and first use.
    guides/                # Using, embedding, authoring, and editing designs.
    reference/             # Public APIs and Vector Loom format reference.
    architecture/          # Boundaries, concepts, and project decisions.
    raw/                   # Numbered source/reference documents.

  pseudo-src/
    project/
      project-profile.md   # Project-wide assumptions and direction.
      adr/                 # Project-wide architectural decisions.
    vectorloom/            # BAD source for the importable vectorloom package.

  src/
    vectorloom/            # Rendered Python package.

  tests/                   # Tests of the rendered Python behavior.
  legacy/                  # Preserved earlier work; not current runtime code.
```

The folders under `docs/` other than `raw/` are the intended human-facing
documentation home. `pseudo-src/` is also documentation, but it is the
normative BAD design layer for both people and AI working on the software.

## BAD and Source Mirror

Where BAD describes a renderable Python region, its `modules/` subtree should
mirror the `src/` import tree:

```text
pseudo-src/
  vectorloom/
    readme.md
    aspects/
    data-structures/
    interfaces/
    modules/
      core/
      tkinter/
      formats/
      editor/
      viewer/

src/
  vectorloom/
    core/
    tkinter/
    formats/
    editor/
    viewer/
```

For example, a renderable module design at
`pseudo-src/vectorloom/modules/tkinter/canvas-context.md` would name a target such as
`src/vectorloom/tkinter/canvas_context.py`.

`aspects/`, `data-structures/`, and `interfaces/` deliberately do not mirror
Python paths. They describe contracts, shared structures, and external
capabilities used across multiple modules. Project-wide decisions likewise
belong with the project, rather than being treated as the property of one
runtime subpackage.

If the project later gains another top-level Python package, it gains a
matching sibling BAD source tree. For now, `editor/` and `viewer/` are
subpackages of `vectorloom`, because they will share its runtime closely.

## Intended `vectorloom` Package Boundaries

```text
src/vectorloom/
  core/       # format-independent design, traversal, geometry, and transforms
  tkinter/    # Tkinter runtime and Canvas realization of core drawing
  formats/    # reading and validating Vector Loom documents
  editor/     # runnable editor application
  viewer/     # runnable read-only package viewer
```

### `core/`

`core/` contains the reusable, format-independent parts of rendering a Vector
Loom design: traversal, coordinate-frame work, and design-facing operations.
It must not create Tk widgets or call Canvas methods.

### `tkinter/`

`tkinter/` owns the Tk runtime ground and the realization of Vector Loom
drawing on a `tkinter.Canvas`. It adapts core drawing results to Canvas items,
including the current immediate-mode connector registry and Canvas tag
contract.

### `formats/`

`formats/` owns reading and validating Vector Loom documents, beginning with
VectorLoom Basic. It turns document data into forms the runtime can use. It
does not create windows, own Canvas drawing, or decide editor behavior.

### `editor/`

`editor/` is a runnable application for authoring and changing Vector Loom
files. It composes `core/`, `formats/`, and `tkinter/`; it does not absorb
their reusable responsibilities.

### `viewer/`

`viewer/` is a runnable, read-only application for inspecting and presenting
the contents of a Vector Loom file. It shares the runtime and format
reading layers with the editor, but owns no editing behavior.

## Public Use and Entry Points

The distribution should eventually support these three modes of use:

```text
import vectorloom                 # Embed Vector Loom in another Python program.
vectorloom-editor                 # Run the editor.
vectorloom-viewer                 # Run the viewer.
```

The exact entry-point names and public import API are not decided by this
document. They should be added once the corresponding package boundaries are
rendered and usable.

## Migration Direction

The current proving-ground modules should not simply be moved wholesale. Their
responsibilities must first be assigned to the new boundaries:

- Transform and design-traversal responsibilities move toward `core/`.
- Tk root, window, timer, Canvas item, and Canvas-tag responsibilities move
  toward `tkinter/`.
- The current host-window kinetic experiment becomes a demonstration or test
  client, not part of the reusable runtime core.
- Format reading begins in `formats/` from the VectorLoom Basic document
  definition.
- Editor-specific work begins only in `editor/`, consuming the isolated core,
  format, and Tkinter layers.

The migration is incremental. Current behavior remains testable while one
bounded region at a time receives a new BAD home and is then rendered there.

## See Also

- [`0015__vectorloom-basic.json`](0015__vectorloom-basic.json) — current
  VectorLoom Basic document definition.
- [`0018__instance-assembly-and-mutation-direction.md`](0018__instance-assembly-and-mutation-direction.md)
  — provisional future direction for durable instances and mutation.
- [`ADR 0005: Retained mode or direct draw`](../../pseudo-src/vectorloom/adr/0005-retained-mode-or-direct-draw.md)
  — current immediate-mode runtime direction.

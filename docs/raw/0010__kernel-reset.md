```
date: 2026-08-05
title: Kernel Reset
```

# Kernel Reset

Vector-Loom is restarting from a smaller, more direct development approach. The earlier work explored transport formats, editor architecture, hierarchy, transforms, undo/redo, reuse, and integration concerns, but too much structure accumulated before the project’s essential mechanism had been proven clearly.

The immediate goal is now to build the smallest working core: basic vector objects, local coordinate systems, named attachment points, hierarchical transforms, and reliable save/reload behavior. Editing tools, richer transport features, reusable component systems, and integration concerns will follow only after this foundation works convincingly.

The previous implementation is retained under `legacy/first_attempt/` as reference material and a source of potentially reusable code. New work begins in `src/vectorloom/`. This structure is provisional: unsuccessful attempts may be moved into `legacy/`, and successful work may be reorganized once its shape becomes clear.

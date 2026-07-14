# How to Drop `record` (design memo, deferred)

**Status:** planned, intentionally deferred. `rt` has already been dropped from
TkVillage window-callback signatures. `record` is still passed for now. This
document captures everything we discussed so a future conversation can pick it
up cold.

**Do not implement yet.** The record drop is too involved for the current
period, and it depends on TkVillage-side changes that should land first. This
memo is the briefing for that future work.

---

## 1. The ethos it points toward

The direction is to make TkVillage's execution model *explicit* and to align it
with Lion's programming style:

- **Contextual state belongs in globals; pass only what varies.** The window
  `record` is not a varying parameter — it is ambient context ("who am I right
  now"). So it belongs in a well-known runtime location, not in every callback
  signature.
- **The runtime acts as one window at a time**, like a small operating system
  with a "current process." When TkVillage invokes code for window A, the
  runtime *is* window A, and the current record refers to A. This is already how
  the tick loop behaves (it processes one window's events / reducer / projection
  synchronously); the change just names that focus.
- **The GUI layer is a semantic input encoder, not a place where behavior
  happens.** Tk callbacks translate outside-world signals into queued semantic
  events or into present-tense facts. They never perform application logic
  directly. ("A Tk callback may translate; it may not decide.")

The point is not shorter signatures. It is one principle from which several
rules fall out: *the runtime acts as one window at a time, and the GUI layer is
an input encoder.*

## 2. Target callback model

Drop `record` from window-kind callbacks:

```python
create()
make_initial_state(key=None, payload=None)
reduce_event(state, event)
project()
on_show()
on_close()
on_tick()
```

Inside a runtime-invoked callback, get the record ambiently:

```python
record = village.current_record()   # or rt.g["record"]
```

**Invariant:** only one window's code is actively running at a time. The runtime
sets the current record immediately before invoking a callback and restores it
immediately after, via a disciplined helper:

```python
def call_with_record(record, fn, *args):
    previous = rt.g.get("record")
    rt.g["record"] = record
    try:
        return fn(*args)
    finally:
        rt.g["record"] = previous   # save/restore, not assert-None: robust to nesting
```

Provide `village.current_record()` as the accessor and have it **raise** if read
outside a window invocation — turn the footgun (below) into a loud, immediate
failure instead of a silent wrong-window read.

## 3. The footgun (the crux of why this is non-trivial)

`rt.g["record"]` is valid **only inside runtime-invoked callbacks**
(create / project / reduce / on_tick / lifecycle). It is **stale or None**
inside:

- Tk widget command callbacks (a button's `command=lambda: ...`)
- raw `<Motion>` / `<ButtonPress>` bindings (they fire *outside* the tick)
- worker threads

The old explicit `record` parameter made it impossible to grab the wrong one.
The ambient global makes it possible. The disciplined answer: **callbacks that
fire outside runtime invocation must capture `window_id` (or the record) in a
closure at registration time**, never read the ambient global at event time.

Vector Loom already follows this pattern (every button/key/RAW callback closes
over `record["window_id"]`), so it is compatible in spirit — but a naive user
who writes `record = current_record()` inside a button handler gets a subtle
bug. This is the reason to route callback registration through TkVillage (next).

## 4. The bigger answer: input ports, not just wrapped callbacks

Rather than only "wrap all callbacks so the record is set," make **all Tk
callback registration go through TkVillage helpers**, and declare raw `.bind()`
/ `command=` non-canonical escape hatches. Three port kinds:

1. **Event ports** — chrome (buttons, menus, dialogs, WM protocols) →
   queued **semantic events**. Protocol events auto-forward, e.g.
   `WM_DELETE_WINDOW` → `{"type": "WINDOW_CLOSE_REQUESTED"}`.
   ```python
   village.button(parent, text="Save", event={"type": "SAVE_REQUESTED"})
   village.bind_event(entry, "<Return>", {"type": "TEXT_SUBMITTED"})
   ```
2. **Fact ports** — continuous / manipulation-surface input → updates
   **tick-sampled RAW facts** (not the reducer).
   ```python
   village.bind_fact(canvas, "<Motion>", "pointer", make_pointer_fact)
   ```
3. **Raw ports** — advanced adapter code, still record-wrapped. The named
   escape hatch.

All three set the current record for the duration and funnel exceptions to the
runtime log (re-raising in `test_mode`, like `tick_once`). Record ownership is
best captured at **registration time** (uniform across `bind`, `command`,
`protocol`, `after`, variable traces); walking `event.widget` up to the
`Toplevel` is a convenience fallback that only works for inputs that have a
widget.

## 5. Event vs. fact is chosen by ENGINE, not by widget type

The sharpest rule from the discussion: whether an input becomes a semantic event
or a fact depends on **which engine consumes it**, i.e. the widget's *role* —
not on the Tk input type.

- **Chrome → semantic event** (feeds the Discrete Engine / reducer).
- **Manipulation surface → fact** (feeds the Continuity Engine / tokenizers).

Proof from Vector Loom: the canvas `<ButtonPress-1>` is a **fact**
(`button1_down`), not a semantic event, because the select/drag/resize organisms
must tokenize the press *alongside* motion. Meanwhile the toolbar buttons post
semantic events directly. Same physical "click," opposite treatment, decided by
role. Continuous data must **not** spam the reducer as meaning — undo/redo
navigates completed acts, and per-frame motion is not a completed act.

## 6. Continuous facts are SAMPLED, not event-pushed

CIRA's canonical runtime loop step 2 is literally "Update RAW facts from
toolkit/input" — every iteration. That is **polling**, and RAW is defined as a
"faithful uninterpreted input snapshot" with `.current` / `.previous`. So the
pure form:

- Each tick, **sample** pointer position (`winfo_pointerxy()` minus the widget
  root origin) into RAW; the tokenizer derives `moving`, `dx`, `dy` from
  current-vs-previous. No `<Motion>` binding is needed for manipulation.
- This is more honest (a fact is sampled), cheaper and self-throttling (O(1) per
  tick regardless of motion rate), robust to Tk grab semantics, and adds no
  latency (perception happens at the tick anyway).

Vector Loom's current `bind_raw` on `<Motion>` is a pragmatic shortcut that this
model would replace with a tick-time `sample_pointer()`.

## 7. Live input facts + motion buffer (TkVillage as first handler)

- **TkVillage maintains canonical live input facts** (buttons down, Ctrl/Shift/
  Alt) by being the true first handler.
  - **Modifiers** come from `event.state` on any event (reliable): Shift
    `0x0001`, Control `0x0004`, Alt `0x0008` / `0x20000` (Windows).
  - **Button-down must be maintained from press/release *edges*, NOT the
    `event.state` bit**, because the bitmask lies at exactly the two moments that
    matter: on `<ButtonPress-1>` the `0x0100` bit is not yet set, and on
    `<ButtonRelease-1>` it is still set. Use edges for buttons; use `event.state`
    for modifiers (and as a motion-time cross-check).
- **Motion buffer:** accumulate the list of motion points since the last tick,
  make it available to the tick, and **clear it after the tick runs** (not
  forever). `RAW.current.pointer` is the latest sample (for manipulation);
  `RAW.motion_points` is the buffered list (for ink fidelity, where sub-tick
  detail matters). Manipulation uses the sample; only stroke capture needs the
  buffer.

## 8. Fact scope and reducer purity

- **Facts are window-local by default** (RAW lives on the record). Only
  truly-global facts belong in `rt.g`: which window the pointer is over
  (`winfo_containing`), tick count / wall-clock. `rt.g["pointer"]` as a single
  global is a subtle mis-default in a multi-window world.
- **Keep the reducer pure.** `reduce_event(state, event)` must NOT read
  `current_record()` — the Discrete Engine stays referentially transparent
  (state + event in, new_state + effects out). Dropping `rt` actually *helps*
  this; the record drop must not undo it. Presentation callbacks
  (create / project / on_tick) may read the current record; the reducer may not.

## 9. Impact on Vector Loom (what actually changes here)

Small and low-risk — we are already aligned in spirit:

- `create`, `project`, `on_tick` → drop the `record` param, add
  `record = village.current_record()` as line one.
- `make_initial_state(key, payload)` → unchanged (doesn't need the record).
- `reduce_event(state, event)` → already pure; gets `doc` via
  `world.get(state["doc_path"])`, not from the record. Keep it that way.
- Thin Tk callbacks (toolbar buttons, key bindings, `bind_raw` RAW writers)
  already close over `record["window_id"]` — compatible. Over time, migrate them
  to `village.bind_event` / `village.bind_fact` / `village.button`.
- Tests: pure tests call internal functions directly (unaffected); Tk-loop tests
  drive via `run_ticks`, which would set the current record for them.

## 10. Sequencing and dependencies

1. **TkVillage first.** The record model (current_record + invariant +
   call_with_record), the input-port/binding API, live input facts, and the
   motion buffer are TkVillage-side changes. A separate recommendations document
   is intended to go to the TkVillage AI coding agent for this.
2. **Then conform Vector Loom** to the new TkVillage (Section 9).
3. Only after both: consider deleting old-signature compatibility support.

A short-lived compatibility shim (callbacks may optionally still accept
`record`) is acceptable during migration, but the target model is
`create()` / `reduce_event(state, event)` with `current_record()` as the current
active window record — not "callbacks may optionally accept record."

## 11. Open decisions for the future conversation

- Accessor name/shape: `village.current_record()` (recommended, raises out of
  context) vs raw `rt.g["record"]`.
- Whether to enforce "no raw `.bind()` / `command=`" by lint/review only (Python
  cannot truly forbid it) — recommended: declare non-canonical, enforce by
  convention.
- Exact fact-port API surface and how ink-stroke capture opts into the motion
  buffer.
- Tone/scope of the recommendations doc handed to the TkVillage agent.

# Module — Tk Runtime

## Render Target

`tk_runtime.py`

## OWNS

- The shared permanent `g["root"]` value containing the hidden Tk root.
- The shared `g["periodic-callback"]` value containing the periodic callback.
- Creating and immediately withdrawing that root.
- General root-level Tk data needed by other modules
  - Such as configuration of the tk runtime system, broadly.
    - presently, config["quit-when-no-toplevels-remain"]
    - presently, config["periodic-timer-interval-in-ms"]
- General root-level Tk operations needed by other modules.
- Returning monotonic millisecond timestamps for Tk callback adapters.


## READS

- The current Tk root's child-widget list.
- Python's monotonic clock.


## CALLS

- Tkinter root and Toplevel operations needed to create/withdraw the root and
  inspect its live Toplevel children.
- Python `time.monotonic()` for timestamp generation.


## MAY SAFELY ASSUME

- App Shell creates the application composition in the Tkinter main thread.
- Visible application windows are Toplevels whose owner is `g["root"]`.
- g["periodic-callback"] will be written to before the main loop begins


## ENSURES

- The root is withdrawn before visible application windows are created.
- Active-Toplevel checks do not require a window module to inspect a sibling
  window's widget registry.

## DOES NOT OWN

- System orchestration, application configuration, or calling `mainloop()`.
- Calling `after()`, `after_cancel()`, or `quit()`.
  (The `timer` module does that.)
- Timer interval/callback/after-id registers or the timer recurrence policy.
- Any Toplevel's widget handles, event bindings, interaction state, or Canvas
  drawing.


## Sketch

```python
g = {
    "root": None,
    "periodic-callback": None    # nulary function, i.e. fn()
}

config = {
  "quit-when-no-toplevels-remain": true,
  "periodic-timer-interval-in-ms": 50
}


def reset():
    (re-establish the default values for g and config)


def create_and_withdraw_root():
    g["root"] = tk.Tk()
    g["root"].withdraw()


def has_active_toplevels():
    Return true if there are any live toplevels that belong to g["root"].


def now_ms():
    return int(time.monotonic() * 1000)


def perform_periodic_callback_per_timer():
    if periodic-callback is defined,
        call it
```

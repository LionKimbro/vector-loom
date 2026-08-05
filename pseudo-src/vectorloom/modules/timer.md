# Module — Periodic Timer

## Render Target

`timer.py`

## OWNS

- The `start_timer()` and `cancel_timer()` operations.
- Registering recurring Tk `after()` callbacks.
- Scheduling the next occurrence after a timer callback has run.
- Cancelling or replacing a prior scheduled callback.
- If the configured tk-runtime policy is to stop the main loop once
  there are no more Toplevel windows, then this module takes responsibility
  for checking the condition, and then issuing a stop to the mainloop,
  once the condition is met.
- Calling perform_periodic_callback_per_timer() on the tk-runtime
  once per period.

## READS

- The period from tk-runtime's configuration.
- Tk Runtime's root operations.

## CALLS

- `tk_runtime.g["root"]` for its `after()`, `after_cancel()`, and `quit()`
  operations.
- `tk_runtime.perform_periodic_callback_per_timer()`
- `tk_runtime.has_active_toplevels()` after each timer callback,
  if the runtime is configured for shutting down when there are
  no active toplevel windows.


## MAY SAFELY ASSUME

- Application composition chooses what recurring work occurs.
- App Shell makes the initial call to `start_timer()`.
- Someone else will stop the main loop, if the system is NOT configured
  for closing automatically when there are no Toplevel windows.


## ENSURES

- Periodic scheduling is reusable and does not know whether it drives an
  interaction cycle, polling task, animation, or other work.
- It schedules the next occurrence without embedding application behavior.


## DOES NOT OWN

- Tk root creation, visible Toplevels, widget bindings, interaction-cycle
  behavior, the semantics of the scheduled callback, or closing a Toplevel.
- The orchestration decision about when a caller starts or cancels the timer.


## Sketch

```text
g = {
  "timer-handle": None
}

def start_timer():
    Call _schedule_next(), directly.

def cancel_timer():
    cancel the .after found at g["timer-handle"]
    reset g["timer-handle"] to None
    Do not guard against None or another invalid handle: calling cancel_timer()
    without a valid scheduled handle is a programmer error and should fail
    visibly at the Tk boundary.

def _on_timer():
    Call perform_periodic_callback_per_timer() on tk-runtime.
    if tk-runtime is configured for quit-when-no-toplevels-remain:
        Check if there are any toplevels, using tk-runtime fn for this.
	If there are no toplevels:
	    issue the tkinter mainloop stop fn call
	    return early, right here
    in general, though, just:
        _schedule_next()

def _schedule_next():
    Read the tk-runtime's configured config["periodic-timer-interval-in-ms"].
    Create an .after on the main loop, and store the handle to it in g["timer-handle"].
```

# Module — Application Shell

## Render Target

`app_shell.py`

## OWNS

- Program setup orchestration.
- Loading and applying program configuration (if any.)
- Making the initial call to `timer.start_timer()` as part of application
  composition.
- Kicking off the first window's creation.
- Entering the Tk event loop after application composition is complete.

## READS

- nothing

## CALLS

- `tk_runtime.create_and_withdraw_root()`.
- `timer.start_timer()`.
- `canvas_host_window.create_canvas_host_window()`.

## MAY SAFELY ASSUME

- The setup code will do what it needs to do, in order to make sure
  that there's something meaningful that happens when the periodic
  timer ticks.

## ENSURES

- The application is setup before calling 'mainloop()'.

## DOES NOT OWN

- Visible application windows.
- Event-handler registration.
- The implementation of timer scheduling or cancellation.
- Periodic timer response.


## Sketch

```python
function main():
    tk_runtime.create_and_withdraw_root()
    timer.start_timer()
    app_specific_setup()
    tk_runtime.g["root"].mainloop()

def app_specific_setup():
    "Isolate app-specific setup here."
    import canvas_host_window
    canvas_host_window.register_periodic_timer_callback()
    canvas_host_window.create_canvas_host_window()
```

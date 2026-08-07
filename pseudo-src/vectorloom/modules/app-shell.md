# Module — Application Shell

This is the outermost shell of the program. It brings the shared
runtime to life, assembles this application’s particular pieces, and
then lets the program run.


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
- `canvas_host_window.start_canvas_host_demo()`.


## MAY SAFELY ASSUME

- The setup code will do what it needs to do, in order to make sure
  that there's something meaningful that happens when the periodic
  timer ticks.


## ENSURES

- The application is setup before calling 'mainloop()'.


## DOES NOT OWN

- Visible application windows.
- Event-handler registration.
- The implementation of timer (re-)scheduling, or timer cancellation.
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
    canvas_host_window.create_canvas_host_window()
    canvas_host_window.start_canvas_host_demo()
```

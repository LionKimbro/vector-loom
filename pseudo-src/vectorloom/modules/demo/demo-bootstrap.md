# Module — Demo Bootstrap

This module composes the current kinetic Canvas demonstration from the shared
Tk runtime environment and the Canvas drawing library.

## Render Target

`src/vectorloom/demo/demo_bootstrap.py`

## OWNS

- Configuring App Shell to run the demo-specific setup function.
- Creating the Canvas Host Window for this demonstration.
- Starting the Canvas Host Demo after its host window exists.

## CALLS

- `app_shell.main()`.
- Canvas Host Window's `create_canvas_host_window()`.
- Canvas Host Demo's `start_canvas_host_demo()`.

## MAY SAFELY ASSUME

- App Shell creates and withdraws the Tk root before it invokes this module's
  setup function.
- Canvas Host Demo expects a live host Canvas.

## ENSURES

- The current proving-ground demonstration is composed without App Shell
  knowing about it directly.

## DOES NOT OWN

- Tk root, timer, main-loop, Canvas host, Canvas drawing, transform, or demo
  animation implementation.

## Sketch

```python
def main():
    app_shell.config["app-specific-setup"] = set_up_demo_application
    app_shell.main()


def set_up_demo_application():
    canvas_host_window.create_canvas_host_window()
    canvas_host_demo.start_canvas_host_demo()
```

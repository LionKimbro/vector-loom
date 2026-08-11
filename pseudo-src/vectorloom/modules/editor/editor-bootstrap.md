# Module — Editor Bootstrap

This module configures the shared App Shell to run the Vector Loom editor.  It
composes the Editor Window and the editor CIRA Runtime without putting editor
knowledge into Tk Runtime's generic App Shell.

## Render Target

`src/vectorloom/editor/editor_bootstrap.py`

## OWNS

- Installing the editor's nullary setup function at
  `app_shell.config["app-specific-setup"]`.
- Creating the Editor Window during that setup.
- Installing the editor Runtime's update-cycle callback into Tk Runtime.

## CALLS

- `app_shell.main()`.
- Editor Window creation.
- Interaction Runtime initialization and update-cycle callback.

## DOES NOT OWN

- Tk root, timer, generic App Shell, editor input interpretation, reduction,
  world mutation, history, or projection.

## Sketch

```python
def main():
    app_shell.config["app-specific-setup"] = set_up_editor_application
    app_shell.main()


def set_up_editor_application():
    editor_window.create_editor_window()
    interaction_runtime.initialize_editor_runtime()
    tk_runtime.g["periodic-callback"] = interaction_runtime.run_update_cycle
```

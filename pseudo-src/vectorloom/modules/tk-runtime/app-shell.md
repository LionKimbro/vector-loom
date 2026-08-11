# Module — Application Shell

This module brings one configured Vector Loom application to life within the
shared Tk runtime.  It owns the common startup sequence, but does not know
whether the configured application is the demo, viewer, or editor.

## Render Target

`src/vectorloom/tk_runtime/app_shell.py`

## OWNS

- The fixed-shape App Shell `config` bundle.
- Checking that an application-specific setup function has been configured.
- The common sequence that creates the hidden Tk root, invokes that setup
  function, starts the periodic timer, and enters Tk's main loop.

## READS

- `config["app-specific-setup"]`.
- Tk Runtime's root after it has been created.

## CALLS

- `tk_runtime.create_and_withdraw_root()`.
- The configured nullary application-specific setup function.
- `timer.start_timer()`.
- Tk Runtime root's `mainloop()`.

## MAY SAFELY ASSUME

- After App Shell has validated `config["app-specific-setup"]`, the configured
  setup function creates the application's first visible window
  and installs any periodic callback it requires.

## ENSURES

- An unset application-specific setup function fails clearly before Tk startup
  begins.
- The configured application setup has completed before the periodic timer is
  started.
- Application composition is complete before Tk's event loop begins.

## DOES NOT OWN

- The identity, imports, windows, Canvas setup, timer callback meaning, or
  cleanup behavior of the demo, viewer, or editor.
- Tk root creation policy, timer scheduling details, or window lifecycle.
  Those belong to sibling Tk Runtime modules.
- Vector Loom Canvas drawing.

## Sketch

```python
config = {
    "app-specific-setup": None,
}


def main():
    app_specific_setup = config["app-specific-setup"]
    if app_specific_setup is None:
        raise RuntimeError(
            "App Shell needs config['app-specific-setup'] before main()."
        )

    tk_runtime.create_and_withdraw_root()
    app_specific_setup()
    timer.start_timer()
    tk_runtime.g["root"].mainloop()
```

## See Also

- `../demo/demo-bootstrap.md` — the current demo's application composition.
- `../viewer/viewer-bootstrap.md` — future viewer composition placeholder.
- `../editor/editor-bootstrap.md` — future editor composition placeholder.

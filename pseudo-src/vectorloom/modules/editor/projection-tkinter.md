# Module — Editor Projection: Tkinter Controls

This is the Tkinter-control part of Editor Projection.  It defaults to the
overall boundary, reads, and exclusions declared in `projection.md`.

## Render Target

Contributes to `src/vectorloom/editor/projection.py`.

## OWNS

- Reconciling Designs and Styles Treeview rows with their projected library
  entries.
- Mirroring committed editor selection into the corresponding Treeview when
  its selected item is present.
- Inspector widgets and their temporary input-queue diagnostic.
- Status-bar text describing the committed active drawing tool.

## ENSURES

- While no library is loaded, each Treeview contains one temporary,
  non-library placeholder row: `(no designs loaded)` or `(no styles loaded)`.
- Treeview rows are reconciled, not wholesale replaced on every projection
  pass.  Unchanged items retain their Treeview identities.
- Projection selects the committed selection only when its projected item is
  present.  It clears the physical Treeview selection when the committed item
  is absent; it does not change committed selection itself.
- The Runtime `PROJECTING` stage suppresses the Treeview callback caused by
  that physical selection mirroring.
- The temporary diagnostic reads Event Queue's drained `recent-events` history,
  never the pending input queue.

## DOES NOT OWN

- Treeview widget handles, inspector-frame widget handle, or status-bar widget
  handle; Editor Window owns those physical controls.
- Canvas realization, camera state, or inspector input interpretation.

## Pseudocode

```text
def project Tkinter controls:
    reconcile Designs Treeview rows with World Model designs
    reconcile Styles Treeview rows with World Model styles
    mirror committed selection into its corresponding Treeview, if present
    replace inspector-frame contents with the temporary recent-input diagnostic
    set status-bar text from the committed active tool


def reconcile Treeview rows(tree, projected entries):
    retain rows whose stable entry identities remain present
    add rows for newly present entry identities
    remove rows for no-longer-present entry identities
    update presentation of retained rows when their visible data changed


def project temporary recent-input diagnostic:
    clear inspector-frame
    show "Recent raw input"
    show one compact row for each of the last ten Event Queue recent-events
```

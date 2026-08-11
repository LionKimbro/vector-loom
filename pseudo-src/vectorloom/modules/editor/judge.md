# Module — Editor Judge

This module coordinates editor interaction resources without knowing what an
interaction means.

## Render Target

`src/vectorloom/editor/judge.py`

## OWNS

- Inspectable resource leases and diagnostic coordination state.
- `CHECK` and `COMMIT` permission decisions.
- Releasing stale leases when their organisms return to idle.

## ENSURES

- At most one exclusive pointer episode owns the pointer at once.
- The Judge performs no hit testing, gesture behavior, reduction, mutation, or
  projection.

## DOES NOT OWN

- RAW/DERIVED facts, organism state transitions, editor workspace state, or
  library data.

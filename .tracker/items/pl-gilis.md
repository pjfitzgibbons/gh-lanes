---
title: "plan report time: estimate against tracked time"
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 12400
lane: cli
milestone: phase-1
blocked_by:
  - "pl-hahuk - Timewarrior adapter for tt: TimeSource, snapshot, ActualTime"
  - "pl-bogeh - index.py: SQLite build, v_work view, plan reindex"
---
`plan report time [--milestone M]` and its `--json` form, as design 0002 §8 specifies: per item, the estimate, estimated hours (`estimate × hours_per_point`), the `actual_time` snapshot and the variance, then totals and observed hours per point against the configured value.

- Only `Done` items with a snapshot count toward the totals; an item without one is listed and counted in the footnote.
- An issue closed as not planned (`stateReason` is `NOT_PLANNED`) is left out of the report and its totals, and a last line names how many were left out.
- A parent's row sums its children for display only; totals count each child once.

Tests: a fixture with completed, not-planned, no-snapshot and parent-with-children items, asserting the rows, the totals and the not-planned line.

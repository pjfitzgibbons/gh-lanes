---
title: Post-merge hook reports closes; reconcile --closed snapshots tracked time
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 12300
lane: github
milestone: phase-1
blocked_by:
  - "pl-hahuk - Timewarrior adapter for tt: TimeSource, snapshot, ActualTime"
---
C9. Implements design 0002 §6 and §6.1: collect an item's tracked time when its issue closes, triggered by pulling the merge.

- Reconcile writes `actual_time` in the same file write that moves a closed issue's item to `Done`. A `TimeSourceError` still reaches `Done`, prints one line, and leaves `actual_time` absent
- `plan reconcile --closed`: only the closed-but-not-`Done` case; refreshes the index first, ignoring `stale_after_minutes`
- `plan hooks install`: writes `.git/hooks/post-merge` running a dry `plan reconcile --closed --quiet || true`, alongside the pre-commit hook from #24. The hook writes nothing: item-file changes go through a branch via `--apply`. Both hooks call `plan` by the absolute path of the executable that ran the install. Refuses to overwrite a hook it did not write
- Tests from design 0002 §11: fake `TimeSource` (entries, none, raises), `--closed` leaves new issues alone, `hooks install` in a temporary repo (absolute path, refuses to overwrite)

---
title: "Timewarrior adapter for tt: TimeSource, snapshot, ActualTime"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 12200
lane: model
milestone: phase-1
---
C9. Implements design 0002 §5 and §10: the `TimeSource` interface and its first adapter, which reads the intervals `tt` writes to Timewarrior.

- `timekeeping/__init__.py`: `WorkKey`, `TimeEntry`, `TimeSource`, `TimeSourceError`, `load()`
- `timekeeping/total.py`: pure `snapshot()` (dedupe by `source_id`, sum closed entries, count running ones)
- `timekeeping/timewarrior.py`: `timew export <tag>`, parsed leniently. Reads raw intervals, never `tt report`, which rounds to 30-minute blocks
- `ActualTime` in `model.py`; `hours_per_point` (default 8.0) and `time_source` in `config.py`
- Tag is `owner/repo#N`, the form `tt` already writes (design 0002 §4). No change to `tt`
- Tests: `snapshot()` cases from design 0002 §11, and the adapter against a recorded `timew export` fixture with synthetic tags and times

`tt` keeps an interval open while you work on the issue's branch, so a snapshot taken at merge can see a running entry. It is counted in `running`, left out of the total, and warned about.

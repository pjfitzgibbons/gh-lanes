---
title: "plan.py: duration, lane heads, next/ready/why, schedule"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 11000
lane: engine
milestone: phase-1
blocked_by:
  - "pl-kabij - Design 0001: next/ready without lane heads; §8.5 repo scope"
---
Pure. `next` selection gets a case per branch; an item blocked by an open issue is not a candidate, with the edges read from the index. `duration_days = max(1, ceil(estimate / points_per_week * 7))`, no weekend exclusion.

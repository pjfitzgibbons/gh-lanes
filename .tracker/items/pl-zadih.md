---
title: freeze and mirror
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 11500
lane: cli
milestone: phase-1
blocked_by:
  - "pl-kufib - plan.py: duration, lane heads, next/ready/why, schedule"
  - "pl-mikad - cli.py: query commands with --json"
---
`freeze <milestone> [--apply] [--rebaseline]` writes baselines; rebaseline records a reason. `mirror [--apply]` writes the `[N]` title prefix; its write strategy follows the 1.21 spike.

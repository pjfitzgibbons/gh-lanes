---
title: "cli.py: query commands with --json"
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 11200
lane: cli
milestone: phase-1
blocked_by:
  - "pl-taroz - validate.py: all 17 rules, tests first"
  - "pl-kufib - plan.py: duration, lane heads, next/ready/why, schedule"
---
`status`, `list`, `show`, `next`, `ready`, `why`, `validate`. Typer, thin; every command delegates to core.

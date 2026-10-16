---
title: "Write commands: new, set, ice, schedule"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 11400
lane: cli
milestone: phase-1
blocked_by:
  - "pl-taroz - validate.py: all 17 rules, tests first"
  - "pl-mikad - cli.py: query commands with --json"
  - "pl-gaseb - git.py: repo root and commit helper"
---
`set` writes tracker-owned fields only, all or nothing (design 0001 §8.4): it rejects 8/13 and any other failing rule, and writes nothing if one check fails. It has no dependency flags; dependencies are edited in GitHub or with `gh issue edit --add-blocked-by`. `new` is GitHub first, then the file.

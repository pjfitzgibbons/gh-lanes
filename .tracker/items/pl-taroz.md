---
title: "validate.py: all 17 rules, tests first"
type: feat
status: Icebox
estimate: 3
priority: P2
ordinal: 10900
lane: engine
milestone: phase-1
---
One function per rule, plus the two milestone rules from 1.2. Write the tests before the rules. Exit 1 on any ERROR.

Cycle detection runs over the pulled blocked-by graph and gets a case per branch: GitHub rejects self-dependencies and two-issue cycles itself, but accepts longer cycles (verified on `gh` 2.102.0). There are no self-dependency or "dependency resolves" rules, because GitHub enforces both.

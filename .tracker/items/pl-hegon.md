---
title: "Design 0003: plan-board cards read and commit gh-plan"
type: chore
status: Icebox
estimate: 2
priority: P2
ordinal: 20720
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
---
### Task
Amend [design 0003](../../docs/design/0003-plan-board.md) for [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md): `worktask-start` checks the item on `origin/gh-plan`, the ready list reads `git show origin/gh-plan:ready.yml`, a card commits and pushes item edits in `.tracker/`, and `worktask done` runs `plan done`.

### Guardrails
- Cards still list every command verbatim; the runner refuses a card whose steps differ from its recipe.
- The `rebase` recipe stays for a PR behind on code; only the plan churn it handled goes.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: design 0003 recipes, ready list and failure table
- [x] L11 Invariants: invariant 5 as ADR 0010 §3.5 states it, with gh-plan pushes from cards
- [ ] L12 Offline and concurrency
### Done
- [ ] The `worktask-start` row checks against `origin/gh-plan`.
- [ ] A recipe commits named paths in `.tracker/` and pushes `gh-plan`.
- [ ] L10: no line in design 0003 reads `ready.yml` from `origin/<default>`.
- [ ] L11: the design's statement of invariant 5 matches ADR 0010 §3.5.

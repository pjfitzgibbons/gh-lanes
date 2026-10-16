---
title: "Architecture, design 0001 and requirements for the gh-plan branch"
type: chore
status: Todo
estimate: 3
priority: P2
ordinal: 20700
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
---
### Task
Restate [architecture](../../docs/architecture.md) §3, §7, §8 and §10, [design 0001](../../docs/design/0001-phase-1.md) §5 *Discovery*, and [requirements](../../docs/requirements.md) `C5` and `D6` for [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md): `.tracker/` as a worktree of `gh-plan`, the symlink and common-dir fallback, `plan done` and `merge: <sha>`, and the commands without `.tracker/`.

### Guardrails
- The docs follow ADR 0010; a change to the decision goes back to the ADR first.
- §7's diagram is redrawn for `gh-plan`, through the graphic-designer agent.

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
- [x] L10 Docs impact: architecture §3, §7, §8, §10, design 0001 §5, requirements C5 and D6
- [x] L11 Invariants: invariants 2, 3 and 5 in §10 read as ADR 0010 §3.5 states them
- [ ] L12 Offline and concurrency
### Done
- [ ] Architecture §3's tree shows `.tracker/` as the `gh-plan` worktree, and §7 has a *Done* subsection for `plan done`.
- [ ] §8 has a row for each case in ADR 0010 §3.4 and for a rejected push to `gh-plan`.
- [ ] Design 0001 §5 describes the symlink and the `--git-common-dir` fallback.
- [ ] L10: `C5` and `D6` name `gh-plan`.
- [ ] L11: §10's invariants 2, 3 and 5 match ADR 0010 §3.5.

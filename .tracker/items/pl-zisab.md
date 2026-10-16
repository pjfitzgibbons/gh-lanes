---
title: "worktask: the .tracker symlink, gh-plan starts and plan done"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 20730
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
---
### Task
Change the worktask skill for [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md): `plan-start` commits to `gh-plan` instead of the default branch, `start` makes the `.tracker` symlink in the new worktree, and `done` records `plan: done <id>` with `merge: <sha>` from the `gh pr view` it already runs.

### Guardrails
- The only remote write stays a `git push` of the tool's own commits, now to `gh-plan`.
- A tool commit touches one item plus `ready.yml`, built through a temporary index and moved by compare-and-swap.

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
- [x] L10 Docs impact: the worktask SKILL.md
- [x] L11 Invariants: invariants 3 and 5 hold for plan-start and the new done commit
- [ ] L12 Offline and concurrency 
### Done
- [ ] `start` makes the symlink, and `git status` in the new worktree is clean.
- [ ] `done` commits `plan: done <id>` with `merge: <sha>`, the sha on the default branch's first-parent history.
- [ ] The skill's unit tests cover a rejected `gh-plan` push and an offline `done`.
- [ ] L10: SKILL.md describes `gh-plan`, the symlink and `plan done`.
- [ ] L11: a test shows each tool commit touches one item and `ready.yml` only.

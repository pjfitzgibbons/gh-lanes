---
title: "Move gh-plan's .tracker/ onto the gh-plan branch"
type: chore
status: Todo
estimate: 2
priority: P2
ordinal: 20740
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
  - "pl-zisab - worktask: the .tracker symlink, gh-plan starts and plan done"
  - "pl-mufed - CLAUDE.md: plan state on the gh-plan branch"
---
### Task
Move this repo's `.tracker/` history onto a `gh-plan` branch by [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md) §3.6, and attach it in the main checkout and every open worktree.

### Guardrails
- Peter runs the push and the PR from plan-board cards; no item is In Progress during the move except this one.
- Finish dates of archived items are unchanged by the split.

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
- [x] L10 Docs impact: the README links the gh-plan branch
- [x] L11 Invariants: invariant 2: after the PR, main carries none of the tracker
- [ ] L12 Offline and concurrency
### Done
- [ ] `origin/gh-plan` exists, and `git log` on it lists the commits that touched `.tracker/`, with the same committer dates.
- [ ] `main` has `/.tracker` in `.gitignore` and no `.tracker/` in its tree.
- [ ] L10: the README links the `gh-plan` branch.
- [ ] L11: `git ls-tree -r origin/main` lists no path under `.tracker/`.

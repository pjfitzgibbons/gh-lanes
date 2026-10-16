---
title: "CLAUDE.md: plan state on the gh-plan branch"
type: chore
status: Icebox
estimate: 1
priority: P2
ordinal: 20710
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
---
### Task
Update `CLAUDE.md`'s *Commands*, *Done differently* and *Boundaries* for [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md): `plan:` commits and item edits go to `gh-plan`, `main` takes nothing but PRs, and a fresh clone runs `git worktree add .tracker gh-plan`.

### Guardrails
- `CLAUDE.md` stays a contents page: the rule and a pointer to ADR 0010, not its reasoning.
- Lands with or after the move of this repo's `.tracker/`, so it never describes a layout the repo doesn't have.

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
- [x] L10 Docs impact: CLAUDE.md's Commands, Done differently and Boundaries
- [x] L11 Invariants: the three invariants CLAUDE.md quotes read as ADR 0010 §3.5 states them
- [ ] L12 Offline and concurrency
### Done
- [ ] *Done differently* says `plan:` commits and item edits are commits on `gh-plan`, and `main` takes only PRs.
- [ ] *Commands* gives the attach command for a fresh clone.
- [ ] L10: no line in `CLAUDE.md` says an item's edits ride on its branch.
- [ ] L11: invariants 2, 3 and 5 in *Boundaries* match ADR 0010 §3.5.

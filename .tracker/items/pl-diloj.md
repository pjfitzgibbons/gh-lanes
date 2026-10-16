---
title: "ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
type: chore
status: In Progress
estimate: 2
priority: P2
ordinal: 20680
lane: infra
milestone: phase-2
started: 2026-10-16T15:16:46Z
---
### Task
Decide, in ADR 0010, that a repo's plan state lives on its own `gh-plan` branch rather than on the default branch:
- The `gh-plan` branch holds `.tracker/`: the items, `ready.yml` and the archive. The default branch gitignores `.tracker/`.
- Each checkout sees it as a worktree of `gh-plan` at `.tracker/`, the way a `gh-pages` branch is often checked out, so nothing is copied or synced by hand.
- `plan:` commits and item edits are commits on `gh-plan`, so the default branch and feature PRs carry no plan churn.
- Say what this amends: ADR 0008 (items ride on their branch, `plan:` commits go to the default branch), ADR 0001 and 0002 where they put items beside the code, invariants 2, 3 and 5 in architecture §10, CLAUDE.md's *Done differently*, `worktask start` and `done`, and design 0003's `worktask-start` checks against `ready.yml` on `origin`.

### Guardrails
- Agree the ADR in chat before it's written; it changes how the tool writes to git (architecture §10).
- The decision only: no code, and no move of this repo's `.tracker/` until the ADR is accepted.
- Weigh what's lost against what's gained: an item no longer lands in the same squash commit as its code.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a checkout without the `.tracker/` worktree, and a `gh-plan` push that's rejected
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: moving an existing repo's `.tracker/` history onto `gh-plan`
- [x] L7 Usability and accessibility: what a fresh clone has to run to see its plan
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: ADRs 0001, 0002 and 0008, architecture §10, CLAUDE.md, design 0003
- [x] L11 Invariants: 2, 3 and 5 restated for a `gh-plan` branch
- [x] L12 Offline and concurrency: several worktrees sharing one `.tracker/` worktree

### Done
- [ ] ADR 0010 is agreed in chat and merged, with its status and the ADRs it amends.
- [ ] L3: the ADR says what each command does when `.tracker/` isn't checked out.
- [ ] L6: the ADR says how an existing repo moves its `.tracker/` history onto `gh-plan`.
- [ ] L7: the ADR gives the commands a fresh clone runs to see its plan.
- [ ] L10: each amended doc has a follow-up item.
- [ ] L11: invariants 2, 3 and 5 are restated in the ADR for a `gh-plan` branch.
- [ ] L12: the ADR says how several item worktrees share the one `.tracker/` worktree.

---
title: tt, worktask and gh-issues work from pl- IDs
status: Todo
estimate: 2
priority: P1
ordinal: 900
lane: infra
milestone: bootstrap
---
### Summary
Time tagging and the work skills read GitHub issue numbers from branch names. With `pl-<word>` IDs and `<type>/<id>-<slug>` branches, tt logs nothing and `worktask` cannot pick up an item. This ticket moves them to the new IDs, so dogfooding records time.

### Scope
- tt (in `~/programming/tempotag`): parse `<type>/<prefix>-<word>-<slug>` and tag entries with the item ID, as ADR 0006 now says. The tt change is a child issue in tempotag's own tracker.
- `worktask`: pick up `pl-<word>`, create `<type>/<id>-<slug>` in a worktree, and call `plan start` once it exists.
- `gh-issues` and the `plan` stand-in skill: drafting and next-ID steps write item files instead of GitHub issues.
- Out of scope: `plan start` itself (pl-dafip).

### Acceptance
- On a branch named `docs/pl-sarov-file-native-items`, tt tags tracked time `pl-sarov`.
- `worktask pl-<word>` creates the branch and worktree.

### Tests
tt's branch-parsing tests cover both the old and new branch shapes.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: existing `#N` time entries keep their tags; new ones use item IDs
- [x] L7 Usability and accessibility: time tracking keeps working through the switch
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

---
title: "Root pointer: sibling repos find the tracker without PLAN_ROOT"
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 12900
lane: model
milestone: phase-1
---
### Summary
Let a sibling component repo point back to the tracker root, so `plan` works there without exporting `PLAN_ROOT`. Today discovery walks up from cwd ([design 0001 *Discovery*](docs/design/0001-phase-1.md#discovery)), which never reaches a root in `../tracker-repo`. Only the installed git hooks set `PLAN_ROOT`. `plan init` (registering a sibling repo) is what writes the pointer, so it needs this first.

### Scope
- Choose the pointer: a committed `.plan-root` file in the component repo, or `git config plan.root`. Record the choice and the loser in design 0001 §5.
- Discovery order: `PLAN_ROOT`, then the pointer, then the walk.
- The pointer's format and where it lives; `plan init` writes it when it registers a sibling repo (that ticket), and `plan hooks install` stops setting `PLAN_ROOT` once the pointer exists.
- Out of scope: more than one tracker per repo.

### Acceptance
- From a sibling repo with the pointer, `plan` finds the root without `PLAN_ROOT` set.
- `PLAN_ROOT` still wins over the pointer.
- A pointer to a directory without `.tracker/config.yml` exits 2, naming the pointer and the path it names.
- A repo with no pointer behaves as today.

### Tests
`tests/test_config.py`: sibling `tmp_path` trees with and without the pointer. No network.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a stale pointer must fail loudly, not fall through to the walk
- [ ] L4 Performance and limits
- [x] L5 Observability: the not-found message names the pointer it followed
- [x] L6 Compatibility and migration: a committed pointer holds a path; absolute paths differ per machine, so it should be relative
- [x] L7 Usability and accessibility: removes the per-shell `PLAN_ROOT` export for sibling layouts
- [x] L8 Testability: discovery already takes `cwd` and `env`; a `git config` pointer would need git.py, so it needs a fake
- [ ] L9 Operations and cost
- [x] L10 Docs impact: design 0001 §5 *Discovery*; design 0002's hook section if the installer writes the pointer
- [x] L11 Invariants: a `git config` pointer means a git call, which must go through git.py (invariant 3)
- [ ] L12 Offline and concurrency

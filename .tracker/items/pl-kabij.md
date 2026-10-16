---
title: "Design 0001: next/ready without lane heads; §8.5 repo scope"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 12600
lane: infra
milestone: phase-1
blocked_by:
  - "pl-bafuf - Requirements and architecture: a lane is a theme; contention is blocked-by"
---
### Summary
Bring design 0001 in line with lanes as themes, and add §8.5 *Repo scope* so `plan next` answers for the repo you're in while reading the whole plan. Must land before plan.py (#16) is built.

### Scope
- §4 layout comment and §8.2 rows for `next`, `ready` and `why`.
- §8.3: drop the lane-head step from `next`; `ready` lists the top N ready items in scope (`-n`, default 5), with `next` as its first; `why` loses "behind lane head". Code sketch and examples follow.
- §9: the ordinal rule's scope, now that lanes don't serialize work.
- §12: the D1, D3 and D4 coverage rows.
- New §8.5 *Repo scope*, from the reviewed draft in `.tmp/design-repo-scope.md`: scope resolution (`--repo`, `--all`, cwd's longest match, the tracker root meaning the whole plan), scope filters output not data, lanes under scope, `repo#N` references, writes landing in the tracker repo.
- Out of scope: milestone `order` in `next` (E4), which is a separate check.

### Acceptance
- No design 0001 text relies on lane heads or lanes as contention.
- `next` in §8.3 is: drop done, iced and needs-triage; drop anything blocked by an open issue; sort by priority, ordinal, number; take the first.
- §8.5 defines the scope for every query and write command, and says scope never hides a blocker.
- At the tracker root `ready` spans the whole plan; in a component repo it lists only that repo's items.
- #16's body is rewritten to match before work on it starts.

### Tests
None; docs only. #16 carries the tests for the new algorithm.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: readiness is computed over the whole plan before scope filters it, so a blocker in another repo is never hidden
- [ ] L4 Performance and limits
- [x] L5 Observability: scoped output names its scope in the header and in `--json`
- [x] L6 Compatibility and migration: `--json` gains a `repo` field; output prints `repo#N` in multi-repo plans
- [x] L7 Usability and accessibility: scope follows cwd like git; `--all` is the one flag to remember
- [x] L8 Testability: scope resolution is pure; fixtures need a two-repo tree with a nested root
- [ ] L9 Operations and cost
- [x] L10 Docs impact: design 0001 §4, §8.2, §8.3, new §8.5, §9, §12
- [x] L11 Invariants: invariant 3 holds; scope resolution reads config and cwd only
- [x] L12 Offline and concurrency: `ready`'s N items are safe to run side by side only if contending items carry blocked-by edges

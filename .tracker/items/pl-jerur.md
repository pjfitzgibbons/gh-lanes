---
title: "Requirements and design: focus, one fast-tracked feature at a time"
type: feat
status: Icebox
estimate: 3
priority: P2
ordinal: 12700
lane: infra
milestone: phase-1
blocked_by:
  - "pl-kabij - Design 0001: next/ready without lane heads; §8.5 repo scope"
---
### Summary
Add a **focus**: one named feature fast-tracked to the top of `ready` and `next`, above priority, until it is cleared. It answers the product owner's "do this feature first" without rewriting anyone's priorities, and it enforces one thing at a time. This ticket settles the requirement and the design; implementation is a follow-up ticket cut from the design.

### Scope
- requirements: a new E-series requirement. A focus fast-tracks one feature's open work above priority, one focus at a time, reversible in one step, with the reason recorded. Its rationale states the rule: only one thing at a time, so an unplanned business request reorders the backlog explicitly and visibly instead of piling up.
- design 0001 (after #72's §8.3 and §8.5):
  - **What the feature is:** a parent issue and its sub-issues (`--parent N`, GitHub's own hierarchy, A4), or an explicit list (`--issues 12,15,18`) when the work has no parent.
  - **Storage:** `.tracker/focus.yml`, committed: name, parent or list, reason, `set_at`. Git history is the record of what was fast-tracked, when and why.
  - **Ordering:** `ready` lists focus items first, in their own priority and ordinal order, then the rest as before; `next` is `ready`'s first. Open blockers of focus items are pulled up with them, so the focus never stalls on work nobody moved.
  - **P0 still wins:** a P0 outside the focus ranks above the focus, so a fast-track never hides an emergency.
  - **One at a time:** `plan focus` refuses while one is active; `--replace` swaps it and records both. `plan focus --clear` removes it and restores the previous order exactly, because nothing else was changed.
  - Output says a focus is active: the header of `next`, `ready` and `status` names it; `why N` reports "outside the focus".
- Alternatives considered: bulk re-prioritising to P0 (loses the old ranking, makes P0 meaningless, no one-step undo); reordering milestones (too coarse: a feature cuts across milestones); a stack of focuses (two at once is ordinary prioritisation, which is what grooming is for).
- Out of scope: the code (follow-up ticket); a label as a feature definition.

### Acceptance
- The requirement exists with its rationale, and design 0001 has a *Focus* section covering definition, storage, ordering, P0, one-at-a-time, clearing and output.
- The design states how focus interacts with repo scope (§8.5): a focus spanning repos still filters to the repo you are in.
- The follow-up implementation ticket is drafted from the design, with its estimate.

### Tests
None; docs only. The implementation ticket carries the tests.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: clearing restores the previous order exactly because the focus is an overlay; a parent that is closed or transferred while focused must be reported, not silently ignored
- [ ] L4 Performance and limits
- [x] L5 Observability: every ordering command names the active focus, so nobody mistakes a fast-track for the normal plan
- [x] L6 Compatibility and migration: `focus.yml` is a new committed file; absent means no focus, so existing trees are unaffected
- [x] L7 Usability and accessibility: one command to set, one to clear; `--replace` makes swapping a deliberate act
- [x] L8 Testability: ordering stays pure in plan.py, with the focus as one more input
- [ ] L9 Operations and cost
- [x] L10 Docs impact: requirements (new E entry); design 0001 §8.2 commands, §8.3 ordering, a new *Focus* section, §9 validation (focus names a live parent or issues)
- [x] L11 Invariants: invariant 1 holds, focus lives in a committed file; invariant 2 holds, nothing is written to GitHub
- [x] L12 Offline and concurrency: two clones setting different focuses get an ordinary git conflict in one short file, which is the point: one focus at a time

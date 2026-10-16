---
title: "Requirements and architecture: a lane is a theme; contention is blocked-by"
type: feat
status: Todo
estimate: 2
priority: P2
ordinal: 12500
lane: infra
milestone: phase-1
---
### Summary
Redefine a lane as a theme, an overarching area of work, rather than a contention domain. Contention between items becomes a blocked-by edge, so the dependency graph is the one thing that limits concurrency. Requirements and architecture change first; design 0001 follows in a separate ticket.

### Scope
- requirements D1: a lane is a theme; items that touch the same files are ordered by blocked-by.
- requirements D3: "what can I start right now" is the top N ready items in the current scope, in priority order, not lane heads.
- requirements D4: single-valued lane, with a reason that doesn't rest on contention (one theme per item keeps the board and roll-ups unambiguous).
- requirements D5: concurrent sessions are kept apart by blocked-by edges between contending items.
- requirements E4: contention edges are allowed inside a milestone, alongside logical dependencies.
- architecture §2 *Definitions*: the Lane row. §12 invariant 7: its reason.
- Out of scope: design 0001 and code; see the follow-up ticket.

### Acceptance
- No requirement or architecture text describes a lane as a contention domain or depends on lane heads.
- D1's rationale states how contention is expressed and why the graph, not the lane, carries it.
- Every changed requirement keeps its ID; no ID is reused or renumbered.

### Tests
None; docs only. The existing suite still passes.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: concurrent sessions are only kept apart if contending items carry a blocked-by edge; nothing else catches a missing one
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: existing `lane` values stay valid; their meaning changes, not their shape
- [x] L7 Usability and accessibility: whoever plans must add blocked-by edges for shared files, which is new planning work
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: requirements D1, D3, D4, D5, E4; architecture §2 and §12 invariant 7
- [x] L11 Invariants: invariant 7 (one lane per item) stays, with a new reason
- [x] L12 Offline and concurrency: concurrency safety moves from lanes to blocked-by edges

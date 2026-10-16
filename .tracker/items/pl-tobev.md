---
title: "ADRs 0001, 0002 and 0008 point to ADR 0010"
type: chore
status: Todo
estimate: 1
priority: P2
ordinal: 20690
lane: infra
milestone: phase-2
blocked_by:
  - "pl-diloj - ADR 0010: plan state lives on a gh-plan branch, checked out at .tracker/"
---
### Task
Amend [ADR 0001](../../docs/adr/0001-git-is-the-database.md), [ADR 0002](../../docs/adr/0002-tracker-per-repo.md) and [ADR 0008](../../docs/adr/0008-file-native-items.md) where [ADR 0010](../../docs/adr/0010-plan-state-on-a-branch.md) changes them: the orphan branch ADR 0001 rejects, `.tracker/` beside the code in ADR 0002, and ADR 0008's start, finish and tool commits on the default branch.

### Guardrails
- Each status line names ADR 0010 as amending it; the decisions it does not change stay as written.
- No history in the docs: no "was" or "previously" notes.

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
- [x] L10 Docs impact: the three ADRs
- [x] L11 Invariants: ADR 0008 states invariants 2, 3 and 5, and its text matches ADR 0010 §3.5
- [ ] L12 Offline and concurrency
### Done
- [ ] Each of ADRs 0001, 0002 and 0008 has a status line saying ADR 0010 amends it, with a link.
- [ ] L10: no sentence in the three ADRs contradicts ADR 0010.
- [ ] L11: ADR 0008's statements of invariants 2, 3 and 5 match ADR 0010 §3.5, or point to it.

---
title: "Reality checks in the Redmine plugin"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 500
lane: web
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
---
### Task
Add the reality checks [ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md) gives to a plugin of ours:
- A Reality checks tab on the parent project lists each open issue that breaks a check, with the check's name.
- The first check is [`B3`](../../docs/requirements.md): an issue with a version and `Points` above 5.
- Each check is one query, so adding one adds a method.

### Guardrails
- The checks read only; they never change an issue or refuse a save (B3 is a practice).
- It finds `Points` by name, as the lane board does (pl-rired).

### Lenses
- [ ] L1 
- [ ] L2 Security
- [x] L3 Privacy and data: a missing Points field
- [x] L4 Reliability and failure: one query per check, not per issue
- [ ] L5 Performance and limits
- [ ] L6 Observability
- [ ] L7 Compatibility and migration
- [x] L8 Usability and accessibility: checked by hand against the redmine:7.0 image
- [ ] L9 Testability
- [ ] L10 Operations and cost
- [ ] L11 Docs impact
- [ ] L12 Invariants

### Done
- [ ] The tab lists an issue with a version and 8 points, and leaves out one with 5 points or no version.
- [ ] L3: with no `Points` field, the tab shows a message instead of an error.
- [ ] L4: the tab's query count doesn't grow with the number of issues.
- [ ] L8: the checks above ran in a `redmine:7.0` container.

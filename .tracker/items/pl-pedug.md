---
title: "Velocity per week and duration from it"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 600
lane: engine
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
---
### Task
Add what the Redmine test found missing: velocity and duration from it ([`C1`, `C2`](../../docs/requirements.md); [survey, *Redmine 7*](../../docs/alternatives-survey.md#redmine-7)):
- Velocity is the points closed per week over a trailing window, from each closed issue's close date.
- An open issue's duration is its points divided by velocity, in weeks.
- The lane board shows each lane's open points as weeks.

### Guardrails
- Velocity is per week, never per day (`C1`).
- Estimate against tracked time (pl-gilis) stays iced.

### Lenses
- [ ] L1 
- [ ] L2 Security
- [x] L3 Privacy and data: no closed issue in the window, so no velocity
- [ ] L4 Reliability and failure
- [ ] L5 Performance and limits
- [ ] L6 Observability
- [ ] L7 Compatibility and migration
- [x] L8 Usability and accessibility: checked against issues with known close dates
- [ ] L9 Testability
- [x] L10 Operations and cost: the plugin's README says how velocity is computed
- [ ] L11 Docs impact
- [ ] L12 Invariants

### Done
- [ ] With 6 points closed over a 3-week window, velocity reads 2 points per week, and a 3-point issue 1.5 weeks.
- [ ] L3: with no closed issue in the window, velocity and durations read unknown, with no error.
- [ ] L8: the check above ran in a `redmine:7.0` container.
- [ ] L10: the README gives the window and the formula.

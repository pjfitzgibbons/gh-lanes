---
title: "Redmine setup: the lane-board plugin"
type: feat
status: In Progress
estimate: 2
priority: P2
ordinal: 300
lane: infra
milestone: phase-2
blocked_by: []
started: 2026-10-16T20:44:21Z
---
### Task
Add the lane-board plugin from the Redmine 7.0.2 test ([ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md), [survey, *Redmine 7*](../../docs/alternatives-survey.md#redmine-7)) to gh-plan, at `redmine/plugins/lane_board/`. It shows a project tree's issues with lanes as rows and statuses as columns, totals the open points of each lane over leaf issues only, and marks an issue ready when it is open and every issue blocking it is closed.
- In scope: the plugin's four files, without the test version's rule that showed an estimate above 5 as ∞ and kept it from being ready ([`B3`](../../docs/requirements.md) is a practice).
- Out of scope: the reality checks, velocity, the compose file and the import, each its own item.

### Guardrails
- The plugin reads only; it writes no issue, field or relation.
- It finds its custom fields by name, `Lane` and `Points`, and shows a page that says so when `Lane` is missing.
- No real personal data in anything committed with it.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a missing `Lane` or `Points` field
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: Redmine 7.0's plugin API
- [ ] L7 Usability and accessibility
- [x] L8 Testability: checked by hand against the `redmine:7.0` image
- [ ] L9 Operations and cost
- [x] L10 Docs impact: a README in the plugin's folder
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency
### Done
- [ ] `redmine/plugins/lane_board/` holds `init.rb`, the controller, the view and the route, with no ∞ rule.
- [ ] L6: the plugin loads in a `redmine:7.0` container with no deprecation warning in the log.
- [ ] L8: in that container, the Lanes tab shows each lane's open leaf points and marks ready issues.
- [ ] L3: with no `Lane` field, the tab shows a message instead of an error.
- [ ] L10: the README says how to mount the plugin and which custom fields it needs.

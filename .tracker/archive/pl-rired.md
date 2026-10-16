---
title: "Redmine setup: the lane-board plugin"
type: feat
status: Done
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
- In scope: the plugin's four files and its README, without the test version's rule that showed an estimate above 5 as ∞ and kept it from being ready ([`B3`](../../docs/requirements.md) is a practice).
- Out of scope: the reality checks, velocity, the compose file and the import, each its own item.

### Guardrails
- The plugin reads only; it writes no issue, field or relation.
- It finds its custom fields by name, `Lane` and `Points`, and shows a page that says so when `Lane` is missing.
- No real personal data in anything committed with it.

### Lenses
- [x] L1 Security: a `Lane` or `Points` field hidden from a role
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a missing `Lane` or `Points` field
- [x] L4 Performance and limits: one query per blocking relation
- [ ] L5 Observability
- [x] L6 Compatibility and migration: Redmine 7.0's plugin API
- [ ] L7 Usability and accessibility
- [x] L8 Testability: checked by hand against the `redmine:7.0` image
- [ ] L9 Operations and cost
- [x] L10 Docs impact: a README in the plugin's folder
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency
### Done
- [x] `redmine/plugins/lane_board/` holds `init.rb`, the controller, the view and the route, with no ∞ rule.
- [x] L6: the plugin loads in a `redmine:7.0` container with no deprecation warning in the log.
- [x] L8: in that container, the Lanes tab shows each lane's open leaf points and marks ready issues.
- [x] L3: with no `Lane` field, the tab shows a message instead of an error.
- [x] L10: the README says how to mount the plugin and which custom fields it needs.
- [x] L1: a `Lane` or `Points` field hidden from the user's role in an issue's project reads as unset on the board.
- [x] L4: the board's query count does not grow with the number of blocking relations.

---
title: "Dogfood: gh-plan's own work in .tracker/items"
status: In Progress
estimate: 1
priority: P1
ordinal: 300
lane: infra
milestone: bootstrap
started: 2026-10-14T13:39:55Z
started_via: hand
---
### Summary
gh-plan plans its own work in the format it is moving to, before the tool can read it. This ticket keeps the bootstrap tracker by hand: `.tracker/config.yml` with the prefix `pl`, the `bootstrap` milestone, and one Markdown file per item under `.tracker/items/`. It replaces #25, whose JSON tracker on `feat/25-dogfood-tracker` is not merged.

### Scope
- `.tracker/config.yml`: `prefix: pl`, velocity, project start, hours per point and lanes.
- `.tracker/milestones/bootstrap.md`, its exit criterion in the body.
- `.tracker/items/pl-<word>.md` for the bootstrap work, front matter as ADR 0008 lists it and the body in the issue outline. IDs are drawn by hand from the CVCVC alphabet until the generator exists.
- `started` and `started_via: hand` are set by hand on items already under way.
- Out of scope: reading these files with the tool (the schema and store tickets), and importing the GitHub backlog.

### Acceptance
- Every file under `.tracker/` parses as YAML 1.2, and front matter keys are the ones ADR 0008 lists.
- Each `blocked_by` entry names an item file that exists.
- #25 is closed with a pointer to this ticket.

### Tests
None until the store and schemas land; then `plan validate` runs over this tracker.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: #25's JSON tracker is dropped; its values for issues still open move with the import
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [x] L12 Offline and concurrency: IDs are random words, so issues added on two branches do not collide

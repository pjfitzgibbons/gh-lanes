---
title: Convert ms-security-docs' .tracker to item and milestone files
type: chore
status: Icebox
estimate: 2
lane: infra
---
### Task
Convert ms-security-docs' tracker from the layout before ADR 0008 to the file-native one, so gh-plan can read it as its second tracker.
- Today it holds 24 YAML files under `items/contoso-health-partners/`, one per GitHub issue, and 11 milestone files as `.yml`. That migration was #26, done in ms-security-docs commit `d059b78`.
- Each item becomes `.tracker/items/<id>.md` with a drawn ID under that repo's prefix, its fields in front matter, and its body kept.
- Each milestone becomes `.tracker/milestones/<slug>.md`, and `config.yml` takes the current schema.

### Guardrails
- The work lands in ms-security-docs, by a PR there; gh-plan's own files don't change.
- No GitHub write: whatever closes are needed, Peter runs them.
- Bodies are kept as they are, apart from fields that move to front matter.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: one-way; the old files go in the same PR
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] Every old item and milestone file has a converted file, and every converted file loads with gh-plan's store and schemas.
- [ ] Every `blocked_by` and `parent` names an item file that exists.
- [ ] L6: no file in the old layout is left in ms-security-docs' `.tracker`.

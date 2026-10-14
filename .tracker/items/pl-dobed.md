---
title: Docs follow the file-native ADRs
status: In Progress
estimate: 5
priority: P1
ordinal: 200
lane: infra
milestone: bootstrap
blocked_by:
  - "pl-sarov - Items are file-native: ADRs 0007 and 0008, requirements"
started: 2026-10-14T14:35:36Z
---
### Summary
ADRs 0007 and 0008 make gh-plan its own tracker: items are Markdown files with YAML front matter, committed in the repo they belong to, and GitHub Issues is not used. The architecture, the two design docs, the older ADRs and the README still describe a planning layer over GitHub Issues with JSON files. This ticket brings them in line with the two ADRs. It changes the docs only.

### Scope
- **`docs/architecture.md`.** Remove what existed only to sync with GitHub: §3 *Ownership* (GitHub-owned fields and the one write-back), §6.1 *Pull*, §6.2 *Reconcile*, §6.3 *Mirror*, §8 *Creation paths* and §9 *Sub-issues*. Rewrite §7 *Identity* for `<prefix>-<word>` IDs, §4 *Storage* for `.tracker/items/<id>.md` and YAML, §5.2 and §5.3 for a tool whose only remote write is a `git push`, §10 *Failure modes* for local commits and pushes, and §2 *Definitions* to match. Add the start commit, the finish read from the default branch, multi-repo plans, and `ready.yml`. In §12 *Invariants*, remove 2, 4 and 6 and cut 10 down to tracked time. Renumber and fix anchors.
- **`docs/design/0001-phase-1.md`.** §6.1 *Item* and §6.2 *Identity* for the front matter fields and word IDs; §6.3 *Status* for the start commit and the finish at merge; §6.6 *Config* for `prefix` and member repos by path; §6.7 *File format* for the YAML canonical form from ADR 0007; §4 *Layout*, §7 *Index*, §8 *CLI* (drop `pull`, `reconcile` and `mirror`; add `start`, `stop` and `hooks install`'s `post-checkout`), §9 *Validation rules* (duplicate IDs, member repos sharing a prefix, unresolved cross-repo `blocked_by`, shadowed milestones, a branch missing its start), §10 *GitHub and git interaction*, §12 *Requirements coverage* and §13 *Work breakdown*.
- **`docs/design/0002-tracked-time.md`.** §4 *The correlation key* tags time entries with the item ID instead of `<owner>/<repo>#<n>`, and the rest of the doc follows.
- **ADRs.**
  - 0001: item files are `.tracker/items/<id>.md` in YAML, and the index no longer joins GitHub facts from a cached pull.
  - 0002: any repo's `.tracker/` can list member repos by path and become a plan.
  - 0003: status becomes "Superseded by ADR 0008".
  - 0004: the tracker files are YAML, read with ruamel.yaml.
  - 0006: time entries are tagged with the item ID.
- **`README.md`** describes a file-native tracker.
- **`tests/fixtures/README.md`** names the YAML and Markdown files. The fixture trees themselves change with the converter.
- **`CLAUDE.md`'s invariants list** matches architecture §12 again.
- **Open tickets that edit the same docs:**
  - #39 (derived actuals) is answered by ADR 0008's start and finish: close it or rewrite it.
  - #71, #72 and #75 rewrite parts of design 0001 and architecture: agree the landing order before starting.
- Out of scope:
  - the converters (JSON to YAML, issues to item files) and the code;
  - the skills (`gh-issues`, `worktask`, the `plan` stand-in) and tt's branch parsing.

### Acceptance
- No doc in the scope above describes GitHub Issues as the source of an item, a field, a dependency or a state, or calls the tracker files JSON.
- Architecture §12 and the `CLAUDE.md` invariants list are the same list.
- Every internal link and anchor resolves.
- The prose has had a humanizer pass.

### Tests
None: documentation only. A link check across `docs/` confirms every link resolves.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: architecture §10 is rewritten for local commits, pushes and missing member repos
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the docs describe the converted layout, and the fixture trees follow with the converter
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: architecture, design 0001 and 0002, ADRs 0001 to 0004 and 0006, the README, the fixtures README and `CLAUDE.md`
- [x] L11 Invariants: invariants 2, 4 and 6 go and 10 keeps only tracked time, in architecture §12 and `CLAUDE.md` together
- [ ] L12 Offline and concurrency

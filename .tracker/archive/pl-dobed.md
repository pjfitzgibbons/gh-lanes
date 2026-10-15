---
title: Docs follow the file-native ADRs
type: chore
status: Done
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
- **`docs/architecture.md`.** Remove what existed only to sync with GitHub: §3 *Ownership* (GitHub-owned fields and the one write-back), §6.1 *Pull*, §6.2 *Reconcile*, §6.3 *Mirror*, §8 *Creation paths* and §9 *Sub-issues*. Rewrite §7 *Identity* for `<prefix>-<word>` IDs, §4 *Storage* for `.tracker/items/<id>.md` and YAML, §5.2 and §5.3 for a tool whose only remote write is a `git push`, §10 *Failure modes* for local commits and pushes, and §2 *Definitions* to match. Add the start commit, the finish read from the default branch, multi-repo plans, and `ready.yml`. The new outline is Purpose, Definitions, Storage, Plans, Identity, Components, Operations, Failure modes, Views and Invariants. Renumber and fix anchors. *Invariants* drops the old 2, 4 and 6, cuts 10 down to tracked time, and adds four rules: the default branch carries the current state; a tool commit touches only one item's `status` and `started`, plus `ready.yml`; `started` is written once, and `plan stop` leaves it; the tool's only remote write is a `git push` of its own commits. The eleven are grouped by theme and numbered 1 to 11, and references elsewhere name an invariant rather than its old number.
- **`docs/design/0001-phase-1.md`.** §6.1 *Item* and §6.2 *Identity* for the front matter fields and word IDs; §6.3 *Status* for the start commit and the finish at merge; §6.6 *Config* for `prefix` and member repos by path; §6.7 *File format* for the YAML canonical form from ADR 0007; §4 *Layout*, §7 *Index*, §8 *CLI* (drop `pull`, `reconcile` and `mirror`; add `start`, `stop` and `hooks install`'s `post-checkout`), §9 *Validation rules* (duplicate IDs, member repos sharing a prefix, unresolved cross-repo `blocked_by`, shadowed milestones, a branch missing its start), §10 *GitHub and git interaction*, §12 *Requirements coverage* and §13 *Work breakdown*.
- **`docs/design/0002-tracked-time.md`.** §4 *The correlation key* tags time entries with the item ID instead of `<owner>/<repo>#<n>`. §6 takes the `actual_time` snapshot in the write that sets `status: Done`, and the `post-merge` hook reports a Done item with no snapshot. The rest of the doc follows.
- **ADRs.**
  - 0001: item files are `.tracker/items/<id>.md` in YAML, and the index no longer joins GitHub facts from a cached pull.
  - 0002: any repo's `.tracker/` can list member repos by path and become a plan.
  - 0003: status becomes "Superseded by ADR 0008".
  - 0004: the tracker files are YAML, read with ruamel.yaml.
  - 0006: time entries are tagged with the item ID.
  - 0008: `started_via` goes, since the commit that sets `started` already records how; `plan stop` keeps `started`; references to invariants by number become names.
- **`docs/requirements.md` `D6`** drops `started_via` from the in-flight section.
- **`docs/agents/technical-writer.md` §3** describes an item file instead of a GitHub issue: no `[N]` title prefix, no *Planning* section, and `blocked_by` in the front matter. The issue forms in `.github/ISSUE_TEMPLATE/` go.
- **An item `type`:** `feat`, `bug` or `chore`, required, after `title`. It names the branch's `<type>`, with `fix` for a bug; `plan new --type` and `plan set --type` write it, and `validate` warns when a branch's `<type>` disagrees. Every item in `.tracker/items/` gets one.
- **Item files:** `started_via` comes out of pl-sarov and pl-bihum, and out of pl-kozot's field order. pl-dafip's `plan stop` keeps `started`.
- **`README.md`** describes a file-native tracker.
- **`tests/fixtures/README.md`** names the YAML and Markdown files. The fixture trees themselves change with the converter.
- **`CLAUDE.md`'s invariants list** holds all eleven from architecture §10, one line each, with the same numbers.
- **Open tickets that edit the same docs:**
  - #39 (derived actuals) is answered by ADR 0008's start and finish, and is closed.
  - #71, #72 and #75 rewrite parts of design 0001 and architecture. They land after this ticket, in that order, and rebase onto its section numbers.
- Out of scope:
  - the converters (JSON to YAML, issues to item files) and the code;
  - the skills (`gh-issues`, `worktask`, the `plan` stand-in) and tt's branch parsing.

### Acceptance
- No doc in the scope above describes GitHub Issues as the source of an item, a field, a dependency or a state, or calls the tracker files JSON.
- Architecture §10 and the `CLAUDE.md` invariants list are the same list.
- Every internal link and anchor resolves.
- The prose has had a humanizer pass.

### Tests
None: documentation only. A link check across `docs/` confirms every link resolves.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: architecture *Failure modes* is rewritten for local commits, pushes and missing member repos
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the docs describe the converted layout, and the fixture trees follow with the converter
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: architecture, design 0001 and 0002, ADRs 0001 to 0004, 0006 and 0008, requirements `D6`, the writer conventions, the README, the fixtures README and `CLAUDE.md`
- [x] L11 Invariants: the old 2, 4 and 6 go, 10 keeps only tracked time, and four rules on the default branch, tool commits, `started` and pushes are added, in architecture and `CLAUDE.md` together
- [ ] L12 Offline and concurrency

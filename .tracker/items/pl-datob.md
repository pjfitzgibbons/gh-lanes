---
title: Import gh-plan's completed GitHub issues as archived Done items
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 900
lane: github
milestone: bootstrap
blocked_by:
  - "pl-johoh - Archive: Done items move to .tracker/archive/"
  - "pl-veles - Import gh-plan's open GitHub issues into .tracker/items, then close them"
---
### Task
Bring gh-plan's completed GitHub issues into `.tracker/archive/` as Done items, so the points finished before 2026-10-14 count in velocity from the files, not only from GitHub's issue titles.
- Import the issues closed as completed, except #25, which pl-bihum already replaces: #3, #6, #7, #8, #10, #60, #66, #67. Issues closed as not planned (#51 to #55) stay on GitHub.
- Each is written as pl-veles writes an open issue (title, body, `type`, estimate from the `[N]` prefix, labels), with `status: Done`, straight into `archive/`, and with no `started`.
- The finish: C5 reads it from the commit on the default branch that makes the item Done, and for these that is the import commit, dated today. An imported item records instead the squash commit of the PR that closed its issue, as `finish_commit: <sha>`, a new optional `Item` field written only by the import. The commits are on `main`'s first-parent history: #3 by `03f4ad7` (#50), #6 by `befe1f4` (#63), #7 by `53dc821` (#73), #8 by `e0c0d74` (#74), #10 by `34235d2` (#79), #66 by `6d848f9` (#70), #67 by `a685d24` (#68).
- Docs: requirement C5 and ADR 0008's finish name `finish_commit` as the finish of an imported item; design 0001's Item schema and key order add it after `started`.
- pl-veles's L6 lens stops saying GitHub keeps the closed issues; it points here.

### Guardrails
- `finish_commit` names a commit and never a typed date: it is evidence in git, and C5 still holds.
- An issue with no closing PR (#60, a run of GitHub writes) is imported with no `finish_commit`, and counts in no velocity.
- No GitHub write: the issues are already closed, so nothing is commented on or reopened.
- Imported bodies are kept as they are.

### Lenses
- [ ] L1 Security
- [x] L2 Privacy and data: issue bodies become committed files, as public as the repo
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: one new optional field; every existing item loads unchanged
- [ ] L7 Usability and accessibility
- [x] L8 Testability: the finish of an imported item is read from a temporary repo's commit
- [ ] L9 Operations and cost
- [x] L10 Docs impact: C5, ADR 0008 and design 0001's Item schema change
- [x] L11 Invariants: the tool makes no GitHub write (invariant 5)
- [ ] L12 Offline and concurrency

### Done
- [ ] `.tracker/archive/` holds one Done item for each of #3, #6, #7, #8, #10, #60, #66 and #67, and none for #25 or #51 to #55.
- [ ] Every imported file loads with the store and schemas, and `ids.py` resolves each by ID.
- [ ] The imported estimates sum to 19 points, matching the issues' `[N]` prefixes.
- [ ] L2: Peter has read the imported bodies in the diff, and none holds a secret or real personal data.
- [ ] L6: `finish_commit` is optional, and every item already in `items/` and `archive/` loads with no change.
- [ ] L8: a test: an item with `finish_commit` takes that commit's date as its finish; one without it takes the commit that made it Done.
- [ ] L8: a test: a `finish_commit` that is not on the default branch's first-parent history fails validation.
- [ ] L10: C5, ADR 0008's finish and design 0001's Item schema name `finish_commit`.
- [ ] L11: the import runs with no `gh` write; the diff is the only change.
- [ ] `uv run pytest` passes, coverage gate included.

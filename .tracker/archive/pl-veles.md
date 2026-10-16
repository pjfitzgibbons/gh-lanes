---
title: Import gh-plan's open GitHub issues into .tracker/items, then close them
type: chore
status: Done
estimate: 3
priority: P1
ordinal: 800
lane: github
milestone: bootstrap
blocked_by:
  - "pl-kozot - Schemas: Item, Milestone and Config for file-native trackers"
  - "pl-ganot - store.py: YAML and Markdown front matter, in one canonical form"
  - "pl-jamup - IDs: draw a word, keep the blocklist, resolve what is typed"
started: 2026-10-15T18:36:08Z
---
### Task
Move gh-plan's open GitHub issues into item files once, then close them on GitHub with a pointer to the file, so GitHub Issues stops being where this repo's work is tracked (ADR 0008).
- Triage first: issues that only make sense with GitHub Issues as the tracker are closed as superseded by ADR 0008, not imported. Candidates: #11 pull, #14 auto-pull, #17 reconcile, #21 batch title writes, #37 transfer and deletion, #38 offline drafts, #39 to #45 derived actuals from issues, #62's reconcile half.
- Import the rest: title, body, `type` (`bug` for an issue labelled `bug`, otherwise `feat`), estimate (from the `[N]` prefix), labels, parent and blocked-by, with `ordinal`, `lane` and `milestone` from each issue's Planning block where it has one. Milestones `phase-0` to `phase-3` get files.
- Close each imported issue with a comment naming its new ID and file.
- Design 0003 gains the step this item needed from the plan board: `worktask-start` reopens an item that is In Progress with no worktree or branch.

### Guardrails
- Peter reviews the triage list before anything closes.
- Peter runs every write to GitHub; the tool only prints a script. Writes are paced.
- Imported bodies are kept as they are, except the Planning block, whose values move to front matter; they are rewritten to the item outline when picked up, not here.

### Lenses
- [ ] L1 Security
- [x] L2 Privacy and data: issue bodies become committed files, as public as the repo
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: one-way, run once; the completed closed issues follow in pl-datob
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [x] L9 Operations and cost: about 50 closes, paced under the secondary rate limit
- [x] L10 Docs impact: design 0003 gains the reopen
- [x] L11 Invariants: the tool itself writes nothing to GitHub; Peter runs the closes (invariant 5)
- [ ] L12 Offline and concurrency

### Done
- [x] The triage list, each issue marked import or close with its reason, is agreed with Peter before any write.
- [x] A dry run prints every file it would write and every close it would make, and writes nothing.
- [x] Every open issue is either imported to an item file or closed with a reason.
- [x] Every imported `blocked_by` and `parent` names an item file that exists, and every imported file loads with the store and schemas.
- [x] L2: Peter has read the imported bodies in the diff, and none holds a secret or real personal data.
- [x] L10: design 0003 describes the reopen, agreed with Peter.
- [x] L6: each closed issue's last comment names its item ID and file.
- [x] L9: the close script pauses between writes, and its run ends without a rate-limit error.
- [x] L11: the import makes no GitHub write; the closes run only from the script Peter runs.
- [x] `gh issue list --state open` shows no issues afterwards, apart from any kept on purpose and named in the PR.

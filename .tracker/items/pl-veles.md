---
title: Import gh-plan's open GitHub issues into .tracker/items, then close them
type: chore
status: Todo
estimate: 3
priority: P1
ordinal: 800
lane: github
milestone: bootstrap
blocked_by:
  - "pl-kozot - Schemas: Item, Milestone and Config for file-native trackers"
  - "pl-ganot - store.py: YAML and Markdown front matter, in one canonical form"
  - "pl-jamup - IDs: draw a word, keep the blocklist, resolve what is typed"
---
### Task
Move gh-plan's open GitHub issues into item files once, then close them on GitHub with a pointer to the file, so GitHub Issues stops being where this repo's work is tracked (ADR 0008).
- Triage first: issues that only make sense with GitHub Issues as the tracker are closed as superseded by ADR 0008, not imported. Candidates: #11 pull, #14 auto-pull, #17 reconcile, #21 batch title writes, #22 mirror, #37 transfer and deletion, #38 offline drafts, #39 to #45 derived actuals from issues, #62's reconcile half.
- Import the rest: title, body, `type` (`bug` for an issue labelled `bug`, otherwise `feat`), estimate (from the `[N]` prefix), labels, parent and blocked-by, with `priority`, `ordinal`, `lane` and `milestone` from #25's JSON tracker where it has them.
- Close each imported issue with a comment naming its new ID and file.

### Guardrails
- Peter reviews the triage list before anything closes.
- Peter runs every write to GitHub; the tool only prints a script. Writes are paced.
- Imported bodies are kept as they are; they are rewritten to the item outline when picked up, not here.

### Lenses
- [ ] L1 Security
- [x] L2 Privacy and data: issue bodies become committed files, as public as the repo
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: one-way, run once; GitHub keeps the closed issues as history
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [x] L9 Operations and cost: about 50 closes, paced under the secondary rate limit
- [ ] L10 Docs impact
- [x] L11 Invariants: the tool itself writes nothing to GitHub; Peter runs the closes (invariant 5)
- [ ] L12 Offline and concurrency

### Done
- [ ] The triage list, each issue marked import or close with its reason, is agreed with Peter before any write.
- [ ] A dry run prints every file it would write and every close it would make, and writes nothing.
- [ ] Every open issue is either imported to an item file or closed with a reason.
- [ ] Every imported `blocked_by` and `parent` names an item file that exists, and every imported file loads with the store and schemas.
- [ ] L2: Peter has read the imported bodies in the diff, and none holds a secret or real personal data.
- [ ] L6: each closed issue's last comment names its item ID and file.
- [ ] L9: the close script pauses between writes, and its run ends without a rate-limit error.
- [ ] L11: the import makes no GitHub write; the closes run only from the script Peter runs.
- [ ] `gh issue list --state open` shows no issues afterwards, apart from any kept on purpose and named in the PR.

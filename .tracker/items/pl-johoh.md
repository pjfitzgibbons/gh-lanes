---
title: "Archive: Done items move to .tracker/archive/"
type: chore
status: Todo
estimate: 2
priority: P1
ordinal: 650
lane: model
milestone: bootstrap
---
### Task
`.tracker/items/` keeps every item ever made, so the active work gets harder to see as Done items pile up. A Done item moves to `.tracker/archive/<id>.md` in the same branch commit that sets it `status: Done`, so the merge both finishes and archives it.
- Docs: ADR 0008 (the finish), the Item row of architecture.md's glossary, and requirements H5 state the rule: Done ⟺ in `archive/`. Reopening an item moves it back to `items/` in the commit that changes its status.
- The finish is still the first-parent commit on the default branch that made the item Done. That commit now also renames the file, so finding it follows the rename.
- `ids.py`: `item_ids` reads `archive/` as well as `items/`, so `new_id` never draws an archived item's word, and `resolve` and `read_titles` still find an archived item.
- Migration: `git mv` the items Done today (pl-sarov, pl-dobed, pl-bihum, pl-ganot, pl-jamup, pl-kozot) into `archive/`.
- The worktask skill: `done` warns when the merged item is not in `archive/`.

### Guardrails
- The move rides on the commit that sets Done, on the item's branch. Nothing reaches the default branch outside a PR.
- An item in both `items/` and `archive/` is an error, never a silent pick of one.
- Out of scope: a `plan validate` rule for Done ⟺ `archive/` (whichever item builds file-native validate takes it from the docs), and a command that sets Done.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: today's Done items move with `git mv`, so history follows; readers look in both directories
- [x] L7 Usability and accessibility: `items/` lists only active work
- [x] L8 Testability: an archived ID is taken, and it resolves
- [ ] L9 Operations and cost
- [x] L10 Docs impact: ADR 0008, the architecture glossary, requirements H5
- [x] L11 Invariants: the move rides on the Done commit on the branch, so invariants 2 and 3 stand
- [ ] L12 Offline and concurrency

### Done
- [ ] Every item with `status: Done` is in `.tracker/archive/`, and `.tracker/items/` holds none.
- [ ] L6: `git log --follow` on each moved file reaches the commit that created it.
- [ ] L6: a test shows `resolve` and `read_titles` find an archived item.
- [ ] L7: `ls .tracker/items/` lists only items that are not Done.
- [ ] L8: a test shows `new_id` never returns an archived item's ID.
- [ ] L8: a test shows an ID in both directories raises an error naming both paths.
- [ ] L10: ADR 0008, architecture.md's glossary and requirements H5 each say a Done item lives in `archive/` and a reopened one moves back.
- [ ] L11: the moves reach the default branch only through this PR; `git log origin/main -- .tracker/archive/` shows no commit before its merge.
- [ ] `worktask done` warns for a merged item outside `archive/`, and is silent for one inside it.
- [ ] `uv run pytest` passes, coverage gate included.

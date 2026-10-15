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
### Summary
`.tracker/items/` keeps every item ever made, so the active work gets harder to see as Done items pile up. A Done item moves to `.tracker/archive/<id>.md`, in the same branch commit that sets it `status: Done`, so the merge both finishes and archives it. Nothing changes on the default branch outside a PR, and the invariants stand as they are.

### Scope
- Docs: amend ADR 0008 (the finish), the Item row of architecture.md's glossary, and requirements H5. The rule is Done ⟺ in `archive/`. Reopening an item moves it back to `items/` in the commit that changes its status.
- The finish is still the first-parent commit on the default branch that made the item Done. That commit now also renames the file, so finding it follows the rename.
- `ids.py`: `item_ids` reads `archive/` as well as `items/`, so `new_id` never draws an archived item's word, and `resolve` and `read_titles` still find an archived item.
- An item in both directories is an error.
- Migration: move the items Done today (pl-sarov, pl-dobed, pl-bihum, pl-ganot, pl-jamup) with `git mv`, so history follows.
- The worktask skill: `done` warns when the merged item is not in `archive/`.
- Out of scope: a `plan validate` rule for Done ⟺ `archive/` (whichever item builds file-native validate takes the rule from the docs), and a command that sets Done.

### Acceptance
- The five Done items are in `.tracker/archive/` and their `git log --follow` reaches their creation.
- `new_id` never returns the ID of an archived item.
- `resolve` finds an archived item by its full ID.
- ADR 0008, architecture.md and requirements H5 describe the archive.

### Tests
`ids.py` tests: an archived ID is taken; an archived item resolves; an ID in both directories is an error.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: existing Done items move with `git mv`, so history follows; readers look in both directories
- [x] L7 Usability and accessibility: `items/` lists only active work
- [x] L8 Testability: an archived ID is taken, and it resolves
- [ ] L9 Operations and cost
- [x] L10 Docs impact: ADR 0008, the architecture glossary, requirements H5
- [x] L11 Invariants: the move rides on the Done commit on the branch, so invariants 2 and 3 stand
- [ ] L12 Offline and concurrency

---
title: "plan start and plan stop: the curated start commit and the post-checkout hook"
type: feat
status: Icebox
estimate: 5
priority: P2
ordinal: 1000
lane: engine
milestone: bootstrap
blocked_by:
  - "pl-ganot - store.py: YAML and Markdown front matter, in one canonical form"
  - "pl-kozot - Schemas: Item, Milestone and Config for file-native trackers"
  - "pl-jamup - IDs: draw a word, keep the blocklist, resolve what is typed"
---
### Task
Record an item's start as ADR 0008 decides: a curated tool commit on the default branch, pushed, that the item's branch contains. This replaces the worktask skill's `plan-start` stand-in.
- `plan start <id>`: set `status: In Progress` and `started` (UTC, to the second), build the commit on the default branch's tip through a temporary index, push it, then create the item's branch from it.
- `plan stop <id>`: commit the item back to Todo.
- The `post-checkout` hook, written by `plan hooks install`: on a branch carrying an ID, start the item, then fast-forward the branch onto the start commit if it has no commits yet, or else write the change into its working tree.
- The default branch comes from `refs/remotes/origin/HEAD`.
- Races: the local default branch moves only by compare-and-swap (`git update-ref <ref> <new> <old>`). A push rejected because the default branch moved fetches, re-reads the item on the new tip, does nothing if it is started there, and otherwise rebuilds the commit on that tip and pushes again.

### Guardrails
- A start or stop commit touches one item's `status` and `started` and nothing else, and leaves the working tree as it was.
- `started` is written once: `plan stop` leaves it, and a later start keeps it.
- The hook always exits 0.
- Offline, the commit stays local until the next push, and the command says so.
- Out of scope: `ready.yml`, which the start commit regenerates once it exists.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a push that fails leaves the commit local and says so
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [x] L8 Testability: every case runs against a temporary repo with a bare remote
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [x] L11 Invariants: the only exception to never committing straight to the default branch (2, 3 and 4)
- [x] L12 Offline and concurrency: two branches starting one item: the second finds `started` set and leaves it; a lost push race rebuilds on the new tip

### Done
- [ ] The item's branch contains the start commit, and its later change to Done merges without conflict.
- [ ] A test: the hook on a fresh branch fast-forwards it onto the start commit.
- [ ] L3: a test: the hook on a branch with commits writes the change into its working tree, and exits 0, even when the start fails.
- [ ] L3: a test: an offline start leaves one local commit and a message saying it is unpushed.
- [ ] L8: every test above runs against a temporary repo with a bare remote, never the real origin.
- [ ] L11: after `plan start`, the default branch has one `plan: start <id>` commit touching only that item file, and `git status` is unchanged.
- [ ] L11: `plan stop` commits `plan: stop <id>` with `status: Todo` and `started` unchanged; a second start keeps that `started`.
- [ ] L11: `git log --grep '^plan:'` finds every tool commit the tests made.
- [ ] L12: a test: two starts racing for one push both land for different items, and give one start commit for the same item.
- [ ] `uv run pytest` passes, coverage gate included.

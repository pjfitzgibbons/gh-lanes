---
title: "plan start and plan stop: the curated start commit and the post-checkout hook"
status: Todo
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
### Summary
Record an item's start as ADR 0008 decides: a curated tool commit on the default branch, pushed, that the item's branch contains.

### Scope
- `plan start <id>`: set `status: In Progress`, `started` (UTC, to the second) and `started_via`, build the commit on the default branch's tip through a temporary index, push it, then create the item's branch from it. An existing `started` is never overwritten.
- `plan stop <id>`: commit the item back to Todo and drop `started`.
- The `post-checkout` hook, written by `plan hooks install`: on a branch carrying an ID, start the item, then fast-forward the branch onto the start commit if it has no commits yet, or else write the change into its working tree. It always exits 0.
- The default branch comes from `refs/remotes/origin/HEAD`.
- Offline, the commit stays local until the next push.
- Out of scope: `ready.yml`, which the start commit regenerates once it exists.

### Acceptance
- After `plan start`, the default branch has one `plan: start <id>` commit touching only that item file, and the working tree is unchanged.
- The branch contains the start commit, and its later change to Done merges without conflict.
- `git log --grep '^plan:'` finds every tool commit.

### Tests
Tests over a temporary repo with a bare remote: start, stop, the hook on a fresh branch, the hook on a branch with commits, offline start.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a push that fails leaves the commit local and says so
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [x] L11 Invariants: the only exception to never committing straight to the default branch
- [x] L12 Offline and concurrency: two branches starting one item: the second finds `started` set and leaves it

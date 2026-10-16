---
title: "The plan-board extension's status bar, toasts and Send back to Claude"
type: feat
status: Todo
estimate: 2
priority: P2
ordinal: 20685
lane: web
milestone: phase-2
blocked_by:
  - "pl-bevig - The plan-board VS Code extension: the sidebar and its presses"
---
### Task
Add the status bar and toasts of [design 0003](../../docs/design/0003-plan-board.md) §3.6:
- `Plan board: N waiting`, or `Plan board: running <card>` while a card runs.
- A toast for each finished card, with *Open log*, *Open PR*, *Send back to Claude*, *Use my edits* and *Open worktree window* where they apply.
- *Send back to Claude* types a line into the item's Claude terminal and leaves it for Peter to send.

### Guardrails
- Nothing is sent to Claude without Peter's Enter.
- Names shown come from git or `gh`, never from the code.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a toast for refused and failed cards
- [ ] L4 Performance and limits
- [x] L5 Observability: the status bar always says what's waiting or running
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: each toast button is also a command
- [x] L8 Testability: toast choice is tested from card results
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] The tests for toasts and the status bar in design §6 pass.
- [ ] L3: a refused card's toast offers *Send back to Claude*.
- [ ] L5: the status bar text matches each state the tests cover.
- [ ] L7: each toast action is in the command palette.
- [ ] L8: each result fixture maps to its toast in the tests.

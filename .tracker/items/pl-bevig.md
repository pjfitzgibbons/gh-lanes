---
title: "The plan-board VS Code extension: the sidebar and its presses"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 20680
lane: web
milestone: phase-2
blocked_by:
  - "pl-jemuj - plan_board.py: the plan-board runner, its card format and eight recipes"
---
### Task
Grow `worktask`'s VS Code extension into `pjfitzgibbons.plan-board`, the sidebar of [design 0003](../../docs/design/0003-plan-board.md) §3.6:
- Ready, In-progress and Done sections across the repos in `planBoard.repos`, read with `plan_board.py list` and refreshed by a file watcher.
- Review of a card's files in the diff editor, a PR body diffed against the copy on GitHub and hidden when it matches, and *Use my edits*.
- ▶ and ▶ *Start* in a named terminal; clicking an item's row switches to its window.
- Polling a `review` card every 60 s, and *Worktree Done*.

### Guardrails
- The extension binds no network port.
- Every press runs `plan_board.py`; the extension runs no git or `gh` write itself.
- Installs from a local `.vsix`, like `worktask`'s.

### Lenses
- [x] L1 Security: no port, and nothing runs without a press
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: the sidebar's rows of design §3.7
- [x] L4 Performance and limits: one `gh` call a minute per watching card
- [x] L5 Observability: each card's state as a word and an icon
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: keyboard-operable tree, each action a command
- [x] L8 Testability: the view model is tested without VS Code
- [x] L9 Operations and cost: installs from a local `.vsix`
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [x] L12 Offline and concurrency: several windows show one card's lock

### Done
- [ ] The extension tests listed in design §6 pass.
- [ ] L1: no listening socket while the extension runs.
- [ ] L3: an interrupted card shows *interrupted*.
- [ ] L4: a watching card polls at most once a minute.
- [ ] L5: each card state has its word and icon.
- [ ] L7: every action runs from the command palette.
- [ ] L8: the view model's tests run without VS Code.
- [ ] L9: `code --install-extension` installs the built `.vsix`.
- [ ] L12: a press on a locked card shows the lock's holder.

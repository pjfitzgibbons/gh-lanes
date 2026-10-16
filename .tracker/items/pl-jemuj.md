---
title: "plan_board.py: the plan-board runner, its card format and eight recipes"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 20670
lane: infra
milestone: phase-2
---
### Task
Build the runner of [design 0003](../../docs/design/0003-plan-board.md) §3.1 to §3.3 in `~/.claude/skills/plan-board/scripts/plan_board.py`:
- The card format, `v: 1`: its `card` ID, its hashed files, its verbatim `steps`, a literal block above `paths` with one command to a line, read with ruamel.yaml from a PEP 723 block under `uv run`, and the `O_EXCL` lock.
- `run`, which checks a card and runs its recipe, appending the `run` block, the log and the `result` to the card.
- `start`, which plants card 01 and runs it; `poll`, one poll of a `review` card; `list`.
- The eight recipes with their checks: `worktask-start` (which also reopens an In Progress item with no worktree or branch), `commit`, `rebase`, `ship`, `pr-body`, `review`, `issue-close`, `worktask-done`.
- The live-body check before `gh pb`, and keeping the last three items done after `worktask-done`.
- The design §3.2 checks that a step reads what was reviewed: the staged blobs and commit message checked before any push, the body read back after posting, nothing outside `paths` staged, and `rebase`'s lease pinned to a fetched tip that `HEAD` contains.

### Guardrails
- The runner runs a card's `steps` only when they are exactly what its recipe would run now; a recipe it doesn't know is refused.
- The runner refuses to start under Claude's Bash tool.
- Nothing in gh-plan's `src/` spawns a process (invariant 6).
- No paid API use and no token or key (G3, I1).

### Lenses
- [x] L1 Security: fixed recipes, a card's steps checked against its recipe's, hashes checked before every run
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: each row of design §3.7 the runner owns
- [ ] L4 Performance and limits
- [x] L5 Observability: the appended run, log and result
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [x] L8 Testability: the recipes run against stub `git` and `gh`, without the network
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [x] L11 Invariants: 5's exception only through a card; 6 holds
- [x] L12 Offline and concurrency: two presses of one card never both run

### Done
- [ ] Each test listed for the runner in design §6 passes.
- [ ] L1: a card naming an unknown recipe, with a changed file, or with a step its recipe wouldn't run, is refused.
- [ ] L1: a file edited between its hash check and its step never reaches the remote.
- [ ] L3: a run killed partway leaves a card that parses, which `run` then refuses.
- [ ] L5: every run appends tool versions, a timestamped log and a result.
- [ ] L8: the suite runs with no network.
- [ ] L11: the runner refuses under Claude's Bash tool.
- [ ] L12: a second `run` of a locked card shows the lock's holder and does nothing.

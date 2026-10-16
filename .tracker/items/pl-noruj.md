---
title: "The plan-board hooks: deny Claude the runner, hand it the results"
type: feat
status: Todo
estimate: 2
priority: P2
ordinal: 20675
lane: infra
milestone: phase-2
blocked_by:
  - "pl-jemuj - plan_board.py: the plan-board runner, its card format and eight recipes"
---
### Task
Build the two hooks of [design 0003](../../docs/design/0003-plan-board.md) §3.4 and §3.5, registered in user settings:
- `deny_plan_board.py`, a `PreToolUse` hook that denies Claude's Bash any command naming the runner.
- `results.py`, a `UserPromptSubmit` hook that adds the card results Claude hasn't seen, a `review` card's review block included, to its next turn, once each.

### Guardrails
- The hooks read cards and never write them, apart from `results.py`'s record of what it has delivered.
- No paid API use and no token or key (G3, I1).

### Lenses
- [x] L1 Security: Claude can't run a recipe by any spelling of the runner's name
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a card that won't parse is reported, not dropped
- [ ] L4 Performance and limits
- [x] L5 Observability: Claude sees each result once, without being asked
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [x] L8 Testability: both hooks run against fixture cards
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [x] L11 Invariants: no agent runs a recipe
- [ ] L12 Offline and concurrency

### Done
- [ ] Each test listed for the hooks in design §6 passes.
- [ ] L1: the deny hook blocks each spelling design §6 lists.
- [ ] L3: a broken card yields a message naming it.
- [ ] L5: a result is delivered once and not again.
- [ ] L8: the tests use fixture cards only.
- [ ] L11: the hooks are in user settings and the suite checks their registration.

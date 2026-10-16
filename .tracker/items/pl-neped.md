---
title: "Hand over steps as plan-board cards in post-pr, worktask and the Complete page"
type: feat
status: Todo
estimate: 2
priority: P2
ordinal: 20690
lane: infra
milestone: phase-2
blocked_by:
  - "pl-jemuj - plan_board.py: the plan-board runner, its card format and seven recipes"
  - "pl-noruj - The plan-board hooks: deny Claude the runner, hand it the results"
---
### Task
Switch the hand-overs to cards, as [design 0003](../../docs/design/0003-plan-board.md) §8 lists:
- `post-pr`, `worktask` and gh-issues' *Complete* page plant a card instead of printing a command line.
- `worktask start` adds the main checkout to the worktree's `additionalDirectories`, so Claude there can plant cards in `.tmp/plan-board/`.
- A `plan-board` skill tells Claude how to plant a card.
- The CLAUDE.md plan-board card rule drops its "until the runner ships" clause.

### Guardrails
- Claude plants cards and never runs one.
- Each skill keeps working where the runner isn't installed, by printing the line as before.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: no runner installed falls back to the printed line
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: skills work with and without the runner
- [x] L7 Usability and accessibility: no command is copied by hand
- [x] L8 Testability: each skill's card is checked by the runner's own parser
- [ ] L9 Operations and cost
- [x] L10 Docs impact: CLAUDE.md, the skills' docs
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] Each skill's tests pass, with and without the runner installed.
- [ ] L3: without the runner, each skill prints its line.
- [ ] L6: a card planted by each skill parses with `plan_board.py`.
- [ ] L7: a full item runs start to done without a copied command.
- [ ] L8: the cards are checked with the runner's parser in the tests.
- [ ] L10: CLAUDE.md and the skills' docs describe cards.

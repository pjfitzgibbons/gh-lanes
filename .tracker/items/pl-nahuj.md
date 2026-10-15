---
title: Fixture trees and a converter from JSON trackers
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 700
lane: model
milestone: bootstrap
blocked_by:
  - "pl-ganot - store.py: YAML and Markdown front matter, in one canonical form"
  - "pl-kozot - Schemas: Item, Milestone and Config for file-native trackers"
  - "pl-jamup - IDs: draw a word, keep the blocklist, resolve what is typed"
---
### Task
The synthetic fixture trees under `tests/fixtures/` are still JSON trackers. Convert them to the file-native layout, and write the one-time converter that moves a JSON tracker to YAML and Markdown, so any JSON tracker has a migration path.
- The converter (`plan convert` or a one-off script) turns `config.json` into `config.yml`, each milestone into `milestones/<id>.md`, and each item into `items/<id>.md` with a drawn ID and `type: feat`.
- `.cache/gh/` drops out of every fixture tree.
- `broken/` trees named for rules that no longer exist (`done-but-open`, `blocker-outside-repos`, and any other) are removed, or renamed for the rule that replaces them.
- `broken/` gains a tree for each rule design 0001 §9 adds.
- `tests/fixtures/README.md` describes the new layout.

### Guardrails
- Fixtures stay synthetic: no real names, repos or issue text.
- Fields GitHub owned are left for the import (pl-veles); the converter does not invent them.
- Each `broken/` tree breaks exactly one rule.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the converter is the migration path for any JSON tracker
- [ ] L7 Usability and accessibility
- [x] L8 Testability: fixtures stay synthetic, one rule per broken tree
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] No fixture tree contains a `.json` tracker file or a `.cache/gh/` directory.
- [ ] Every `valid/` tree loads with the file-native store and schemas, in `tests/test_fixtures.py`.
- [ ] `test_every_section_9_rule_with_a_message_has_a_tree` has lost its `xfail` mark and passes.
- [ ] L6: a converter test turns a JSON tree into the expected YAML tree, and every field the new schema keeps survives it.
- [ ] L8: each `broken/` tree fails on exactly its one named rule, in `tests/test_fixtures.py`.
- [ ] L8: every converted file in the diff names only synthetic owners, repos and people.
- [ ] `tests/fixtures/README.md` names only directories and files that exist.
- [ ] `uv run pytest` passes, coverage gate included.

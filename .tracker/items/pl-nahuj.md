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
### Summary
Convert the synthetic fixture trees under `tests/fixtures/` to the new layout, and write the one-time converter that moves a JSON tracker to YAML and Markdown.

### Scope
- `plan convert` (or a one-off script) turns `config.json` into `config.yml`, each milestone into `milestones/<id>.md`, and each item into `items/<id>.md` with a drawn ID and `type: feat`. Fields GitHub owned are left for the import (pl-veles).
- `.cache/gh/` drops out of every fixture tree.
- `broken/` trees named for rules that no longer exist (`done-but-open`, `blocker-outside-repos`) are removed or renamed for the rule that replaces them.
- `broken/` gains a tree for each rule design 0001 §9 adds, and `test_every_section_9_rule_with_a_message_has_a_tree` loses its `xfail` mark.
- `tests/fixtures/README.md` describes the new layout.

### Acceptance
- Every `valid/` tree loads with the new store and schemas.
- Each `broken/` tree fails on exactly its one named rule.
- The converter is lossless for every field the new schema keeps.

### Tests
`tests/test_fixtures.py` over the converted trees; a converter test from a JSON tree to the expected YAML tree.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the converter is the migration path for any JSON tracker
- [ ] L7 Usability and accessibility
- [x] L8 Testability: fixtures stay synthetic
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

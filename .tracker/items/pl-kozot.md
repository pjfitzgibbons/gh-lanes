---
title: "Schemas: Item, Milestone and Config for file-native trackers"
type: feat
status: Todo
estimate: 3
priority: P1
ordinal: 500
lane: model
milestone: bootstrap
---
### Summary
Change the models in `model.py` and `config.py` to the fields ADR 0008 puts in the files. GitHub identity goes, and the tracker owns title, labels, parent and blocked-by.

### Scope
- Item front matter, in this order: `title`, `type`, `status`, `estimate`, `priority`, `ordinal`, `lane`, `milestone`, `labels`, `parent`, `blocked_by`, `started`, `baseline`. `type` is `Literal["feat", "bug", "chore"]` and required. The ID is the file stem. `issue`, `node_id`, `draft` and `repo` go.
- `blocked_by` entries are `"<id> - <title>"`; the ID part is parsed and authoritative (`G7`).
- Milestone front matter: `title` and `order`; the exit criterion is the body. The ID is the file stem.
- Config: `prefix` added; `repos` names member repos by path only; `stale_after_minutes` and `write_pause_seconds` go.
- Discovery finds `.tracker/config.yml`, and a `config.json` tracker fails with a pointer to the converter.
- Out of scope: reading files from disk (pl-ganot) and resolving IDs (pl-jamup).

### Acceptance
- This repo's `.tracker/` validates against the new models.
- An unknown key, a wrong type, or an estimate outside 1, 2, 3, 5 fails naming the file.

### Tests
`tests/test_model.py` and `tests/test_config.py` rewritten for the new fields.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: JSON trackers and their fields stop loading; the converter handles them
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [x] L11 Invariants: estimates stay `Literal[1, 2, 3, 5]`
- [ ] L12 Offline and concurrency

---
title: "Import each repo's .tracker/ items into Redmine"
type: chore
status: Todo
estimate: 3
priority: P2
ordinal: 200
lane: infra
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
---
### Task
Import, once, every item in gh-plan's and tempotag's `.tracker/items/` and `.tracker/archive/` into Redmine, keeping each body ([ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md), *Consequences*):
- Each item becomes an issue in its repo's project: title, body, status (Done imported closed, Icebox as Icebox), `Points`, `Lane`, priority, its milestone's version, and its old ID in an `Old ID` custom field.
- `parent` becomes the parent issue, and `blocked_by` a `blocks` relation, once every issue exists.
- A dry run prints what it would create and writes nothing.

### Guardrails
- `.tracker/` stays in each repo; pl-nepos removes it once the skills no longer read it.
- Importing closes nothing by commit: commits older than a repository's registration never change a status (ADR 0011).
- Bodies go in as they are; nothing is rewritten on the way.

### Lenses
- [ ] L1 
- [ ] L2 Security
- [x] L3 Privacy and data: a run that stops halfway, then runs again
- [ ] L4 Reliability and failure
- [ ] L5 Performance and limits
- [x] L6 Observability: every field of an item file, and a Done item's start and finish
- [ ] L7 Compatibility and migration
- [x] L8 Usability and accessibility: a dry run, then a run against a throwaway container
- [ ] L9 Testability
- [ ] L10 Operations and cost
- [ ] L11 Docs impact
- [ ] L12 Invariants

### Done
- [ ] Redmine holds one issue per item file in both repos, and the counts match `ls .tracker/items .tracker/archive`.
- [ ] L3: re-running the import creates no duplicate; it finds existing issues by `Old ID`.
- [ ] L6: a check script compares each item file with its issue, field by field, including parent, blocks, start and finish, and reports no difference.
- [ ] L8: the dry run writes nothing, shown by the issue count before and after.

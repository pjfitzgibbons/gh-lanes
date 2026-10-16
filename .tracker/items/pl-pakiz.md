---
title: "Nightly backup and export of Redmine to the USB drive"
type: chore
status: Todo
estimate: 2
priority: P2
ordinal: 300
lane: infra
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
---
### Task
Back Redmine up and export it every night to the USB external drive, not to git:
- A launchd job copies the SQLite database (`sqlite3 .backup`) and the files volume into a dated folder on the drive.
- The same job exports every issue with its journal, relations and custom fields as JSON through the REST API, beside the backup ([`G2`](../../docs/requirements.md)).
- Change [ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md)'s consequence, which says the export is committed in gh-plan, and requirement [`G1`](../../docs/requirements.md), which says "exportable to a committed file", to the USB drive. Agree the wording in chat first.

### Guardrails
- The job never writes into a repo, and never changes Redmine.
- When the drive isn't mounted, the job logs why and exits non-zero; it doesn't write anywhere else.

### Lenses
- [ ] L1 
- [x] L2 Security: every issue body sits on a removable drive
- [x] L3 Privacy and data: the drive unmounted, the Mac asleep at the scheduled hour
- [ ] L4 Reliability and failure
- [ ] L5 Performance and limits
- [x] L6 Observability: a restore from the backup
- [ ] L7 Compatibility and migration
- [ ] L8 Usability and accessibility
- [x] L9 Testability: how many nightly copies the drive keeps
- [x] L10 Operations and cost: ADR 0011's consequence and requirement G1
- [ ] L11 Docs impact
- [ ] L12 Invariants

### Done
- [ ] One run of the job leaves a dated backup and a JSON export on the drive.
- [ ] L2: the drive's volume is encrypted, shown by `diskutil apfs list`.
- [ ] L3: with the drive unmounted, the job exits non-zero, logs why, and writes nothing.
- [ ] L6: a backup restored into a throwaway container shows the same issue count and journal as the live one.
- [ ] L9: the job keeps a fixed number of copies, and removes the oldest beyond it.
- [ ] L10: ADR 0011 and `G1` name the USB drive, not a committed file.

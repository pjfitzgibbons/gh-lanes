---
title: "Redmine fetches each repository's commits without a browse"
type: chore
status: Done
estimate: 2
priority: P2
ordinal: 150
lane: infra
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
started: 2026-10-17T10:22:37Z
---
### Task
Redmine reads a repository's new commits only when someone opens its Repository tab, so `fixes #<n>` waits until then to close the issue, and the issue's `closed_on` is the fetch time, not the commit time (found in pl-dezoj; [survey, *Redmine 7*](../../docs/alternatives-survey.md#redmine-7), `C5`). Settle how Redmine fetches, and keep the live Redmine on its port:
- No scheduled fetch. A sidecar service running `Repository.fetch_changesets` in a loop was built and dropped: the fetch is wanted after a PR merges, not on a timer.
- The post-merge fetch, through Redmine's own `POST /sys/fetch_changesets`, is pl-sijil, in the icebox.
- `redmine/compose.yml` defaults Redmine's port to 3010, where the live Redmine runs, so a plain `up` doesn't recreate it on 3000.
- `redmine/README.md` says how a fetch happens now and gives the new URL.

### Guardrails
- No Redmine core patch, and no hook installed in the repos' `.git`.
- The repositories stay mounted read-only.
- The running container isn't recreated by this change.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the live container's config is unchanged
- [ ] L7 Usability and accessibility
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: redmine/README.md
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [x] pl-sijil holds the post-merge fetch, in the icebox.
- [x] L6: the new `compose.yml`'s config hash matches the running container's, so `docker compose -f redmine/compose.yml up -d` with no `REDMINE_PORT` leaves it running.
- [x] L10: `redmine/README.md` gives `http://127.0.0.1:3010` and says opening the Repository tab fetches now.

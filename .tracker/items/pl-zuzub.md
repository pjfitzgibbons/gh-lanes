---
title: "Redmine fetches each repository's commits without a browse"
type: chore
status: Todo
estimate: 2
priority: P2
ordinal: 150
lane: infra
milestone: redmine
blocked_by:
  - "pl-dezoj - Redmine setup: compose file, projects, custom fields and repositories"
---
### Task
Redmine reads a repository's new commits only when someone opens its Repository tab, so `fixes #<n>` waits until then to close the issue, and the issue's `closed_on` is the fetch time, not the commit time (found in pl-dezoj; [survey, *Redmine 7*](../../docs/alternatives-survey.md#redmine-7), `C5`):
- Fetch every repository's commits on a schedule, with `Repository.fetch_changesets` run in the container (cron, or a loop in a sidecar service in `redmine/compose.yml`).
- Say in `redmine/README.md` how often it fetches and how to fetch now.

### Guardrails
- No Redmine core patch, and no hook installed in the repos' `.git`.
- The repositories stay mounted read-only.
- Velocity's use of the close date (pl-pedug) is that item's call; this one only bounds the lag.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a failed fetch is retried at the next run and stops nothing else
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [x] L8 Testability: checked against a throwaway container and volume
- [x] L9 Operations and cost: one more scheduled job to run
- [x] L10 Docs impact: redmine/README.md
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] A commit with `fixes #<n>` closes issue `#<n>` within one fetch interval, with nobody opening the Repository tab.
- [ ] L3: with one repository's mount missing, the others still fetch, and the next run fetches it once it is back.
- [ ] L8: the checks above ran in a throwaway `redmine:7.0.2` container.
- [ ] L9: the job runs under `docker compose up -d` with no step by hand.
- [ ] L10: `redmine/README.md` gives the fetch interval and the command to fetch now.

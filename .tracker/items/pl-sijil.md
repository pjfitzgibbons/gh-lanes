---
title: "Redmine fetches a repository's commits after each merge"
type: chore
status: Icebox
estimate: 2
priority: P2
ordinal: 150
lane: infra
---
### Task
Redmine reads a repository's new commits only when someone opens its Repository tab, so `fixes #<n>` waits until then to close the issue, and the issue's `closed_on` is the fetch time, not the commit time (found in pl-dezoj, settled in pl-zuzub; [survey, *Redmine 7*](../../docs/alternatives-survey.md#redmine-7), `C5`). Trigger the fetch after a PR merges, through Redmine's own endpoint:
- `setup.rb` switches on *Enable WS for repository management* (`sys_api_enabled`), and the key (`sys_api_key`) is kept outside every repo.
- After a merge, `POST /sys/fetch_changesets?key=<key>&id=<project>` fetches that project's commits (`app/controllers/sys_controller.rb` in 7.0.2).
- Say in `redmine/README.md` when it fetches and how to fetch now.

### Guardrails
- No Redmine core patch, no hook installed in the repos' `.git`, and no scheduled service.
- The repositories stay mounted read-only.
- Velocity's use of the close date (pl-pedug) is that item's call; this one only bounds the lag.

### Lenses
- [x] L1 Security: the key is a credential, out of every repo; the endpoint answers on localhost only
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: a failed fetch leaves the next merge's fetch to catch up
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [ ] L7 Usability and accessibility
- [x] L8 Testability: checked against a throwaway container and volume
- [ ] L9 Operations and cost
- [x] L10 Docs impact: redmine/README.md
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [ ] A merged commit with `fixes #<n>` closes issue `#<n>` once the post-merge fetch runs, with nobody opening the Repository tab.
- [ ] L1: the key is in no repo, and a request without it gets 403.
- [ ] L3: after a fetch fails, the next merge's fetch picks up the commits it missed.
- [ ] L8: the checks above ran in a throwaway `redmine:7.0.2` container.
- [ ] L10: `redmine/README.md` says when it fetches and gives the command to fetch now.

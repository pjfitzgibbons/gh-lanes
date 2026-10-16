---
title: "Redmine setup: compose file, projects, custom fields and repositories"
type: chore
status: In Progress
estimate: 3
priority: P2
ordinal: 100
lane: infra
milestone: redmine
started: 2026-10-16T21:51:08Z
---
### Task
Make gh-plan the Redmine setup [ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md) describes, reproducible from the repo:
- `redmine/compose.yml` runs the `redmine:7.0` image on SQLite in a named volume, on localhost, with `redmine/plugins/lane_board/` mounted and each tracked repo mounted read-only.
- A setup script, Python over the REST API, makes what's missing and changes nothing that's already right: a parent project, one sub-project per repo (gh-plan, tempotag), and an Icebox status the lane board leaves out.
- It also makes the custom fields: `Points` (1, 2, 3, 5, 8, 13), `Lane` (cli, engine, github, infra, model, web), and `Baseline start` and `Baseline finish`, read-only by workflow for every role but the administrator.
- Each milestone becomes a version in the parent project, shared with its tree.
- Each repo is registered as its project's repository, with `refs` and `fixes` as commit keywords.
- `redmine/README.md` says how to start, stop, upgrade and re-run the setup.

### Guardrails
- The API key and the admin password are never committed; the script reads the key from the environment ([`G3`](../../docs/requirements.md)).
- No real personal data in anything committed.
- Backup and export are pl-pakiz's; importing items is pl-japih's.

### Lenses
- [x] L1 : the API key and admin password stay out of the repo
- [ ] L2 Security
- [x] L3 Privacy and data: the setup run twice, or after a half-finished run
- [ ] L4 Reliability and failure
- [ ] L5 Performance and limits
- [x] L6 Observability: the image pinned to a Redmine 7.0 tag the plugin was tested on
- [ ] L7 Compatibility and migration
- [x] L8 Usability and accessibility: checked against a throwaway container and volume
- [x] L9 Testability: one more service to run and upgrade (G4)
- [x] L10 Operations and cost: redmine/README.md
- [ ] L11 Docs impact
- [ ] L12 Invariants

### Done
- [ ] `docker compose -f redmine/compose.yml up -d` starts Redmine 7.0 with the lane board loaded.
- [ ] After the setup script, the REST API lists the projects, custom fields, Icebox status, versions and repositories above.
- [ ] L1: `git grep` finds no API key or password; the script fails with a message when the key is unset.
- [ ] L3: a second run of the setup script reports nothing to change.
- [ ] L6: `compose.yml` pins a `redmine:7.0.x` tag.
- [ ] L8: the checks above ran against a throwaway container, whose volume was then removed.
- [ ] L9: `redmine/README.md` says how to start, stop and upgrade Redmine, and where its data lives.
- [ ] L10: `redmine/README.md` says how to re-run the setup script.

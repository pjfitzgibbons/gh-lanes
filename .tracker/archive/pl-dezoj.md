---
title: "Redmine setup: compose file, projects, custom fields and repositories"
type: chore
status: Done
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
- A setup script, `redmine/setup.rb`, run in the container by `bin/rails runner`, makes what's missing and changes nothing that's already right: a parent project, one sub-project per repo (gh-plan, tempotag), and an Icebox status. Redmine's REST API can create projects and versions but not custom fields, statuses, workflows, settings or repositories, so the script uses Redmine's models directly.
- It also makes the custom fields: `Points` (1, 2, 3, 5, 8, 13), `Lane` (cli, engine, github, infra, model, web), and `Baseline start` and `Baseline finish`, read-only by workflow for every role but the administrator.
- It sets what the lane board and later scripts need: the REST API on, cross-project relations allowed, and the lane board module and its permission given to each project and role.
- The lane board leaves out the Icebox status: no column, and its issues add nothing to a lane's points.
- Each milestone becomes a version in the parent project, shared with its tree.
- Each repo is registered as its project's repository, with `refs` and `fixes` as commit keywords.
- `redmine/README.md` says how to start, stop, upgrade and re-run the setup.

### Guardrails
- The API key and the admin password are never committed, and the setup script needs neither ([`G3`](../../docs/requirements.md)).
- The plugin stays read-only: no write, no migration.
- No real personal data in anything committed.
- Backup and export are pl-pakiz's; importing items is pl-japih's.

### Lenses
- [x] L1 Security: the API key and admin password stay out of the repo
- [ ] L2 Privacy and data
- [x] L3 Reliability and failure: the setup run twice, or after a half-finished run
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: the image pinned to a Redmine 7.0 tag the plugin was tested on
- [ ] L7 Usability and accessibility
- [x] L8 Testability: checked against a throwaway container and volume
- [x] L9 Operations and cost: one more service to run and upgrade (G4)
- [x] L10 Docs impact: redmine/README.md
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

### Done
- [x] `docker compose -f redmine/compose.yml up -d` starts Redmine 7.0 with the lane board loaded.
- [x] After the setup script, the REST API lists the projects, custom fields, Icebox status and versions above, and each repository's commits fetch (REST has no repository listing).
- [x] The lane board shows no Icebox column, and an Icebox issue's points are not in its lane's total.
- [x] L1: `git grep` finds no API key or password, and the setup script reads no credential.
- [x] L3: a second run of the setup script reports nothing to change.
- [x] L6: `compose.yml` pins a `redmine:7.0.x` tag.
- [x] L8: the checks above ran against a throwaway container, whose volume was then removed.
- [x] L9: `redmine/README.md` says how to start, stop and upgrade Redmine, and where its data lives.
- [x] L10: `redmine/README.md` says how to re-run the setup script.

---
title: "Skills, CLAUDE.md and tt work from Redmine issues"
type: chore
status: Todo
estimate: 5
priority: P2
ordinal: 400
lane: infra
milestone: redmine
blocked_by:
  - "pl-japih - Import each repo's .tracker/ items into Redmine"
---
### Task
Move everything that reads items or makes branches onto Redmine issues ([ADR 0011](../../docs/adr/0011-redmine-is-the-tracker.md), *Consequences*):
- `worktask start` reads issue `#<n>` through the REST API, sets it In Progress, and makes `<type>/<n>-<slug>`; `worktask done` cleans up as before.
- `gh-issues` checks and ticks the outline in the issue's description; `post-pr` writes `fixes #<n>` in the commit message and names the issue in the PR body.
- The plan-board recipes check an issue's status in Redmine, not `ready.yml` on `origin`.
- tt reads the issue number from `<type>/<n>-<slug>`.
- `CLAUDE.md` says items are Redmine issues, and drops `plan:` commits and `ready.yml`.
- Then each repo's `.tracker/` is removed, by its own PR.

### Guardrails
- The API key stays out of every repo and every skill file.
- A GitHub PR's `#<n>` also links GitHub's own issue or PR `<n>` (ADR 0011 🔍); check what GitHub links before choosing the PR body's wording.

### Lenses
- [x] L1 : the API key read from the environment
- [ ] L2 Security
- [x] L3 Privacy and data: Redmine down when worktask starts or finishes
- [ ] L4 Reliability and failure
- [ ] L5 Performance and limits
- [ ] L6 Observability
- [ ] L7 Compatibility and migration
- [x] L8 Usability and accessibility: the skills' tests against a throwaway Redmine
- [ ] L9 Testability
- [x] L10 Operations and cost: CLAUDE.md and each skill's SKILL.md
- [ ] L11 Docs impact
- [x] L12 Invariants: the Mac off, so Redmine is down

### Done
- [ ] `worktask start <n>` sets issue `<n>` In Progress and makes its branch and worktree, and tt tags the time to `#<n>`.
- [ ] Neither repo has a `.tracker/` directory on its default branch.
- [ ] L1: `git grep` over the skills and both repos finds no API key.
- [ ] L3: with Redmine stopped, `worktask start` and `worktask done` refuse and change nothing.
- [ ] L12: offline, `worktask start` says Redmine can't be reached, naming the URL it tried.
- [ ] L8: the worktask and gh-issues tests pass against a throwaway Redmine.
- [ ] L10: `CLAUDE.md` and the skills name Redmine issues, with no `plan:` commit or `ready.yml` left.

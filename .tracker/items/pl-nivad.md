---
title: "plan init: create a tracker, or register the current repo with one"
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 13000
lane: cli
milestone: phase-1
blocked_by:
  - "pl-nutem - Root pointer: sibling repos find the tracker without PLAN_ROOT"
  - "pl-gaseb - git.py: repo root and commit helper"
---
### Summary
Add `plan init`, the one way to start a tracker or join one. In a repo with no tracker it creates `.tracker/`. In a component repo it registers that repo with an existing tracker's `config.repos`, and writes the pointer back to the root when the repo is a sibling. Today every `.tracker/` is written by hand, and a tracker without its `.gitignore` would commit the cached pull and its real GitHub data. The `plan` skill's `init` is the working prototype.

### Scope
- **Create**, when discovery finds no tracker:
  - `.tracker/config.yml`, with this repo at `path: "."` and `gh` read from `origin`. `--lanes` is required, and `points_per_week` and `hours_per_point` are flags.
  - `.tracker/.gitignore`, for `.cache/` and `out/`.
  - Milestone files, from `--milestones a,b,c` in order, or from the repo's GitHub milestones ordered by due date. Each gets `order` 100, 200, …, and its `exit_criterion` comes from the GitHub description, or a placeholder that `validate` flags.
- **Register**, with `--root PATH` or when discovery finds a tracker:
  - Adds the current repo to that tracker's `config.repos`: the short name from `--name` or the directory name, `path` relative to the root, and `gh` from `origin`.
  - Edits `config.yml` keeping its comments.
  - Writes the root pointer (the sibling-root ticket) when the repo isn't under the root.
  - Refuses when the `gh` repo is already registered, or the short name is taken.
- **Dry by default.** It prints every file it would write or change, and `--apply` writes them. Some values are derived (the milestones and their order), so it follows the reconcile rule (design 0001 §8.1).
- **Next step:** both modes end by pointing at `plan reconcile`, which creates the item files.
- **The first command in `cli.py`:** `init` creates the Typer app, and #18 adds the query commands to it later, so `init` doesn't wait for the query stack (#13 to #16).
- **Docs:** design 0001 §8.2 gains an `init` row, and the architecture layout says `.gitignore` is written by `init`.
- Out of scope:
  - a per-user list of trackers;
  - moving a repo between trackers;
  - unregistering.

### Acceptance
- In a repo with no tracker, `plan init --lanes api,docs --apply` writes `config.yml`, `.gitignore` and the milestone files, and `plan validate` then exits 0, apart from placeholder exit criteria.
- In a sibling repo, `plan init --root ../tracker-repo --apply` adds the repo to the root's `config.repos` with a relative path, writes the pointer, and `plan next` run from the sibling finds the tracker without `PLAN_ROOT`.
- A second register of the same repo exits 1 and changes nothing. So does a short-name clash.
- Without `--apply`, nothing on disk changes.
- `config.yml`'s comments survive a register.

### Tests
`tests/test_init.py`: create and register in `tmp_path` trees, nested and sibling layouts. `git` and `gh` come from the recorded-output fakes. No network.

### Lenses
- [ ] L1 Security
- [x] L2 Privacy and data: `.gitignore` is written in the same step as the tracker, so the cached pull can't be committed by omission
- [x] L3 Reliability and failure: register is all or nothing, so a refused register leaves `config.yml` untouched
- [ ] L4 Performance and limits
- [x] L5 Observability: the dry run lists every file and every `config.repos` change
- [x] L6 Compatibility and migration: hand-written trackers keep working; `init` refuses to overwrite an existing `config.yml`
- [x] L7 Usability and accessibility: one command per repo, and `gh` and the path are inferred instead of typed
- [x] L8 Testability: create and register run against `tmp_path` trees with git and gh faked
- [ ] L9 Operations and cost
- [x] L10 Docs impact: design 0001 §8.2 (the command), architecture *Layout* (`.gitignore` written by `init`), README setup steps
- [x] L11 Invariants: `origin` and the repo root come through git.py, and GitHub milestones through gh.py (invariant 3)
- [x] L12 Offline and concurrency: create with `--milestones` needs no network; two clones registering different repos edit different lines of `config.yml`

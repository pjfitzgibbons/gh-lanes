---
title: Watch for new gh releases and contract-check the recorded output against them
type: feat
status: Icebox
estimate: 3
priority: P2
ordinal: 12800
lane: infra
milestone: phase-1
---
### Summary
Notice when a new GitHub CLI release changes the output gh-plan depends on, before it breaks a user, the way Dependabot notices a new action version. The offline suite runs against recorded `gh` output (#10), so a new `gh` can't fail it. The re-test has to be a **contract check**: run the `gh` calls gh.py makes (#11) with the new version, and compare the JSON shape (keys, nesting, types) with the recorded fixtures. See design 0001 [*Testing*](docs/design/0001-phase-1.md#testing).

### Scope
- **Pin the version:** `.github/gh-version` holds the version the recorded shapes match (2.102.0 today). The #10 README points at this file.
- **The contract check:** `tests/contract/`, marked so the default `pytest` run skips it.
  - It runs each gh.py call against this repo, read-only, and compares the shape with the recorded JSON.
  - It records keys and types only, never values, so no live data reaches the repo or the logs.
- **The watcher:** a scheduled workflow (weekly, plus `workflow_dispatch`).
  - It reads the latest release with `gh release view --repo cli/cli --json tagName`.
  - If that's newer than the pin, it installs that release from its tarball, verifies the checksum, and runs the suite and the contract check.
  - On a pass, it opens or updates one issue saying "gh X.Y.Z passes; bump the pin". On a failure, it opens or updates one issue with the shape diff.
- **Decide and record in design 0001 §11** why this design, against the alternatives:
  - *Dependabot:* it has no ecosystem for a GitHub release binary 🔍 (its supported ecosystems are package managers, Docker and Actions).
  - *Renovate:* a `customManagers` regex manager on `.github/gh-version` with the `github-releases` datasource 🔍. It opens real PRs, but it's another bot and another config.
  - *A workflow that opens the bump PR itself:* a PR opened with `GITHUB_TOKEN` doesn't trigger `pull_request` workflows ([GitHub docs: triggering a workflow from a workflow](https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#triggering-a-workflow-from-a-workflow)), so CI would never run on it without a PAT, which G3 rules out.
- Out of scope:
  - bumping the pin automatically (Peter bumps it in a PR after a pass);
  - testing older `gh` versions;
  - recording new shapes, which follows #10's README.

### Acceptance
- `.github/gh-version` exists, and the #10 README says the recorded shapes match it.
- `uv run pytest` skips the contract check. `uv run pytest -m contract` runs it against the installed `gh`, and fails with a diff naming the command and the key path when a shape differs.
- The watcher runs on schedule and on dispatch. With the pin set to an older version, a dispatch installs the latest release and opens one issue; a second dispatch updates that issue instead of opening another.
- The workflow uses only `GITHUB_TOKEN`, with `contents: read` and `issues: write`. No secrets, no PAT.
- Design 0001 §11 records the decision and the alternatives.

### Tests
- A unit test for the shape comparison, offline: same shape, a missing key, a type change, an object that became a list (as `blockedBy` did relative to what we first assumed).
- The watcher itself is checked by a dispatch with an old pin, as the acceptance says.

### Lenses
- [x] L1 Security: the installed `gh` is downloaded from cli/cli's release and verified against the release checksums before it runs; the workflow token is limited to `contents: read` and `issues: write`
- [x] L2 Privacy and data: the contract check compares shapes only; no live titles, logins or node IDs are written to the repo, the logs or the issue
- [x] L3 Reliability and failure: one issue per release, updated rather than duplicated; a failed download or a missing checksum fails the run loudly instead of testing the old `gh`
- [x] L4 Performance and limits: weekly, read-only, a handful of `gh` calls per run, far inside the API limits
- [x] L5 Observability: the issue names the version, the result and, on failure, the command and key path that changed
- [x] L6 Compatibility and migration: this is the early warning for `gh` output changes; the pin records which version the fixtures match
- [ ] L7 Usability and accessibility
- [x] L8 Testability: the shape comparison is pure and unit-tested; the contract check stays out of the default offline run
- [x] L9 Operations and cost: one more scheduled workflow on free Actions minutes; nothing to install locally
- [x] L10 Docs impact: design 0001 §11 (the decision), the #10 fixtures README (the pin)
- [x] L11 Invariants: invariant 3 holds, because the contract check calls `gh` through gh.py and the unit suite stays offline
- [x] L12 Offline and concurrency: the default suite stays offline; only the marked contract check needs the network

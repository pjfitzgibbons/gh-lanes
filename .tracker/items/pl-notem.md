---
title: Package as a gh extension
type: feat
status: Icebox
estimate: 2
priority: P2
ordinal: 31300
lane: infra
milestone: phase-3
---
Ship as a gh extension, so `gh extension install pjfitzgibbons/gh-plan` installs it and `gh plan next` runs it. The tool already shells out to `gh` for everything, so it runs under the user's existing `gh` login (G3).

- A script extension: an executable `gh-plan` at the repo root that runs the package with the user's Python, for example `exec uv run --project "$(dirname "$0")" plan "$@"`. gh clones the repo on install and pulls it on `gh extension upgrade`.
- Python and `uv` are prerequisites; the README says so.
- Add the `gh-extension` repo topic.
- Local development: `gh extension install .` symlinks the working copy.

Precompiled per-platform binaries (`gh extension create --precompiled=other`, a frozen build per OS) are out of scope; they get their own ticket if someone without a Python toolchain needs it.

Tests: from a clean clone, `gh extension install .` then `gh plan next --json` against the fixture tree matches `plan next --json`.

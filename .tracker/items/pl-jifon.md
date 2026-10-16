---
title: "VS Code extension: milestones and lanes tree views"
type: feat
status: Icebox
estimate: 3
priority: P2
ordinal: 300300
lane: web
---
Third front end over the same core. TypeScript, likely its own repo: [ADR 0004](https://github.com/pjfitzgibbons/gh-plan/blob/main/docs/adr/0004-python-no-docker.md#alternatives) keeps Node out of this one.

Tree views fed by `plan list|ready|next|why --json`, never by parsing `.tracker/` directly (that would duplicate the planning logic in a second language). Optionally a webview over `plan serve` once Phase 2 exists.

Implies: the `--json` output format (1.12) becomes a stable, versioned contract.

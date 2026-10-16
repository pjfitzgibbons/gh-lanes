---
title: De-number requirements
type: feat
status: Todo
estimate: 3
priority: P2
ordinal: 600
lane: infra
milestone: phase-0
---
Replace the requirement IDs in `docs/requirements.md` (`A1` … `I5`) with named requirements, each with a descriptive anchor that contains no number. Then sweep every reference to an ID: `docs/`, `CLAUDE.md`, `.github/workflows/test.yml` (comment cites G3), code and test comments, and the issue bodies that cite IDs (#3, #8, #24, #30, #32, #33, #46, and the title of #39, at the time of writing; re-search before starting).

Decide first: `alternatives-survey.md` uses the IDs as its matrix row keys and is a working doc that is otherwise left alone. Either it keeps the old IDs with a mapping, or it is swept too.

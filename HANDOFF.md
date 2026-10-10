# Handoff — gh-lanes, first session

Written 2026-10-10 by the session that designed this tool inside
`~/programming/ms-security/ms-security-docs`. That session is done. This repo is empty apart from
the docs and config described below.

## What this is, in one paragraph

GH Lanes is a replacement for **GitHub Projects v2**, not for GitHub Issues. Six tool surveys and
two hands-on tests established that Issues is fine and the *planning* layer is what fails: custom
fields live on the project item rather than the issue, there is no dependency relationship, no
readable rank, some fields are display-only, a board cannot group by labels, and bulk field writes
trip a secondary rate limit at about twenty mutations. GH Lanes keeps Issues underneath and owns
estimates, lanes, priorities, dependencies, baselines and every view.

## Read in this order

| File | What it gives you |
|---|---|
| `docs/requirements.md` | The spec — 37 requirements in 9 groups, with MoSCoW priorities, **and a table of the 14 places GitHub Projects actually failed**, each verified rather than read in a review |
| `docs/adr/0001-architecture.md` | The architecture. Definitions, the storage decision, platform choice, CLI surface, data model, the GitHub boundary, phasing, and an appendix of ~20 rejected options |
| `docs/design/0001-phase-1.md` | **Start here for code.** Module layout, pydantic model, SQLite DDL, all 13 validation rules with their messages, the `lanes next` algorithm, and the work breakdown |
| `docs/alternatives-survey.md` | Why this is being built at all: eleven tools scored against the same requirements, with the two hands-on test results |

`CLAUDE.md` carries the hard rules. **Read it first** — see the warning below.

## State of the repo

| Present | Note |
|---|---|
| `docs/` | The four documents above. Moved from `ms-security-docs`, where pointers now reference this repo |
| `.claude/settings.json` | `attribution` off, `deny` for secrets and for `git push` / `rebase` / `reset`, minimal `allow` |
| `.claude/hooks/no_ai_attribution.py` + test | The attribution hook. **18 cases in 6 methods, verified passing in this repo** |
| `.gitignore` | Python build output, `.tracker/.cache/`, `.tracker/out/`, per-person Claude state |
| `CLAUDE.md` | Repo instructions and the design invariants |

**Nothing is committed yet.** `main` has no commits. There is no `pyproject.toml`, no `src/`, no
tests, and no `README.md` — all of those are the first session's work.

## ⚠️ The thing most likely to bite you

**This repo inherits nothing.** It sits at `~/programming/gh-lanes`, outside the
`~/programming/ms-security/` workspace, and there is no `CLAUDE.md` anywhere above
`~/programming/`. `CLAUDE.md` inherits only from ancestor directories, and `settings.json` anchors
to the launch directory. So the originating project's rules — no AI attribution, synthetic data
only, cite-or-flag — **do not reach here by inheritance.** They are restated in `CLAUDE.md` and
enforced by the committed hook, which is why both were set up before the first commit rather than
after.

## Decisions already made — do not relitigate without reading the ADR

1. **Python 3.12+, FastAPI, Jinja2, HTMX, SQLite, Typer, pydantic v2.** The decisive factor is that
   the tool **shells out to `gh`** instead of using a GitHub library, because `gh` is already
   authenticated and a library would need a PAT. Requirement `G3` forbids a new credential.
2. **No Docker on the run path.** The app reads a git working tree and calls `gh` with the host's
   credentials; containerising means bind-mounting both. Docker is for CI only.
3. **Go was the considered alternative** and lost on one axis only — it wins on single-binary
   distribution, loses on fitting a Python-tooled project. The argument is in the ADR if you want to
   revisit it before any code exists. After that, don't.
4. **No Mermaid.** Charts are generated HTML — CSS Grid for lanes and bars, inline SVG for
   dependency arrows. This is Phase 2.
5. **Phase 1 is CLI only, 32 points.** Its acceptance criterion is explicit: **`lanes next` must be
   good enough to work from daily.** If it is not, Phase 1 failed and Phase 2 is mandatory.

## Open questions — resolve these before writing `model.py`

1. **`status` ownership.** GitHub has only open/closed, so `Todo` / `In Progress` / `Blocked` must be
   tracker-owned — but the ADR's field-ownership table does not list `status`. This is the one gap in
   the otherwise clean disjoint-ownership story. Options: store it; or derive `Blocked` from unmet
   dependencies and `In Progress` from branch existence, which is better but needs Phase 3 branch
   detection.
2. **`ordinal`.** Adopt a writable integer rank, or rely on `priority` plus issue number? A rank
   makes `lanes next` tie-free. Backlog.md's was genuinely useful in testing.
3. **`reconcile` default.** Report only, or create missing item files? Leaning report-by-default,
   create on `--apply`.

## Suggested first steps

1. Read `CLAUDE.md` and `docs/design/0001-phase-1.md`.
2. Resolve the three open questions above, recording each as a short ADR amendment.
3. **Commit what is already here first** — docs, config and the hook — so the attribution control is
   in history before any generated content lands. Branch first; never commit to `main`.
4. `pyproject.toml` with uv, then `config.py` and `model.py`, which are the cheapest items and
   unblock everything else.
5. Write `validate.py`'s tests **before** its rules. Cycle detection and `lanes next` selection are
   the two places a bug is silent, and the design doc specifies a case per branch.
6. Open the Phase 1 work breakdown as issues in this repo — **the tracker's own backlog is the first
   thing it will track.** That is the dogfooding, and it is also the only realistic way to find out
   whether `lanes next` is actually useful.

## The data lives elsewhere

The tool is here; the planning data it operates on is `~/programming/ms-security/ms-security-docs/.tracker/`.
That separation is deliberate — the tool is general-purpose, the data belongs to that project. There
are currently **24 live items in GitHub Projects v2** on `pjfitzgibbons/contoso-health-partners`
project #2 that need migrating into `.tracker/items/*.yml`; that migration is a 2-point item in the
Phase 1 breakdown, and the existing field values (`Story Points`, `Priority`, `Lane`, `Depends On`)
are the fixture data you want for tests.

# ADR 0001: Architecture for a bespoke GitHub-integrated tracker

**Status:** proposed · **Inputs:** [`requirements.md`](requirements.md) ·
[`alternatives-survey.md`](alternatives-survey.md)

## Definitions

The tool is `gh-lanes` (product: GH Lanes, CLI: `lanes`), in its own repo. Its *data* lives in
`.tracker/` in whichever repo is being planned. See [design 0001](design/0001-phase-1.md).

| Term | Definition |
|---|---|
| **Tracker** | A local CLI plus optional localhost web UI that owns the *planning* layer over GitHub Issues. Not an issue tracker |
| **Item** | One YAML file, `.tracker/items/<n>.yml`, holding the planning fields for one GitHub issue. Committed. The source of truth |
| **Index** | `.tracker/.cache/index.db`, SQLite. A join of GitHub facts and item files. Derived, gitignored, rebuildable |
| **GitHub-owned field** | title, body, state, labels, assignee, comments, sub-issue links, `closedAt`. Read, never stored in an item file |
| **Tracker-owned field** | estimate, priority, status, ordinal, lane, `depends_on`, baseline, milestone. Written to item files, never pushed to GitHub |
| **Lane** | A contention domain. Items in a lane touch the same files, so they run one at a time. Single-valued |
| **Milestone** | Ours, not GitHub's. An Act or Interlude. Spans all four repos |
| **Baseline** | A frozen start/finish pair, written once per milestone at its checkpoint, never recomputed |
| **Draft** | An item with no GitHub issue yet (`draft: true`). Expected state, created offline |
| **Orphan** | An item whose `node_id` resolves to nothing. Unexpected state, needs a human |
| **needs-triage** | An item with identity but no estimate or lane. A warning, not an error |
| **Pull** | Read GitHub into the index. Automatic, idempotent, no writes to item files |
| **Reconcile** | Compare issues to item files; create missing files, report orphans. Explicit, dry by default |
| **Mirror** | The one write-back to GitHub: the `[N]` estimate prefix in an issue title |
| **Freeze** | Compute and write baselines for one milestone. Explicit, dry by default |

## The premise

Six surveys and two hands-on tests produced one consistent result: GitHub Issues is fine.
Projects v2 is what failed. Issues gave us identity, bodies, state, labels, milestones,
sub-issues, an authenticated CLI and zero credentials. Every ❌ in the matrix came from the
*planning* layer: fields living on the project item instead of the issue, no dependency
relationship, no readable rank, display-only fields, a board that cannot group by labels, and a
secondary rate limit that trips at twenty mutations.

So this is a replacement for Projects v2 that keeps Issues underneath, not a tracker.
That reframing removes roughly half the work: no issue CRUD, no comments, no notifications,
no auth, no multi-user, no permissions, no email.

### What GitHub keeps owning

Identity (`#23`), title, body, open/closed, labels, assignee, comments, sub-issue links,
repository, and the commit and PR graph.

### What we own

Estimate · priority · **status** (GitHub has only open/closed) · **ordinal** · lane · dependencies ·
baseline start and finish · velocity · milestone membership *across repos* · derived actuals · the
ready-queue computation · every view.

## Core decision: git is the database, SQLite is a disposable index

The binding requirements are **G1** (tracking data is reviewable evidence: diffable, readable with
no account) and **G3** (no new credential). Both are satisfied by one choice:

```
repo/.tracker/
  items/23.yml          ← one file per issue. THE source of truth. Committed.
  milestones/act-0.yml  ← our milestones, which span repos
  config.yml            ← pointsPerWeek, lanes, statuses, priorities
  .cache/index.db       ← SQLite. Derived, gitignored, deletable, rebuilt in seconds
```

**Nothing authoritative lives in the database.** SQLite exists so the web UI can sort, filter and
join without re-parsing 60 YAML files per request. Drop it at any time and `lanes reindex`
rebuilds it from the committed files.

What this buys, requirement by requirement:

- **G1 ✅ G2 ✅** — the data *is* committed YAML. Diffable, readable in a browser on GitHub, no
  export step and no lock-in.
- **G5 ✅ free** — change history on an estimate or a baseline is `git log -p .tracker/items/23.yml`.
  Who changed it and when, signed, with the commit that explains why. Better than any surveyed
  tool, and it is the requirement that matters most given where Act 6 goes.
- **G4 ✅** — no database to back up, patch or validate. A corrupted index is a `rm` away.
- **H2 ✅** — bulk writes are file writes. Twenty-four lane assignments is one commit.
- **C3/C4 ✅** — a frozen baseline is a value in a committed file. Re-baselining shows up as a diff
  with a commit message. The requirement that no free tool satisfied is nearly free
  here.
- **B3 ✅** — validation runs at write time, in our own code. That is server-side enforcement of the
  >5-must-split rule, which no surveyed tool offers.

🏛 This project's subject matter is audit trails and evidence. A tracker whose history is git
history is the same argument applied to our own tooling: derived facts over typed assertions, and
a record that an auditor could follow.

## Platform recommendation: Python · FastAPI · HTMX · SQLite · shell out to `gh`

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Language | **Python 3.14+** (the floor is the one version CI tests) | Already this project's tooling language: the attribution hook, the `wp-publish` skill and the gantt generator are all Python. `uv 0.11.7` is installed. Adding a second toolchain to a docs repo costs more than it returns |
| GitHub access | **subprocess to `gh`** | The decisive choice: `gh` is already authenticated, so G3 is satisfied natively with no PAT anywhere. PyGithub or httpx would each need a token, the exact cost that killed the auto-add Action |
| Web | **FastAPI + Jinja2 + HTMX** | No build step, no npm, no bundler, server-rendered HTML. HTMX gives drag-and-drop and partial updates with attributes rather than a front-end app. For a single-user local tool, a React SPA is the wrong complexity |
| Index | **SQLite via stdlib `sqlite3`** | No server, no driver, no ORM needed. It is a cache, so schema migrations are irrelevant: delete and reindex |
| Validation | **Pydantic v2** | Schema for the YAML files, which is how `B3` becomes server-side instead of a lint |
| CLI | **Typer** | One core library behind both front ends (see *CLI surface*). CI and hooks call the CLI |
| Charts | **Generated HTML**: CSS Grid for bars and lanes, inline SVG for dependency arrows | No Mermaid, no JS charting library, no build step. See *Rendering* |
| Packaging | **`uv run`**, no Docker | See below |

### Why not Docker

The app's entire job is to read and write a **git working tree** and to call `gh` with **the host's
credentials**. Containerising means bind-mounting the repo, bind-mounting `~/.config/gh`, and
reconciling uid/gid. That is more moving parts than `uv run lanes serve`, for a single-user tool
bound to localhost. Docker's wins (isolation, reproducible deps, multi-service) do not apply: there is one
service, `uv.lock` already pins deps, and isolation from the repo is the opposite of what we want.

**Where Docker earns its place:** a `Dockerfile` for *CI* so the validation CLI runs hermetically,
and as a reproducibility escape hatch if the thing is still wanted in three years. Ship it as
optional, not as the run path.

## CLI surface

One core library; the CLI and the web UI are two front ends over it. Neither shells out to the
other.

Reads are implicit and writes are deliberate: pull runs automatically, while reconcile, freeze,
mirror and push-drafts are dry by default. The rule and the command set are in
[design 0001, *Reads and writes*](design/0001-phase-1.md#reads-and-writes) and
[*Commands*](design/0001-phase-1.md#commands). Phase 1's acceptance criterion is that `lanes next`
is good enough to work from ([design 0001, *Scope*](design/0001-phase-1.md#scope)).

## Data model

An item file holds identity and tracker-owned fields only. The schema and an example are in
[design 0001, *Data model*](design/0001-phase-1.md#data-model).

## The GitHub boundary: how sync works

**There is no bidirectional sync, because the two systems never hold the same field.** That is why
"git is the database" does not collapse into a reconciliation problem.

### Field ownership is disjoint

| Field | Authority | Stored in YAML? | Stored in index? |
|---|---|---|---|
| title · body · state · labels · assignee · comments · sub-issue links · `closedAt` | **GitHub** | no | yes, as a cache |
| estimate · priority · status · ordinal · lane · `depends_on` · baseline · our milestone | **Files** | yes | yes, as a cache |
| the `[N]` title prefix | GitHub, written by us | no | — |

GitHub-owned fields are *never copied into a tracker file*. No
copy means no divergence means nothing to reconcile. Tracker-owned fields are never pushed to
GitHub, so GitHub cannot contradict them either. The two sets are disjoint, and the only overlap is
one mirrored field in one direction.

**`depends_on` stays tracker-owned, although GitHub has native dependencies.** The GraphQL
`Issue` type has `blockedBy` / `blocking` / `issueDependenciesSummary`, with
`addBlockedBy` / `removeBlockedBy` mutations, and `gh issue edit` has `--add-blocked-by` /
`--add-blocking` (verified against the API on `gh` 2.102.0). GitHub's field is not read, written
or reconciled. Revisit if experience shows the native field would serve better.

### Three operations

```
          ┌──────────────── GitHub (authoritative for identity) ───────────────┐
          │  #23  title · state · labels · closedAt · sub-issues              │
          └───────────────────────────┬───────────────────────────────────────┘
                         (1) PULL     │ read-only, `gh`, no token
                                      ▼
   .tracker/items/23.yml ───────▶ .cache/index.db ◀─── (3) MIRROR, one field only
   estimate · lane · deps          a JOIN of both,        `[N]` → issue title
   baseline · priority             nothing authoritative
   ▲                                      │
   │ (2) RECONCILE: file⇄issue membership │
   └──────────────────────────────────────┘
```

**1. Pull: read-only, idempotent, no credential.**
`gh issue list --repo <r> --state all --json number,id,title,state,labels,closedAt` per repo, plus
one `gh api graphql` for sub-issue links. Writes only to the index, never to YAML. Records
`fetched_at`; commands warn when the cache is stale and `--offline` works entirely from it, since
every tracker-owned field is local.

**2. Reconcile: the only operation that creates item files or changes them to match GitHub.** This
is today's lint, promoted to a first-class step. Where a case needs a judgement, it *reports* rather
than guessing:

- an open issue with no item file → offer to create one (that is `H5`, automatic membership)
- a closed issue whose item is not `Done` → set `status: Done`
- a reopened issue whose item is still `Done` → report it; the earlier status is not recorded
- an item file whose `node_id` resolves to nothing → orphan, report it

**3. Mirror: the single write-back.** When `estimate` changes, rewrite the title's `[N]` prefix.
One field, one direction, with drift detection already specified. **Every additional write-back
would be a new reconciliation problem, so there are none.**

### Creation paths and the ordering rule

Issues arrive two ways and only one of them involves the tracker. Both must end in the same state.

#### A. Cold-created on GitHub: web UI, phone, a bot, a naive user

GitHub assigns the number and `node_id`. No item file exists, and **nothing is lost**:

1. **Pull** brings it into the index like any other issue, with title, state and labels present.
2. **Reconcile** sees an issue with no item file and writes
   `.tracker/items/24.yml` containing **identity only**: `issue`, `node_id`, `repo`. No estimate,
   no lane, no milestone. **It never guesses a planning value.**
3. Because it has no milestone, **`F1` makes it `Icebox` by definition**. An untriaged issue *is*
   deferred until a human triages it, so the icebox is where unplanned work lands.
4. `lanes validate` reports it as **`needs-triage`**: has identity, missing estimate or lane.
   A **warning with a count**, not a failure: a naive user filing an issue has done nothing wrong.
   It becomes a failure only when an Act is being frozen, where an unestimated item would corrupt
   the baseline.
5. It carries **no `[N]` title prefix**, because the mirror only runs once an estimate exists.
   Consistent by construction rather than by special-casing.

🔑 **If the user also set a GitHub milestone or labels**, reconcile surfaces them as a *suggestion*
in the triage report. It does not import them, because GitHub's milestones are not ours (`A2`) and
mapping one onto an Act is a judgement call.

#### B. Created locally by CLI or agent

The complication: **we cannot allocate an issue number.** That is GitHub's to assign. So there are
two sub-paths and the default matters.

By default `lanes new` works online: it creates the GitHub issue, then writes the item file, then
commits. Offline, `lanes new --draft` writes a draft file with no issue, and `lanes push-drafts`
later creates the issue and renames the file. Both command sequences are in
[design 0001, *Commands*](design/0001-phase-1.md#commands).

The rename is visible in git history, so a draft's provenance survives. `draft: true` is explicit
rather than inferred from a null `issue:`, because reconcile must distinguish **a draft (expected to
have no issue yet)** from **an orphan (unexpectedly has none)**. Those look identical without the
flag and mean opposite things.

#### The ordering rule: GitHub first, then the file

`lanes new` calls `gh` first and writes the file second, and that order is deliberate. Compare the two ways a
crash between them can land:

| Crash leaves | Who notices | Cost |
|---|---|---|
| An issue with no file | Reconcile, automatically | Self-healing: it is scenario A, which already works |
| A file with no issue | A human reading an orphan report | Needs a decision: create the issue, or delete the file? |

**Choose the failure mode that repairs itself.** Writing the file first would create orphans
requiring judgement; writing GitHub first degrades gracefully into the cold-create path we have to
support anyway. The naive-user path is therefore the recovery mechanism for the CLI path, not an edge case to
tolerate, which is why it is worth making robust first.

A corollary for sequencing: **build reconcile before build create.** Reconcile alone makes the whole
system tolerant of every creation route, including ones we have not thought of.

### Sub-issues: GitHub owns the relationship, we own the planning

Checked against `A4`, `A5`, `A6`. GitHub behaviour as of 2026-10-10.

| Need | Met? | By what |
|---|---|---|
| `A4` sub-tasks are first-class and schedulable | ✅ | A sub-issue *is* an issue, so it gets its own number, its own item file, and therefore its own estimate, lane, baseline and dependencies |
| `A4` appear in every view | ✅ | **`Auto-add sub-issues to project` is already enabled**, so children join without ceremony |
| `A5` parent roll-up without double-count | ✅ | `subIssuesSummary{total completed percentCompleted}` from GitHub, plus our rule that a parent with children carries no estimate. Sum is computed in the index |
| `A6` arbitrary depth | ✅ | 8 levels, against the two we use |
| Per-parent capacity | ✅ | 100 children, far more than splitting an item produces |
| Cross-repo parent/child | ✅ | Documented, and `gh` accepts a URL as well as a number for `--parent` and `--add-sub-issue`. ⚠️ Docs-verified, not hands-tested; only one repo exists today. Confirm during Act 1 |

**So no tracker-side parent field.** Parentage joins the GitHub-owned column alongside title, state
and labels: read via `Issue.parent`, cached in the index, never written to an item file. The only
tracker-side rule is the one `A5` needs, *a parent with children must have an empty estimate*,
which `validate` enforces.

`gh` wraps sub-issue writes fully on 2.102.0, so they need no raw GraphQL:
`gh issue create --parent` and `gh issue edit --add-sub-issue|--parent|--remove-parent`. Reads come
from one query over `Issue.parent` / `subIssues` / `subIssuesSummary`.

The cross-repo answer is the one that mattered. Had sub-issues been same-repo only, the Act 1
migration would have broken every split parent whose children moved to an app repo, and parentage
would have had to live in our files after all.

### The join key, and why `issue:` alone is wrong

`gh issue transfer` changes an issue's number, so `node_id` is the real key and `issue:` is a cache.
The details are in [design 0001, *Identity*](design/0001-phase-1.md#identity).

### Failure cases, and what happens

| Event | Effect | Handling |
|---|---|---|
| Issue transferred to another repo | `issue:` goes stale, `node_id` still resolves | Reconcile rewrites `issue:` and `repo:`. No data lost |
| Issue deleted | `node_id` resolves to nothing | Orphan report; file kept until a human decides |
| Issue reopened | `closedAt` clears | Derived `actual_finish` is computed, never cached in YAML, so it just changes. Reconcile reports the item if it is still `Done` |
| Title edited on GitHub | `[N]` prefix may be dropped | Mirror drift detected, re-applied on next run |
| Estimate edited in the file | GitHub title now stale | Mirror re-applies |
| Offline | Pull fails | Everything tracker-owned still works; index serves stale reads with a warning |
| Two sessions edit **different** items | Two different files | Git merges cleanly. This is why it is one file per item, not one big YAML |
| Two sessions edit the **same** item | Normal git conflict | A ten-line YAML conflict a human can read, unlike a database merge |

## Rendering: generated HTML, not Mermaid

**Mermaid is not used.** All charts, graphs and tables are generated HTML.

| Artifact | Technique |
|---|---|
| Lane board | CSS Grid: lanes are rows, statuses are columns |
| Gantt / timeline bars | CSS Grid: a bar is a column span; duration is `grid-column: start / span n` |
| Dependency arrows | Inline SVG overlaid on the grid |
| Tables, roll-ups, ready queue | plain `<table>`, server-rendered |
| Colour / status | CSS custom properties, with shape or label as well as colour so nothing depends on hue alone |

No JS charting library and no build step: Jinja templates emit HTML, CSS does the layout. Interaction
in Phase 3 is HTMX attributes.

### What this gains

**Dependency arrows become possible.** Mermaid `gantt` sequences with `after` but **draws no
arrows and has no critical path**, so a dependency affects bar position only and the reader cannot
see *why*. Inline SVG over a CSS grid draws the edges, so the chart shows the real structure.

Also: no 44-character label truncation, real tooltips, and a lane board and a timeline that are the
same template with different column semantics.

### What this costs

⚠️ **GitHub does not render the charts.** Mermaid in a committed `.md` renders natively in the
GitHub UI, so anyone with the link sees the chart with no tooling. An HTML file in a repo displays
as **source**. So:

- The charts are **build artifacts, not committed evidence**. They are generated into
  `.tracker/out/` and gitignored.
- **`G1` is unaffected**, because `G1` is about the tracking *data* (the item YAML), which is still
  committed and diffable. It is the *rendering* that stops being viewable without running something.
- If a chart is ever needed in a blog post or for someone with no checkout, it is a screenshot or a
  published page, not a repo file.

That is a real loss; the gain is a chart that shows dependencies at all.

## Alternative: Go

Go loses to Python on one axis only.

| | Go | Python |
|---|---|---|
| Distribution | **Single static binary.** No venv, no interpreter version, runs in 2031 | `uv run`, needs Python + lockfile |
| Reproducibility | **Strong**; matters for a public teaching artifact | Good, via `uv.lock` |
| SQLite | `modernc.org/sqlite`, pure Go, **no cgo** | stdlib |
| Web | `html/template` + HTMX; `templ` for typed templates | Jinja2 + HTMX |
| YAML | `goccy/go-yaml` | ruamel.yaml, **round-trips comments** |
| Validation | hand-written or `go-playground/validator` | **Pydantic v2, less code** |
| Fit with repo | **New language in a Python/Markdown repo** | Already the tooling language |

**Choose Go if** the tracker should outlive the project as a standalone artifact a reader can
`go install` and run. The single-binary story is better, and "still runs in three years"
matters for a blogged project.

**Choose Python because** it is already here. Every existing tool in this repo is Python, `uv` is
installed, Pydantic removes a chunk of validation code, and ruamel.yaml round-trips comments,
which matters when humans hand-edit the item files, as they will.

Rejected: TypeScript/Node (a build step and `node_modules` in a docs repo, for a tool with no rich
front end), Rust (compile times and ceremony for a CRUD app), Ruby/PHP (no presence in this
workspace).

---

## Appendix: options rejected

### Storage

| Option | Why not |
|---|---|
| **Postgres** | Fails `G1` and `G4`. A service to run, back up and patch, holding the authoritative data outside git, for a single-user tool with ~60 rows |
| **SQLite as source of truth** | Fails `G1`/`G5`. A binary blob is not diffable and not reviewable; `git log -p` on it says nothing |
| **One big YAML file** | Every edit touches one file, so git history becomes useless for "who changed this estimate" and concurrent sessions conflict constantly |
| **Issue body frontmatter** | Tempting, since it needs no new files, but it fights GitHub's editor, invites human mangling, and Backlog.md's test showed what silent frontmatter loss looks like |
| **Git notes / orphan branch** | Technically elegant, practically invisible. Fails `G1`'s "readable by someone with no account" |
| **JSON instead of YAML** | No comments. Item files will be hand-edited and the comments are the explanation |

### GitHub access

| Option | Why not |
|---|---|
| **PyGithub / Octokit / raw httpx** | Each needs a PAT, so it fails `G3`: the exact cost that killed the auto-add Action |
| **GitHub App** | Worse: a key *and* an install, and apps cannot act on user-owned projects anyway |
| **Webhooks** | Needs a public endpoint for a localhost tool. Poll on demand instead |

### Web stack

| Option | Why not |
|---|---|
| **React / Vue / Svelte SPA** | A build step, `node_modules`, and an API boundary, for a single-user local board. HTMX does drag-and-drop with attributes |
| **Streamlit / Gradio** | Fast to start, fights you on layout, and a kanban board is exactly the layout they are bad at |
| **TUI (Textual)** | Attractive and much cheaper, but a board is a 2-D spatial artifact and the chart needs to be shareable in a blog post |
| **Static site generator** | Read-only by construction, so Phase 3 is impossible. Phase 2's `lanes render` is the useful part of this idea without the framework |
| **Mermaid** | Renders free on GitHub, but draws no dependency arrows and has no critical path, which is what a dependency chart is for. Also truncates labels and has no tooltips |
| **A JS chart library** (Chart.js, D3, Frappe Gantt) | A dependency and a build step for layout that CSS Grid already does. D3 would be justified only if the dependency graph needed force-directed layout |

### Scope

| Option | Why not |
|---|---|
| **Replace GitHub Issues too** | Doubles the work, loses sub-issues, comments, PR linkage and `gh`, and gains nothing the matrix asked for |
| **Fork an existing tool** | Backlog.md would need an estimate field *and* a safe-frontmatter fix *and* lane grouping; Redmine would need a Ruby plugin. Owning a fork of someone else's data model is worse than owning 2,000 lines of our own |
| **Two-way field sync** | Rejected on principle (see the boundary section). It is the sync-drift pathology this project exists to criticise |

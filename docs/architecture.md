# Architecture

**Requirements:** [`requirements.md`](requirements.md) · **Decisions:** [`adr/`](adr/) ·
**Design:** [design 0001](design/0001-phase-1.md), [design 0002](design/0002-tracked-time.md)

<a id="purpose"></a>
## 1. Purpose

GH Plan is a planning layer over GitHub Issues. Issues already provide identity, bodies, state,
labels, sub-issues, an authenticated CLI and no new credential. What fails is the planning layer of
GitHub Projects v2: fields live on the project item instead of the issue, there is no dependency
field and no readable rank, some fields are display-only, a board cannot group by labels, and
writing project fields trips a secondary rate limit at about twenty mutations.

gh-plan replaces Projects v2 and keeps Issues underneath. It has no issue CRUD, comments,
notifications, auth, multi-user support, permissions or email. Replacing GitHub Issues as well
would double the work and lose sub-issues, comments, PR linkage and `gh`. Forking an existing tool
would mean owning someone else's data model; the [alternatives survey](alternatives-survey.md)
records where each candidate fell short.

The tool (`gh-plan`, product GH Plan, CLI `plan`) lives in its own repo. Its data lives in
`.tracker/` in whichever repo is being planned ([ADR 0002](adr/0002-tracker-per-repo.md)).

<a id="definitions"></a>
## 2. Definitions

| Term | Definition |
|---|---|
| Tracker | A local CLI plus an optional localhost web UI that owns the planning layer over GitHub Issues. Not an issue tracker |
| Item | One JSON file, `.tracker/items/<repo>/<n>.json`, holding the planning fields for one GitHub issue. `<repo>` is the repo's short name in `config.repos`. Committed. The source of truth |
| Index | `.tracker/.cache/index.db`, SQLite, built from the item files and the cached pull. A join of GitHub facts and item files. Derived, gitignored, rebuildable |
| GitHub-owned field | A field GitHub holds (§3.1). Read, never stored in an item file |
| Tracker-owned field | A field the tracker holds (§3.2). Written to item files, never pushed to GitHub |
| Time source | An external time tracker, read through one adapter per vendor. Optional ([ADR 0006](adr/0006-tracked-time.md)) |
| Snapshot | The total tracked time for an item, written into its file when the issue closes, with the tracker and tag it came from |
| Lane | A contention domain. Items in a lane touch the same files, so they run one at a time. Single-valued |
| Milestone | The tracker's own milestone, not GitHub's. It has an exit criterion and can span every repo in `config.repos` |
| Baseline | A frozen start/finish pair, written once per milestone at its checkpoint and changed only by a deliberate rebaseline |
| Draft | An item with no GitHub issue yet (`draft: true`). Expected state, created offline |
| Orphan | An item whose `node_id` resolves to nothing. Unexpected state, needs a human |
| needs-triage | An item with identity but no estimate or lane. A warning, not an error |
| Pull | Read GitHub into the index. Automatic, idempotent, no writes to item files (§6.1) |
| Reconcile | Compare issues to item files: create missing files, keep `Done` and the time snapshot in step with closed issues, report orphans. Explicit, dry by default (§6.2) |
| Mirror | The one write-back to GitHub: the `[N]` estimate prefix in an issue title (§6.3) |
| Freeze | Compute and write baselines for one milestone. Explicit, dry by default (§6.4) |

<a id="ownership"></a>
## 3. Ownership

GitHub and the tracker never hold the same field, so there is no bidirectional sync and nothing to
reconcile field by field ([ADR 0003](adr/0003-disjoint-field-ownership.md)).

| Field | Authority | In an item file | In the index |
|---|---|---|---|
| title · body · state · labels · assignee · comments · parent and sub-issue links · blocked-by · `closedAt` | GitHub | no | yes, as a cache |
| estimate · priority · status · ordinal · lane · baseline · milestone | the tracker | yes | yes, as a cache |
| `actual_time` | the tracker, snapshotted from the time source | yes | yes, as a cache |
| the `[N]` title prefix | GitHub, written by the tracker | no | — |

<a id="github-owned"></a>
### 3.1 GitHub-owned

Identity (issue number and `node_id`), title, body, open/closed state, labels, assignee, comments,
parent and sub-issue links, dependencies (blocked-by and blocking), `closedAt`, repository, and the
commit and PR graph.

These are read through `gh` and cached in the index. No item file holds a copy. The tool is
read-only for dependencies: people edit them in GitHub or with `gh issue edit --add-blocked-by` and
`--remove-blocked-by`, and the next pull reads them.

<a id="tracker-owned"></a>
### 3.2 Tracker-owned

Estimate, priority, status, ordinal, lane, baseline, milestone and `actual_time`. These live in item
files and are never pushed to GitHub. `status` is stored because GitHub has only open/closed.

`actual_time` is the snapshot of tracked time. Only reconcile and `plan time` write it, from the
configured time source, and nobody types it ([ADR 0006](adr/0006-tracked-time.md),
[design 0002, *Data model*](design/0002-tracked-time.md#data-model)).

The tracker also computes values it never stores: duration from estimate and velocity
(`points_per_week`), estimated hours (`hours_per_point`), derived actuals, the ready queue, and
every view. Milestone membership can span repos.

<a id="write-back"></a>
### 3.3 The one write-back

When an estimate changes, mirror rewrites the `[N]` prefix in the issue title
([`B2`](requirements.md)). It is one field in one direction. Each further write-back would be a new
reconciliation problem, so there are none.

<a id="storage"></a>
## 4. Storage

Committed item files are the source of truth and SQLite is a disposable index
([ADR 0001](adr/0001-git-is-the-database.md)). `.tracker/` lives in the repo being planned
([ADR 0002](adr/0002-tracker-per-repo.md)) and is found by walking up from the working directory
([design 0001, *Discovery*](design/0001-phase-1.md#discovery)).

```
repo/.tracker/
  items/web-app/23.json  ← one file per issue, under its repo's short name. The source of truth. Committed
  milestones/beta.json   ← one file per milestone, which may span repos
  config.json            ← points_per_week, hours_per_point, repos, lanes, time_source
  focus.json             ← the one fast-tracked feature, present only while a focus is set
  .cache/index.db        ← SQLite. Derived, gitignored, deletable, rebuilt in seconds
  .cache/gh/web-app.json ← the last pull of one repo, exactly as gh returned it. Derived, gitignored
  out/                   ← generated HTML. Gitignored
  .gitignore             ← ignores .cache/ and out/. Written by plan init. Committed, so every tracker carries the rule
```

Nothing authoritative lives in the database. SQLite lets commands and the web UI sort, filter and
join without re-parsing every item file. Drop it at any time and `plan reindex` rebuilds it from
the committed files and the cached pull, without the network. If the cached pull is gone too, the next pull restores it.

One file per item and one per milestone means concurrent edits to different items merge cleanly,
and `git log -p` on one file is that item's history. The committed files are formatted JSON, one
key per line, in one canonical form that every tool write produces
([ADR 0007](adr/0007-tracker-files-are-yaml.md)). The schemas are in
[design 0001, *Data model*](design/0001-phase-1.md#data-model) and
[design 0002, *Data model*](design/0002-tracked-time.md#data-model).

<a id="components"></a>
## 5. Components

<a id="front-ends"></a>
### 5.1 Core and front ends

One core library has two front ends: the CLI and a web UI. Neither shells out to the other. The web
UI is a server bound to localhost that renders the same templates as `plan render`
([ADR 0005](adr/0005-generated-html-charts.md)); its stack is not chosen.

Reads are implicit and writes are deliberate: pull runs automatically, while reconcile, freeze,
mirror and push-drafts are dry by default
([design 0001, *Reads and writes*](design/0001-phase-1.md#reads-and-writes),
[*Commands*](design/0001-phase-1.md#commands)).

<a id="process-boundary"></a>
### 5.2 Process boundary

`gh.py`, `git.py` and the adapters in `timekeeping/` are the only modules that spawn a process or
open a network connection. Everything else is pure and testable without a network or a repo
([ADR 0004](adr/0004-python-no-docker.md), [ADR 0006](adr/0006-tracked-time.md),
[design 0001, *Layout*](design/0001-phase-1.md#layout)).

- `gh.py` makes every call to GitHub, through the `gh` CLI. `gh` is already authenticated, so the
  tool holds no token, as [`G3`](requirements.md) requires. A library such as PyGithub, Octokit or
  httpx would need a token, and a GitHub App would need a key and an install. The tool polls GitHub
  on demand, because webhooks would need a public endpoint.
- `git.py` makes every call to git.
- Each `timekeeping/` adapter reads one vendor's time tracker behind the `TimeSource` interface.
  It reads and never writes
  ([design 0002, *The TimeSource interface*](design/0002-tracked-time.md#interface)).

<a id="platform"></a>
### 5.3 Platform

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.14+ (the floor is the one version CI tests) | [ADR 0004](adr/0004-python-no-docker.md) |
| GitHub access | subprocess to `gh` | requirement [`G3`](requirements.md) |
| Time tracker access | one adapter per vendor behind `TimeSource` | [ADR 0006](adr/0006-tracked-time.md) |
| Tracker files | formatted JSON via stdlib `json` | [ADR 0007](adr/0007-tracker-files-are-yaml.md) |
| Index | SQLite via stdlib `sqlite3` | [ADR 0001](adr/0001-git-is-the-database.md) |
| Validation | Pydantic v2 | [ADR 0004](adr/0004-python-no-docker.md) |
| CLI | Typer | [ADR 0004](adr/0004-python-no-docker.md) |
| Charts | generated HTML: CSS Grid for bars and lanes, inline SVG for dependency arrows | [ADR 0005](adr/0005-generated-html-charts.md) |
| Web UI | a localhost server rendering the chart templates; stack not chosen | [ADR 0005](adr/0005-generated-html-charts.md) |
| Packaging | `uv run`, no Docker on the run path; an optional `Dockerfile` for CI | [ADR 0004](adr/0004-python-no-docker.md) |

<a id="operations"></a>
## 6. Operations

```
          ┌──────────────── GitHub (authoritative for identity) ───────────────┐
          │  #23  title · state · labels · closedAt · sub-issues · blocked-by │
          └───────────────────────────┬───────────────────────────────────────┘
                         (1) PULL     │ read-only, `gh`, no token
                                      ▼
   items/web-app/23.json ───────▶ .cache/index.db ◀─── (3) MIRROR, one field only
   estimate · lane · status        a JOIN of both,        `[N]` → issue title
   baseline · priority             nothing authoritative
   ▲                                      │
   │ (2) RECONCILE: file⇄issue membership │
   └──────────────────────────────────────┘
```

Freeze (§6.4) writes baselines into item files. The time source feeds reconcile's snapshot (§6.2).

<a id="pull"></a>
### 6.1 Pull

Pull is read-only, idempotent and needs no credential. Per repo it runs
`gh issue list --repo <r> --state all --json number,id,title,state,stateReason,closedAt,labels,blockedBy,parent,subIssuesSummary`,
which also returns the blocked-by edges and the sub-issue links. It saves the output to `.tracker/.cache/gh/<r>.json`, replacing the previous file only once the new one is complete, then rebuilds the index from it. It never writes to item files. The file's modification time records when that repo was pulled. Commands warn when the
cache is stale, and `--offline` works entirely from it, since every tracker-owned field is local.

<a id="reconcile"></a>
### 6.2 Reconcile

Reconcile is the only operation that creates item files or changes them to match GitHub. It is dry
by default and writes with `--apply`. Where a case needs a judgement, it reports instead of
guessing:

- an open issue with no item file: create one ([`H5`](requirements.md), automatic membership)
- a closed issue whose item is not `Done`: set `status: Done`, and in the same write record the
  `actual_time` snapshot when a time source is configured
- a reopened issue whose item is still `Done`: report it, because the earlier status is not
  recorded
- an item file whose `node_id` resolves to nothing: report it as an orphan

A time source that fails does not block reconcile. The item still reaches `Done`, without a
snapshot, and `validate` warns ([design 0002, *Lifecycle*](design/0002-tracked-time.md#lifecycle)).

<a id="mirror"></a>
### 6.3 Mirror

Mirror is the single write-back (§3.3). When `estimate` changes, it rewrites the title's `[N]`
prefix. If someone edits the title on GitHub and drops the prefix, mirror detects the drift and
re-applies it. It is dry by default.

<a id="freeze"></a>
### 6.4 Freeze

Freeze computes start and finish dates for one milestone and writes them into its items as
baselines. It is dry by default. A baseline is written once and never silently recomputed;
`--rebaseline` replaces it deliberately, with a reason, and git records the change
([`C3`, `C4`](requirements.md)). `plan validate` runs before freeze, and an unestimated item fails
it, because it would corrupt the baseline.

<a id="identity"></a>
## 7. Identity

`gh issue transfer` changes an issue's number and can change its repo, so `node_id` is the key and
`issue:` is a cache. The file path, `items/<repo>/<n>.json`, follows the cache so a person can find
the file. Two repos can both have a #23, so the repo is part of the path. Reconcile repairs a stale
`issue:` and `repo:` from `node_id` and renames the file to match, and git records the rename
([design 0001, *Identity*](design/0001-phase-1.md#identity)).

Commands name an item by issue number when only one configured repo has that number, and as
`<repo>#<n>` otherwise.

A draft carries `draft: true` explicitly rather than being inferred from a null `issue:`. Reconcile
must tell a draft, which is expected to have no issue yet, from an orphan, which unexpectedly has
none. Without the flag the two look identical.

<a id="creation-paths"></a>
## 8. Creation paths

Issues arrive two ways, and only one involves the tracker. Both end in the same state.

<a id="cold-created"></a>
### 8.1 Created on GitHub

An issue created in GitHub's web UI, on a phone, by a bot, or by someone who has never heard of the
tracker gets its number and `node_id` from GitHub. No item file exists yet, and nothing is lost:

1. Pull brings it into the index like any other issue.
2. Reconcile sees an issue with no item file and writes `.tracker/items/web-app/24.json` with identity and defaults only:
   `issue`, `node_id` and `repo`, then `"draft": false`, `"priority": "P2"` and
   `"status": "Icebox"`. It never guesses an estimate, lane or milestone.
3. With no milestone, [`F1`](requirements.md) makes it `Icebox`. An untriaged issue is deferred
   until someone triages it.
4. `plan validate` reports it as `needs-triage`, a warning with a count. It becomes a failure only
   when its milestone is being frozen.
5. It has no `[N]` title prefix, because mirror only runs once an estimate exists.

If the issue has a GitHub milestone or labels, reconcile offers them as suggestions in the triage
report. It does not import them, because GitHub's milestones are not the tracker's
([`A2`](requirements.md)).

<a id="local-create"></a>
### 8.2 Created by the CLI or an agent

The tracker cannot allocate an issue number; GitHub assigns it. By default `plan new` works
online: it creates the GitHub issue, then writes the item file, then commits. Offline,
`plan new --draft` writes a draft file with no issue, and `plan push-drafts` later creates the
issue and renames the file, so git history keeps the draft's provenance. The command sequences are
in [design 0001, *Commands*](design/0001-phase-1.md#commands).

<a id="ordering-rule"></a>
### 8.3 GitHub first, then the file

`plan new` calls `gh` first and writes the file second. A crash between the two can land two ways:

| Crash leaves | Who notices | Cost |
|---|---|---|
| An issue with no file | Reconcile, automatically | Repairs itself: it is the path in §8.1 |
| A file with no issue | A human reading an orphan report | Needs a decision: create the issue, or delete the file |

Writing GitHub first means a crash falls back into the §8.1 path, which has to work anyway. Writing
the file first would create orphans that need a human. The tool always takes the failure mode that
repairs itself.

<a id="sub-issues"></a>
## 9. Sub-issues

GitHub owns the parent and child relationship; the tracker owns each child's planning. Checked
against [`A4`, `A5`, `A6`](requirements.md), GitHub behaviour as of 2026-10-10:

| Need | Met? | By what |
|---|---|---|
| `A4` sub-tasks are first-class and schedulable | ✅ | A sub-issue is an issue, so it gets its own number, its own item file, and its own estimate, lane, baseline and dependencies |
| `A4` appear in every view | ✅ | Reconcile creates a child's item like any other issue's ([`H5`](requirements.md)) |
| `A5` parent roll-up without double-count | ✅ | `subIssuesSummary{total completed percentCompleted}` from GitHub, plus the rule that a parent with children carries no estimate. The sum is computed in the index |
| `A6` nesting deeper than two levels | ✅ | 8 levels |
| Per-parent capacity | ✅ | 100 children, far more than splitting an item produces |
| Cross-repo parent and child | ✅ | Documented, and `gh` accepts a URL as well as a number for `--parent` and `--add-sub-issue`. Docs-verified, not hands-tested 🔍 |

The tracker has no parent field. Parentage is GitHub-owned: read through `Issue.parent`, cached in
the index, never written to an item file. The one tracker-side rule is the one `A5` needs, that a
parent with children has no estimate, and `validate` enforces it.

Cross-repo support means a split parent's children can live in other repos without parentage
moving into item files.

`gh` wraps sub-issue writes fully on 2.102.0, so they need no raw GraphQL:
`gh issue create --parent` and `gh issue edit --add-sub-issue|--parent|--remove-parent`. Reads come
from one query over `Issue.parent` / `subIssues` / `subIssuesSummary`.

<a id="failure-modes"></a>
## 10. Failure modes

| Event | Effect | Handling |
|---|---|---|
| Issue transferred to another repo | `issue:` goes stale, `node_id` still resolves | Reconcile rewrites `issue:` and `repo:` and renames the file. No data lost |
| Issue deleted | `node_id` resolves to nothing | Orphan report; file kept until a human decides |
| Issue reopened | `closedAt` clears | Derived `actual_finish` is computed, never stored in an item file, so it changes with it. Reconcile reports the item if it is still `Done`. The `actual_time` snapshot stays until the next close replaces it |
| Crash between `gh issue create` and the file write | An issue with no item file | Reconcile creates the file (§8.3) |
| Title edited on GitHub | `[N]` prefix may be dropped | Mirror detects the drift and re-applies it |
| Estimate edited in the file | GitHub title is stale | Mirror re-applies |
| Time source unreachable at close | No snapshot | Item still reaches `Done`; `validate` warns until `plan time N --apply` |
| Offline | Pull fails | Everything tracker-owned still works; the index serves stale reads with a warning |
| Two sessions edit different items | Two different files | Git merges cleanly, because there is one file per item |
| Two sessions edit the same item | Ordinary git conflict | A short JSON conflict a human can read, because each key is on its own line |

<a id="views"></a>
## 11. Views

The terminal views are `plan next`, `ready`, `why` and `board`, each with `--json`
([design 0001, *next, ready, why*](design/0001-phase-1.md#next-ready-why)).

Every chart, graph and table is also generated HTML, with no Mermaid, no JS charting
library and no build step ([ADR 0005](adr/0005-generated-html-charts.md)):

| Artifact | Technique |
|---|---|
| Lane board | CSS Grid: lanes are rows, statuses are columns |
| Timeline bars | CSS Grid: a bar is a column span; duration is `grid-column: start / span n` |
| Dependency arrows | Inline SVG over the grid |
| Tables, roll-ups, ready queue | plain `<table>`, server-rendered |
| Colour and status | CSS custom properties, with a shape or label as well as colour so nothing depends on hue alone |

`plan render` writes the HTML to `.tracker/out/`, which is gitignored, because GitHub shows a
committed HTML file as source. `plan serve` renders the same templates from a localhost server.

<a id="invariants"></a>
## 12. Invariants

1. Git is the database; SQLite is a disposable index rebuilt by `plan reindex`
   ([ADR 0001](adr/0001-git-is-the-database.md)).
2. Field ownership is disjoint, and the only write-back is the `[N]` title prefix (§3,
   [ADR 0003](adr/0003-disjoint-field-ownership.md)).
3. `gh.py`, `git.py` and the `timekeeping/` adapters are the only modules that spawn a process or
   open a network connection (§5.2).
4. GitHub first, then the file (§8.3).
5. Estimates are `Literal[1, 2, 3, 5]`. 8 and 13 are refusal codes meaning "split this" and cannot
   be represented ([`B3`](requirements.md)).
6. GitHub mutations are paced by `write_pause_seconds` (default 1), because the secondary rate
   limit counts them: 80 content-generating requests a minute and 500 an hour.
7. An item has at most one lane ([`D4`](requirements.md)).
8. A parent with children has no estimate ([`A5`](requirements.md)).
9. A baseline is written only by freeze and never silently recomputed ([`C3`](requirements.md)).
10. Dependencies and tracked time are read, never written: the first in GitHub, the second in the
    time tracker.

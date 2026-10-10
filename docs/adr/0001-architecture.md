# ADR 0002 — Architecture for a bespoke GitHub-integrated tracker

**Status:** proposed 2026-10-10 · **Inputs:** [`02-tracking-requirements.md`](../research/02-tracking-requirements.md) ·
[`03-tracking-options-matrix.md`](../research/03-tracking-options-matrix.md)

## Definitions

**The tool is `gh-lanes` (product: GH Lanes, CLI: `lanes`), in its own repo. Its *data* lives in
`ms-security-docs/.tracker/`. See [design 0001](../design/0001-tracker-phase-1.md).**

| Term | Definition |
|---|---|
| **Tracker** | A local CLI plus optional localhost web UI that owns the *planning* layer over GitHub Issues. Not an issue tracker |
| **Item** | One YAML file, `.tracker/items/<n>.yml`, holding the planning fields for one GitHub issue. Committed. The source of truth |
| **Index** | `.tracker/.cache/index.db` — SQLite. A join of GitHub facts and item files. Derived, gitignored, rebuildable |
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

## The premise, which is narrower than "build a tracker"

Six surveys and two hands-on tests produced one consistent result: **GitHub Issues is fine.
Projects v2 is what failed.** Issues gave us identity, bodies, state, labels, milestones,
sub-issues, an authenticated CLI and zero credentials. Every ❌ in the matrix came from the
*planning* layer — fields living on the project item instead of the issue, no dependency
relationship, no readable rank, display-only fields, a board that cannot group by labels, and a
secondary rate limit that trips at twenty mutations.

So this is not a tracker. **It is a replacement for Projects v2** that keeps Issues underneath.
That single reframing removes roughly half the work: no issue CRUD, no comments, no notifications,
no auth, no multi-user, no permissions, no email.

### What GitHub keeps owning

Identity (`#23`), title, body, open/closed, labels, assignee, comments, sub-issue links,
repository, and the commit and PR graph.

### What we own

Estimate · priority · **status** (GitHub has only open/closed) · **ordinal** · lane · dependencies ·
baseline start and finish · velocity · milestone membership *across repos* · derived actuals · the
ready-queue computation · every view.

## Core decision: git is the database, SQLite is a disposable index

The binding requirements are **G1** (tracking data is reviewable evidence — diffable, readable with
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
  Who changed it and when, signed, with the commit that explains why. **Better than any surveyed
  tool**, and it is the requirement that matters most given where Act 6 goes.
- **G4 ✅** — no database to back up, patch or validate. A corrupted index is a `rm` away.
- **H2 ✅** — bulk writes are file writes. Twenty-four lane assignments is one commit.
- **C3/C4 ✅** — a frozen baseline is a value in a committed file. Re-baselining shows up as a diff
  with a commit message. The requirement that **no free tool on earth satisfied** is nearly free
  here.
- **B3 ✅** — validation runs at write time, in our own code. **Server-side enforcement of the
  >5-must-split rule, which no surveyed tool offers.**

🏛 The deeper reason: this project's subject matter is audit trails and evidence. A tracker whose
history is git history is the same argument applied to our own tooling — derived facts over typed
assertions, and a record that an auditor could follow.

## Platform recommendation: Python · FastAPI · HTMX · SQLite · shell out to `gh`

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Language | **Python 3.14+** (🔧 raised from 3.12 on 2026-10-10: CI tests one version, 3.14, so the floor is what is tested) | Already this project's tooling language — the attribution hook, the `wp-publish` skill and the gantt generator are all Python. `uv 0.11.7` is installed. Adding a second toolchain to a docs repo costs more than it returns |
| GitHub access | **subprocess to `gh`** | **The decisive choice.** `gh` is already authenticated, so **G3 is satisfied natively with no PAT anywhere.** PyGithub or httpx would each need a token — the exact cost that killed the auto-add Action |
| Web | **FastAPI + Jinja2 + HTMX** | No build step, no npm, no bundler, server-rendered HTML. HTMX gives drag-and-drop and partial updates with attributes rather than a front-end app. For a single-user local tool, a React SPA is the wrong complexity |
| Index | **SQLite via stdlib `sqlite3`** | No server, no driver, no ORM needed. It is a cache, so schema migrations are irrelevant — delete and reindex |
| Validation | **Pydantic v2** | Schema for the YAML files, which is how `B3` becomes server-side instead of a lint |
| CLI | **Typer** | One core library behind both front ends — see *CLI surface*. CI and hooks call the CLI |
| Charts | **Generated HTML** — CSS Grid for bars and lanes, inline SVG for dependency arrows | No Mermaid, no JS charting library, no build step. See *Rendering* |
| Packaging | **`uv run`**, no Docker | See below |

### Not Docker, and here is the argument

The app's entire job is to read and write a **git working tree** and to call `gh` with **the host's
credentials**. Containerising means bind-mounting the repo, bind-mounting `~/.config/gh`, and
reconciling uid/gid — more moving parts than `uv run lanes serve`, for a single-user tool bound
to localhost. Docker's wins (isolation, reproducible deps, multi-service) do not apply: there is one
service, `uv.lock` already pins deps, and isolation from the repo is the opposite of what we want.

**Where Docker earns its place:** a `Dockerfile` for *CI* so the validation CLI runs hermetically,
and as a reproducibility escape hatch if the thing is still wanted in three years. Ship it as
optional, not as the run path.

## CLI surface

One core library; the CLI and the web UI are two front ends over it. Neither shells out to the
other.

### The rule: reads are implicit, writes are deliberate

**`pull` is automatic. `reconcile` is not.** The split is not arbitrary — it follows from whether an
operation can make a wrong decision:

- **Pull is read-only, idempotent and decision-free.** Requiring a human to remember it only
  produces stale data, so it runs automatically whenever the index is older than
  `config.stale_after_minutes` (default 15 min). `lanes pull` exists for scripting and debugging.
- **Reconcile creates files and reports orphans.** It has consequences and sometimes needs a
  judgement, so it is explicit and **dry by default**.

That is the same principle the current gantt tooling already uses: `extract.py` reads freely and
`freeze.py` is the lone writer, kept separate so a read path can never mutate a record.

### Commands

**Query — always safe, auto-refresh the index**

| Command | Does |
|---|---|
| `lanes status` | Counts, `needs-triage` list, index age |
| `lanes list [--lane a-enforcement] [--milestone act-0] [--ready]` | Filtered items |
| `lanes show 23` | One item: GitHub facts joined with ours |
| `lanes next [--lane L]` | **One answer: the single task to start now.** The acceptance criterion for Phase 1 |
| `lanes ready` | One per lane — the parallel view, for concurrent sessions |
| `lanes why 23` | Why this item is not startable: blocked by, behind a lane head, iced, or unestimated |
| `lanes board` | Terminal lane board, ASCII columns |
| `lanes validate` | The lint. Non-zero exit. Runs in the pre-commit hook and before `freeze` |

**Write what the user named — immediate**

| Command | Does |
|---|---|
| `lanes new "title" [--estimate N] [--lane L] [--milestone M] [--draft]` | `gh issue create`, then the file |
| `lanes set 23 --estimate 3 --lane a-enforcement --priority P0 --depends-on 1,21` | Validates, then writes. Rejects 8/13, self-refs and cycles **at write time** |
| `lanes ice 23` / `lanes schedule 23 --milestone act-0` | Clear or set the milestone |

**Write what the tool decided — dry by default, `--apply` to commit**

| Command | Does |
|---|---|
| `lanes reconcile [--apply]` | Creates files for untracked issues; reports orphans and drafts |
| `lanes freeze act-0 [--apply] [--rebaseline]` | Computes and freezes baselines |
| `lanes mirror [--apply]` | The one write-back: `[N]` into issue titles |
| `lanes push-drafts [--apply]` | Turns drafts into real issues, renames files |

**Maintenance**

| Command | Does |
|---|---|
| `lanes pull [--repo R] [--fresh]` | Explicit index refresh |
| `lanes reindex` | Rebuild SQLite from the committed files. Always safe — the index is derived |
| `lanes serve [--port 7420]` | The local web UI, bound to localhost |
| `lanes render` | Mermaid lane chart and Gantt into `docs/` |

**Global flags:** `--offline` (never call `gh`; serve stale index with a warning), `--json` (machine
output on every query command), `--repo` (scope to one of the four).

🏛 **Why `new` and `set` are immediate while `freeze` and `reconcile` are not:** the first pair write
a value the user just typed, so a confirmation prompt would only add a keystroke to a decision
already made. The second pair write values *the tool derived* across many items, where a dry run is
the only chance to catch a wrong inference before it is committed. The dividing line is **who chose
the value**, not how many rows change.

### `lanes next` — the Phase 1 acceptance criterion

Phase 1 ships no HTML and no server, so the terminal has to answer *what do I do now* well enough to
work from. That is one command with one answer:

```
$ lanes next
#1  [3] Attribution hook has five bypasses          lane A enforcement   P2
    ready · 5d at 5 pts/week · unblocks #20

$ lanes next --lane e-writing
#19 [5] Post: multi-repo harness configuration      lane E writing       P2
    ready · 7d · head of lane (3 behind it)
```

Selection order, which is the whole algorithm:

1. drop anything `Done`, `Icebox`, or `needs-triage`
2. drop anything with an unmet `depends_on`
3. drop anything that is not its lane's head
4. sort by `priority`, then `ordinal`, then issue number
5. print the first

`lanes ready` prints step 3's survivors — one per lane — which is the concurrency answer:

```
$ lanes ready
LANE               TAKE  EST  BLOCKED BY
a-enforcement      #1    3    —
b-wp-publish       #7    2    —
c-workspace-docs   #4    1    —
d-agents           #9    3    —
e-writing          #19   5    —
f-mcp-config       #17   2    —
g-standalone       #23   2    —
z-sweep            #6    3    #1 #2 #3 #14 #16 #17
```

`lanes why` explains a negative, which is the part a chart conveys badly anyway:

```
$ lanes why 20
#20 not startable
  · depends on #1 (open), #21 (open)
  · behind lane head #19 in lane E writing
```

All three take `--json`, so an agent can consume them without parsing columns.

🔑 **If `lanes next` is not useful enough to work from, Phase 1 has failed** and the HTML views are
not optional after all. That is the explicit test, decided before building rather than after.

## Data model

```yaml
# .tracker/items/23.yml
issue: 23                # human join key — CHANGES on repo transfer
node_id: I_kwDOA1b2c3    # GitHub global id — SURVIVES transfer. The real key
# draft: true            # set only before the GitHub issue exists (offline create)
repo: contoso-health-partners
estimate: 2              # 1 2 3 5 only — 8/13 rejected at write time
priority: P0
status: Todo             # tracker-owned; Done/Icebox cross-checked by validate
ordinal: 100             # sparse rank — tiebreak within a priority band
lane: a-enforcement      # single-valued by schema
depends_on: [1, 21]      # validated: exists, not self, no cycle
milestone: act-0         # our milestone, which may span repos
baseline:
  start: 2026-10-13      # written once by `lanes freeze act-0`
  finish: 2026-10-15
  frozen_at: 2026-10-10T16:00:00Z
  reason: "Act 0 checkpoint"
```

Deliberately absent: title, body, status, labels, assignee. Those are GitHub's, read through `gh`
and cached in the index. **Not duplicated in a file we would then have to reconcile.**

## The GitHub boundary — how sync actually works

**There is no bidirectional sync, because the two systems never hold the same field.** That is the
whole design, and it is why "git is the database" does not collapse into a reconciliation problem.

### Field ownership is disjoint

| Field | Authority | Stored in YAML? | Stored in index? |
|---|---|---|---|
| title · body · state · labels · assignee · comments · sub-issue links · `closedAt` | **GitHub** | **No** | yes, as a cache |
| estimate · priority · **status** · **ordinal** · lane · `depends_on` · baseline · our milestone | **Files** | yes | yes, as a cache |
| the `[N]` title prefix | GitHub, written by us | no | — |

**The second column is the trick.** GitHub-owned fields are *never copied into a tracker file*. No
copy means no divergence means nothing to reconcile. Tracker-owned fields are never pushed to
GitHub, so GitHub cannot contradict them either. The two sets are disjoint, and the only overlap is
one mirrored field in one direction.

### Three operations, not one "sync"

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

**1. Pull — read-only, idempotent, no credential.**
`gh issue list --repo <r> --state all --json number,id,title,state,labels,closedAt` per repo, plus
one `gh api graphql` for sub-issue links. Writes only to the index, never to YAML. Records
`fetched_at`; commands warn when the cache is stale and `--offline` works entirely from it, since
every tracker-owned field is local.

**2. Reconcile — the only operation that creates or flags files.** This is today's lint, promoted
to a first-class step. It answers two questions and *reports* rather than guessing:

- an open issue with no item file → offer to create one (that is `H5`, automatic membership)
- an item file whose `node_id` resolves to nothing → orphan, report it

**3. Mirror — the single write-back.** When `estimate` changes, rewrite the title's `[N]` prefix.
One field, one direction, with drift detection already specified. **Every additional write-back
would be a new reconciliation problem, so there are none.**

### Creation paths — and the ordering rule they imply

Issues arrive two ways and only one of them involves the tracker. Both must end in the same state.

#### A. Cold-created on GitHub — web UI, phone, a bot, a naive user

GitHub assigns the number and `node_id`. No item file exists, and **nothing is lost**:

1. **Pull** brings it into the index like any other issue — title, state, labels all present.
2. **Reconcile** sees an issue with no item file and writes
   `.tracker/items/24.yml` containing **identity only** — `issue`, `node_id`, `repo`. No estimate,
   no lane, no milestone. **It never guesses a planning value.**
3. Because it has no milestone, **`F1` makes it `Icebox` by definition** — and that is exactly
   right. An untriaged issue *is* deferred until a human triages it. The icebox is not a
   dumping-ground, it is where unplanned work correctly lands.
4. `lanes validate` reports it as **`needs-triage`**: has identity, missing estimate or lane.
   A **warning with a count**, not a failure — a naive user filing an issue has done nothing wrong.
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

**Default — online, GitHub first:**

```
lanes new "Attribution hook has five bypasses" --estimate 3 --lane a-enforcement --milestone act-0
  1. gh issue create --repo … --title "[3] …"     → returns #24 and node_id
  2. write .tracker/items/24.yml with identity + planning fields
  3. one commit
```

**Offline — `--draft`:**

```
lanes new "…" --draft    → .tracker/items/draft-01JA7Z…yml
                             issue: null   node_id: null   draft: true
lanes push-drafts        → creates the GitHub issues, renames the files to items/25.yml
```

The rename is visible in git history, so a draft's provenance survives. `draft: true` is explicit
rather than inferred from a null `issue:`, because reconcile must distinguish **a draft (expected to
have no issue yet)** from **an orphan (unexpectedly has none)**. Those look identical without the
flag and mean opposite things.

#### 🏛 The ordering rule: GitHub first, then the file

Step 1 calls `gh`, step 2 writes the file, and that order is deliberate. Compare the two ways a
crash between them can land:

| Crash leaves | Who notices | Cost |
|---|---|---|
| **An issue with no file** | Reconcile, automatically | **Self-healing** — it is exactly scenario A, which already works |
| A file with no issue | A human reading an orphan report | Needs a decision: create the issue, or delete the file? |

**Choose the failure mode that repairs itself.** Writing the file first would create orphans
requiring judgement; writing GitHub first degrades gracefully into the cold-create path we have to
support anyway. The naive-user path is therefore not an edge case to tolerate — **it is the
recovery mechanism for the CLI path**, which is why it is worth making robust first.

A corollary for sequencing: **build reconcile before build create.** Reconcile alone makes the whole
system tolerant of every creation route, including ones we have not thought of.

### Sub-issues — GitHub owns the relationship, we own the planning

Checked against `A4`, `A5`, `A6` on 2026-10-10.

| Need | Met? | By what |
|---|---|---|
| `A4` sub-tasks are **first-class and schedulable** | ✅ | A sub-issue **is** an issue, so it gets its own number, its own item file, and therefore its own estimate, lane, baseline and dependencies |
| `A4` appear in every view | ✅ | **`Auto-add sub-issues to project` is already enabled**, so children join without ceremony |
| `A5` parent roll-up without double-count | ✅ | `subIssuesSummary{total completed percentCompleted}` from GitHub, plus our rule that a parent with children carries no estimate. Sum is computed in the index |
| `A6` arbitrary depth | ✅ | **8 levels**, against the two we use |
| Per-parent capacity | ✅ | **100 children.** A 13-point item splitting into more than 100 is not a splitting problem |
| **Cross-repo parent/child** | ✅ | Documented, and `gh` accepts a **URL** as well as a number for `--parent` and `--add-sub-issue`. ⚠️ Docs-verified, **not hands-tested** — only one repo exists today. Confirm during Act 1 |

**So no tracker-side parent field.** Parentage joins the GitHub-owned column alongside title, state
and labels: read via `Issue.parent`, cached in the index, never written to an item file. The only
tracker-side rule is the one `A5` needs — *a parent with children must have an empty estimate* —
which `validate` enforces.

The cross-repo answer is the one that mattered. Had sub-issues been same-repo only, the Act 1
migration would have broken every split parent whose children moved to an app repo, and parentage
would have had to live in our files after all.

### The join key, and why `issue:` alone is wrong

🔧 **Corrected by this question.** An issue *number* is not stable — `gh issue transfer` changes it,
and the Act 1 migration moves app issues into three new repos, so this is scheduled, not
hypothetical. The schema therefore carries **`node_id`** (GitHub's global id, stable across
transfer) as the real key, with `issue:` kept as the human-readable one and treated as a cache.
Reconcile repairs a stale `issue:` from `node_id` rather than reporting a false orphan.

### Failure cases, and what happens

| Event | Effect | Handling |
|---|---|---|
| Issue transferred to another repo | `issue:` goes stale, `node_id` still resolves | Reconcile rewrites `issue:` and `repo:`. **No data lost** |
| Issue deleted | `node_id` resolves to nothing | Orphan report; file kept until a human decides |
| Issue reopened | `closedAt` clears | Derived `actual_finish` is **computed, never cached in YAML**, so it just changes |
| Title edited on GitHub | `[N]` prefix may be dropped | Mirror drift detected, re-applied on next run |
| Estimate edited in the file | GitHub title now stale | Mirror re-applies |
| Offline | Pull fails | Everything tracker-owned still works; index serves stale reads with a warning |
| Two sessions edit **different** items | Two different files | **Git merges cleanly.** This is why it is one file per item, not one big YAML |
| Two sessions edit the **same** item | Normal git conflict | A ten-line YAML conflict a human can read — unlike a database merge |

### What this costs in estimate terms

The 13-point sync engine in the plan below is **mostly reconcile and transfer handling**, not field
synchronisation — because field synchronisation does not exist. If two-way field sync were in scope
the number would be much larger and the risk open-ended, which is exactly why it is not.

## Rendering — generated HTML, not Mermaid

**Decided 2026-10-10: Mermaid is out.** All charts, graphs and tables are generated HTML.

| Artifact | Technique |
|---|---|
| Lane board | **CSS Grid** — lanes are rows, statuses are columns |
| Gantt / timeline bars | **CSS Grid** — a bar is a column span; duration is `grid-column: start / span n` |
| **Dependency arrows** | **Inline SVG** overlaid on the grid |
| Tables, roll-ups, ready queue | plain `<table>`, server-rendered |
| Colour / status | CSS custom properties, with shape or label as well as colour so nothing depends on hue alone |

No JS charting library and no build step: Jinja templates emit HTML, CSS does the layout. Interaction
in Phase 3 is HTMX attributes.

### What this gains

**Dependency arrows become possible.** The reason the Gantt was shelved was that Mermaid `gantt`
sequences with `after` but **draws no arrows and has no critical path** — so `Depends On` affected
bar position only and the reader could not see *why*. Inline SVG over a CSS grid draws the edges.
The chart that was abandoned as not-worth-it becomes the chart that shows the real structure.

Also: no 44-character label truncation, real tooltips, and a lane board and a timeline that are the
same template with different column semantics.

### What this costs

⚠️ **GitHub will no longer render the charts.** Mermaid in a committed `.md` renders natively in the
GitHub UI, so anyone with the link saw the chart with no tooling. An HTML file in a repo displays as
**source**. So:

- The charts become **build artifacts, not committed evidence** — generated into `.tracker/out/` and
  **gitignored**, not committed like `docs/gantt/*.md` were.
- **`G1` is unaffected**, because `G1` is about the tracking *data* — the item YAML — which is still
  committed and diffable. It is the *rendering* that stops being viewable without running something.
- If a chart is ever needed in a blog post or for someone with no checkout, it is a screenshot or a
  published page, not a repo file.

That is a real loss and worth stating plainly; the gain is a chart that shows dependencies at all.

### Consequence for phasing

HTML rendering sits in **Phase 2**, not Phase 1. Phase 1 answers *what next* in the terminal
instead; see `lanes next`. The templates and the server land together in Phase 2, since serving an
existing template is nearly free once it exists.

## Requirements coverage and estimates

Fibonacci, `>5 must split` applies to this plan too.

| # | Requirement | How | sp |
|---|---|---|---|
| **A1** | One tracker, 4 repos | `repo:` per item; `gh` queries each | 2 |
| **A2** | Milestones span repos | **Our** milestone entity — GitHub's is unused | 2 |
| **A3** | Milestone exit criterion | `exit_criterion:` field, rendered on the board | 1 |
| **A4** | Sub-tasks schedulable | Read GitHub sub-issues; children get their own files | 3 |
| **A5** | Parent roll-up, no double-count | Parent estimate must be empty; computed sum | 2 |
| **B1** | Fibonacci estimate | field + enum | 1 |
| **B2** | Visible in lists | our UI; mirror to title `[3]` | 2 |
| **B3** | >5 split enforced | **write-time rejection** | 2 |
| **C1** | Velocity per week | `config.pointsPerWeek` | 1 |
| **C2** | Duration from estimate | existing formula | 1 |
| **C3** | Frozen baseline | committed values + `frozen_at` | 3 |
| **C4** | Re-baseline recorded | `reason:` + the git commit | 1 |
| **C5** | **Derived actuals** | **see hard items** | 8 → split |
| **D1 D4** | Lane, single-valued | field + enum | 1 |
| **D2** | Board groups by lane | **see hard items** | 8 → split |
| **D3** | Ready queue | `isReady` computed in the index | 3 |
| **E1** | Dependencies | `depends_on` list | 2 |
| **E2** | Cycle detection | DFS at write time, reject | 2 |
| **E3** | Priority outranks age | enum + sort | 1 |
| **F1** | Icebox | absent milestone ⟺ iced | 1 |
| **F2** | States orderable | `config.statuses` ordered | 1 |
| **F4** | Taxonomy | GitHub labels, unchanged | 0 |
| **G1 G2 G5** | Evidence, export, history | **free — it is committed YAML in git** | 0 |
| **G3** | No credential | **free — `gh` is already authenticated** | 0 |
| **G4** | Low ops | **free — no database to operate** | 0 |
| **H1** | CLI | Typer | 2 |
| **H2** | Bulk writes | **free — file writes** | 0 |
| **H3 H4** | Fields readable, on the item | **free — YAML** | 0 |
| **H5** | Automatic membership | reconcile creates missing files | 2 |
| **H6** | Validation hooks | pre-commit hook runs `lanes validate` | 2 |
| **C7** | Gantt + lane board | **HTML templates: CSS Grid + SVG arrows** | 8 → split |
| — | **GitHub sync engine** | **see hard items** | 13 → split |
| — | Index + reindex | SQLite schema, rebuild | 3 |
| — | Web shell, auth-free, localhost | FastAPI + Jinja + HTMX | 3 |

**Total ≈ 70 points before splitting the three hard items — about 14 weeks at 5/week.** Phase 1 alone is 32.

Note the shape: **eight requirements cost zero** because they fall out of the storage choice, and
they include the three that no surveyed tool satisfied (`G1`, `G5`, `H2`) plus the one that
disqualified several (`G3`).

## The hard MUSTs

### 🔴 GitHub sync engine — 13, must split

The only genuinely difficult piece. Reconciling two systems that both think they know an issue's
state. Split:

1. **Pull + index** (3) — `gh` → SQLite, read-only
2. **Orphan reconcile** (3) — file with no issue, issue with no file, draft vs orphan, report and offer to fix. **Build this first** — it makes every creation path tolerable
3. **Title mirror for `[N]`** (2) — the one write-back, with drift detection
4. **Transfer and deletion handling** (3) — what `issue: 23` means when 23 moves to another repo.
   Act 1 makes this real, not hypothetical
5. **Reopen handling** (2) — recompute derived actuals rather than caching them

### 🔴 Derived actuals (`C5`) — 8, must split

`actual_finish` is easy: `closedAt` from `gh`. `actual_start` is the hard half — first commit on
the issue's branch, across four repos.

1. **`actual_finish` from `closedAt`** (1)
2. **Branch discovery** (3) — `git for-each-ref` over four repos, matching `<kind>/<issue>-<slug>`,
   local *and* remote, with the ambiguity rules written down
3. **First-commit timestamp** (2) — `git log --reverse` against the merge-base
4. **Missing-branch reporting** (2) — a missing actual bar is a branch-naming defect and must be
   reported as one, not silently blank

### 🔴 Board UI with lane grouping (`D2`) — 8, must split

Where the UI effort concentrates.

1. **Read-only lane board** (3) — HTML table, lanes as rows, statuses as columns. **Useful on its
   own, and it is the view GitHub cannot produce at all**
2. **Drag to change status** (3) — HTMX swap + optimistic update
3. **Drag to reorder / change lane** (2)

### Not hard, but easy to get wrong

**`A4` sub-issues** (2, down from 3) — 🔧 **corrected 2026-10-10.** The earlier note that this
needs raw GraphQL was wrong. `gh` wraps it fully on 2.102.0 — `gh issue create --parent`,
`gh issue edit --add-sub-issue|--parent|--remove-parent`. Reads come from one query over
`Issue.parent` / `subIssues` / `subIssuesSummary`.

**Parentage is a GitHub-owned field.** It is *not* stored in item files, for the same reason labels
are not: GitHub already holds it, so a copy could only diverge. See *Sub-issues* below.

## Phasing — each phase independently useful

| Phase | Contents | sp | Standing value if we stop here |
|---|---|---|---|
| **1 — CLI only, terminal views** | schema, validation, cycle detection, pull, reconcile, index, **`next` / `ready` / `why` / `board`**, plus repo setup, tests and migrating the live items | **32** | **Already beats today**: real dependencies, cycle detection, server-side split rule, baselines, evidence in git, no rate limits, and a usable *what-next* answer |
| **2 — HTML views** | Jinja templates, CSS Grid board and timeline, SVG dependency arrows, `lanes render` → `.tracker/out/`, then FastAPI serving the same templates | ~18 | The board and the arrows nothing we have can draw |
| **3 — write UI + sync** | drag, title mirror, orphan reconcile, transfer handling | ~26 | Full replacement |

**Phase 1 returns to ~20 points — four weeks — on one condition:** the terminal must answer
*what next* well enough to work from, which is `lanes next` above. Charts are deferred to Phase 2
and are a *presentation* upgrade, not a capability one, because every fact a chart would show is
already in the index by the end of Phase 1.

**Phase 1 is the recommendation.** It is **32 points — six weeks** (🔧 corrected 2026-10-10 from ~20, which omitted repo setup, tests and the migration) — and it clears more MUSTs
than any tool in the survey, including the three nobody satisfied. Phases 2 and 3 are convenience
and can be judged later, on evidence, which is also the project's own methodology.

## Alternative: Go

Worth real consideration, and it loses on one axis only.

| | Go | Python |
|---|---|---|
| Distribution | **Single static binary.** No venv, no interpreter version, runs in 2031 | `uv run`, needs Python + lockfile |
| Reproducibility | **Strong** — matters for a public teaching artifact | Good, via `uv.lock` |
| SQLite | `modernc.org/sqlite`, pure Go, **no cgo** | stdlib |
| Web | `html/template` + HTMX; `templ` for typed templates | Jinja2 + HTMX |
| YAML | `goccy/go-yaml` | ruamel.yaml, **round-trips comments** |
| Validation | hand-written or `go-playground/validator` | **Pydantic v2, less code** |
| Fit with repo | **New language in a Python/Markdown repo** | Already the tooling language |

**Choose Go if** the tracker should outlive the project as a standalone artifact a reader can
`go install` and run. The single-binary story is genuinely better, and "still runs in three years"
is not a small thing for a blogged project.

**Choose Python because** it is already here. Every existing tool in this repo is Python, `uv` is
installed, Pydantic removes a chunk of validation code, and ruamel.yaml round-trips comments —
which matters when humans hand-edit the item files, as they will.

Rejected: TypeScript/Node (a build step and `node_modules` in a docs repo, for a tool with no rich
front end), Rust (compile times and ceremony for a CRUD app), Ruby/PHP (no presence in this
workspace).

---

## Appendix — options rejected

### Storage

| Option | Why not |
|---|---|
| **Postgres** | Fails `G1` and `G4`. A service to run, back up and patch, holding the authoritative data outside git, for a single-user tool with ~60 rows |
| **SQLite as source of truth** | Fails `G1`/`G5`. A binary blob is not diffable and not reviewable; `git log -p` on it says nothing |
| **One big YAML file** | Every edit touches one file, so git history becomes useless for "who changed this estimate" and concurrent sessions conflict constantly |
| **Issue body frontmatter** | Tempting — no new files. But it fights GitHub's editor, invites human mangling, and **Backlog.md's test showed what silent frontmatter loss looks like** |
| **Git notes / orphan branch** | Technically elegant, practically invisible. Fails `G1`'s "readable by someone with no account" |
| **JSON instead of YAML** | No comments. Item files will be hand-edited and the comments are the explanation |

### GitHub access

| Option | Why not |
|---|---|
| **PyGithub / Octokit / raw httpx** | Each needs a PAT. **Fails `G3`** — the exact cost that killed the auto-add Action |
| **GitHub App** | Worse: a key *and* an install, and apps cannot act on user-owned projects anyway |
| **Webhooks** | Needs a public endpoint for a localhost tool. Poll on demand instead |

### Web stack

| Option | Why not |
|---|---|
| **React / Vue / Svelte SPA** | A build step, `node_modules`, and an API boundary, for a single-user local board. HTMX does drag-and-drop with attributes |
| **Streamlit / Gradio** | Fast to start, fights you on layout, and a kanban board is exactly the layout they are bad at |
| **TUI (Textual)** | Genuinely attractive and much cheaper — but a board is a 2-D spatial artifact and the chart needs to be shareable in a blog post |
| **Static site generator** | Read-only by construction, so Phase 3 is impossible. Phase 1's `lanes render` is the useful part of this idea without the framework |
| **Mermaid** | **Rejected 2026-10-10.** Renders free on GitHub, but **draws no dependency arrows and has no critical path** — the limitation that made the Gantt not worth building. Also truncates labels and has no tooltips |
| **A JS chart library** (Chart.js, D3, Frappe Gantt) | A dependency and a build step for layout that CSS Grid already does. D3 would be justified only if the dependency graph needed force-directed layout |

### Scope

| Option | Why not |
|---|---|
| **Replace GitHub Issues too** | Doubles the work, loses sub-issues, comments, PR linkage and `gh`, and gains nothing the matrix asked for |
| **Fork an existing tool** | Backlog.md would need an estimate field *and* a safe-frontmatter fix *and* lane grouping; Redmine would need a Ruby plugin. Owning a fork of someone else's data model is worse than owning 2,000 lines of our own |
| **Two-way field sync** | Rejected on principle — see the boundary section. It is the sync-drift pathology this project exists to criticise |

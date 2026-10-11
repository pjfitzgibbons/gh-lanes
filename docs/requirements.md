# Requirements

What the tracker for Contoso Health Partners has to do. Written after building the
scheme on GitHub Issues + Projects v2 (`ms-security-docs` ADR 0001) and hitting enough walls to be worth writing down
properly before evaluating alternatives.

**Scope note.** This is a solo, public, blogged teaching project: nine Acts, two Interludes, four
repos, roughly 50 planned items plus discovered defects, worked a few hours at a time and not every
day. Requirements are sized for that, not for a team.

## Priorities

`MUST`: a tool failing this is disqualified · `SHOULD`: failing this is a real cost, recorded and
traded · `COULD`: nice, and no tool gets credit for it over a MUST.

---

## A. Structure

| # | Priority | Requirement | Why |
|---|---|---|---|
| **A1** | MUST | **One tracker spanning four repositories**, with a single portfolio view across all of them | `ms-security-docs` plus `caretasks`, `patient-directory`, `referral-intake`. Work crosses them constantly |
| **A2** | MUST | **Milestones that span repositories** | Acts are the organising unit and every Act after 1 touches several repos. GitHub milestones are per-repo, which forces either a central-issues compromise or hand-synced duplicates |
| **A3** | MUST | **Milestone carries an exit criterion**, not just a due date | An Act closes on its ⏸ checkpoint, which is sometimes stricter than "all issues closed" |
| **A4** | MUST | **Sub-tasks are first-class and schedulable**: own estimate, own dates, appear in every view | The >5-points split rule produces them constantly. A checkbox list is not sufficient: it cannot be scheduled or counted |
| **A5** | SHOULD | **Parent roll-up** that does not double-count a parent carrying children | |
| **A6** | COULD | Arbitrary depth of nesting | Two levels has sufficed so far |

## B. Estimation

| # | Priority | Requirement | Why |
|---|---|---|---|
| **B1** | MUST | **Numeric estimate per item**, Fibonacci 1 / 2 / 3 / 5 / 8 / 13 | |
| **B2** | MUST | **Estimate visible in list views without opening the item**, in one canonical place | Had to be hacked onto GitHub by prefixing titles `[3]`, which then needs a lint to stop it drifting from the real field |
| **B3** | MUST | **A rule that items above 5 points must be split can be enforced, not just documented** | 8 and 13 are refusal codes, not sizes. An 8 sitting in a sprint is a planning error |
| **B4** | SHOULD | Points queryable in bulk for roll-ups and totals | |

## C. Scheduling

| # | Priority | Requirement | Why |
|---|---|---|---|
| **C1** | MUST | **Velocity expressed per week, not per day** | Elapsed calendar time, absorbing the weeks the project is untouched. A daily rate needs a fictional working calendar to correct it |
| **C2** | MUST | **Duration derived from estimate × velocity**, not typed per item | |
| **C3** | MUST | **Baseline start and finish, frozen** and never silently recomputed | A baseline that moves when the estimate changes is not a baseline |
| **C4** | MUST | **Re-baselining is deliberate and leaves a record** of when and why | |
| **C5** | MUST | **Actual start and finish derived from evidence**, not typed: first commit on the item's branch, and the close event | A commit timestamp is evidence in git history; a typed date is an assertion. This matters in a project whose subject is audit trails |
| **C6** | SHOULD | Planned-versus-actual variance visible per item and per Act | |
| **C7** | COULD | **Gantt rendering** | Deferred: it answers "when will this be done", which for this duty cycle is a number nobody should trust. Wanted eventually, not now |
| **C8** | SHOULD | No working-calendar/weekend logic that would double-count idleness already inside the weekly velocity | |

## D. Parallelism

| # | Priority | Requirement | Why |
|---|---|---|---|
| **D1** | MUST | **A "lane" dimension: a contention domain.** Items in a lane touch the same files and run one at a time; different lanes run in parallel | This, not the dependency graph, is what limits concurrency. Two sessions editing `.claude/settings.json` collide regardless of what any graph says |
| **D2** | MUST | **Board/kanban grouping by that dimension** | GitHub cannot group a board by labels, so lanes had to become a single-select field |
| **D3** | MUST | **"What can I start right now" answerable directly**: the head of each lane with dependencies met | The daily question, and the one a Gantt never answers |
| **D4** | MUST | **Single-valued lane membership** | An item in two contention domains breaks the invariant. A multi-value label cannot enforce this |
| **D5** | SHOULD | Multiple concurrent sessions / worktrees supported without the tracker fighting it | |

## E. Dependencies and ordering

| # | Priority | Requirement | Why |
|---|---|---|---|
| **E1** | MUST | **First-class blocks / blocked-by relationships** | Dependencies drive ordering, readiness and baseline dates. GitHub Issues has native blocked-by / blocking relationships; `depends_on` is tracker-owned regardless (see the [architecture](architecture.md), *Field ownership is disjoint*) |
| **E2** | MUST | **Cycle detection**, or data good enough to detect cycles reliably in a script | A cycle makes the topological sort undefined, and the sort drives both ordering and baseline dates |
| **E3** | MUST | **Priority that lets newly filed urgent work outrank everything older** | Issue-number ordering sorts a new P0 last, which is backwards |
| **E4** | SHOULD | Dependencies are *intra-milestone only* by convention; cross-Act sequence comes from milestone order | Recording what milestone order already implies produces a dense, cycle-prone, useless edge list |
| **E5** | COULD | Readable total ordering (rank) | A bare rank was rejected: an opaque integer carries no intent where a priority band does. `ordinal`, a tiebreak inside a priority band, is adopted because ordering tasks across repos is still needed |

## F. States

| # | Priority | Requirement | Why |
|---|---|---|---|
| **F1** | MUST | **A deferred state that is visible and counted but excluded from the schedule**: the icebox | Deferred work and accidentally-dropped work must not look the same, or you cannot tell a decision from a mistake |
| **F2** | MUST | **Workflow states orderable**, because order reads as progression in any board UI | `Icebox → Todo → In Progress → Blocked → Done` |
| **F3** | SHOULD | Reordering states does not orphan stored values | |
| **F4** | MUST | **An orthogonal taxonomy alongside state**: our `repo:*`, `kind:*`, `by-design`, `verification` | `by-design` is load-bearing: a weakness recorded deliberately, closed by documenting it and never by fixing it |

## G. Evidence and provenance

| # | Priority | Requirement | Why |
|---|---|---|---|
| **G1** | MUST | **Tracking data is reviewable evidence**: in git or exportable to a committed file, diffable, and readable by someone with no account | Public teaching project ending in an Act 8 evidence pack. A row in someone's hosted database is not evidence |
| **G2** | MUST | **Full export in a documented, stable format.** No lock-in | |
| **G3** | MUST | **No new credential.** No PAT, API token or app secret stored in a repo, repo settings, or CI | The project's subject matter is credential handling, and a hard rule forbids secrets in any repo. GitHub's own auto-add Action was rejected on exactly this |
| **G4** | SHOULD | Low operational burden: no other system that itself needs patching, backing up and validating | A self-hosted tracker becomes in-scope for the project's own compliance argument |
| **G5** | SHOULD | Change history on tracking data: who changed an estimate or a baseline, and when | |

## H. Automation

| # | Priority | Requirement | Why |
|---|---|---|---|
| **H1** | MUST | **Scriptable from the command line** for lint and generated views | |
| **H2** | MUST | **Bulk writes that do not trip rate limits.** 24 single-field updates must be expressible as one or few operations | Writing 24 lane values one at a time hit GitHub's *secondary* rate limit with 4,900 of 5,000 primary calls still unused. Pacing at 0.7s did not help; only batching does |
| **H3** | MUST | **Fields readable by script.** A field that renders in the UI but returns nothing from the API is not a field | GitHub's native `Created` / `Updated` / `Closed` project fields are display-only (verified 2026-10-10) |
| **H4** | SHOULD | Custom fields attach to the **item itself**, not to its membership in a view | GitHub puts them on the project item, so an issue outside the project silently has no estimate and no dates, and a repo transfer drops every value |
| **H5** | SHOULD | Automatic membership: new items join the tracked set without a manual step | GitHub's auto-add is capped at one workflow per repo and one workflow total on the Free plan |
| **H6** | SHOULD | Validation hooks, so a rule can be enforced server-side rather than by a lint that runs later | A lint detects; it does not prevent |

## I. Cost and licence

| # | Priority | Requirement | Why |
|---|---|---|---|
| **I1** | MUST | **Free, or very cheap** for a single user | No budget is approved for this project |
| **I2** | SHOULD | **Open source**, preferably with a copyleft or permissive licence | Subject matter of a public teaching project; a reader should be able to reproduce the setup |
| **I3** | MUST | **No feature we depend on sits behind a paid tier** | OpenProject's baselines and Plane's GitHub integration both failed here |
| **I4** | SHOULD | Actively maintained: commits within the last quarter, a release within the year | |
| **I5** | COULD | Integrates with GitHub for PR/commit linking | Useful, not essential; **C5** needs commit data from *somewhere*, but a local git read satisfies it |

---

## What GitHub Issues + Projects v2 actually failed

Every failure below was verified in this project.

| Requirement | How it failed |
|---|---|
| **A2** milestones span repos | They do not. Forces central issues and a hand-synced migration at Act 1 |
| **B2** estimate visible in lists | Not shown anywhere in a list view. Worked around by prefixing titles, which needs a lint to prevent drift |
| **B3** split rule enforceable | No server-side validation. Lint only |
| **C3** frozen baseline | No concept of one. Built from two date fields and a convention |
| **C5** derived actuals | No mechanism. `Actual Finish` works only because `closedAt` is readable; `Actual Start` is still unimplemented |
| **D2** group board by lane | Cannot group a board by labels at all. Lanes had to become a single-select field |
| **E1** dependencies | Projects v2 has no dependency field; the workaround is a text field with no validation and no UI. GitHub Issues has native blocked-by / blocking (`Issue.blockedBy`, `gh issue edit --add-blocked-by`), which the tracker does not use |
| **E3** priority ordering | Projects v2 exposes no readable rank or position, so view order is unusable from a script |
| **F3** reorder without orphaning | Reordering single-select options replaces the whole list; existing option ids must be passed back or values are orphaned |
| **G3** no new credential | Satisfied only by declining automation. `GITHUB_TOKEN` cannot touch projects, so any Action needs a PAT |
| **H2** bulk writes | Secondary rate limit trips at roughly 20 project mutations regardless of pacing |
| **H3** fields readable | Native `Created`/`Updated`/`Closed` are display-only |
| **H4** fields on the item | They live on the project item, so membership becomes load-bearing and transfers drop values |
| **H5** automatic membership | One auto-add workflow per repo, one total on Free. Breaks at four repos |

**What it got right**, and a replacement must not lose: issues live beside the code, sub-issues are
native and auto-join the project, `gh` is already authenticated so no new credential is needed,
labels are flexible, and the whole thing costs nothing and needs no hosting.

## The question for the evaluation

Given that the scheme *works* today on GitHub with roughly 400 lines of Python holding it together,
is there a tool where fewer of these requirements are workarounds? A replacement that trades
fourteen workarounds for eight is progress. One that trades them for a self-hosted database with a
PAT in it is not, because **G1** and **G3** are the constraints that bind.

# 03 — Tracking options: analysis matrix

Scored against [`02-tracking-requirements.md`](02-tracking-requirements.md). Survey 2026-10-10.

**✅** native · **⚠️** workaround · **💰** paid tier · **❌** absent · **🔍** unverified

The **GH** column is this project's own experience — every ⚠️ and ❌ was hit while building the
scheme, not read in a comparison article. The question is not which tool has most features but
**which makes fewer of these a workaround.**

| # | Requirement | GH | Backlog.md | GitLab F | Redmine | Taiga | Leantime | Shortcut |
|---|---|---|---|---|---|---|---|---|
| **A1** | One tracker, 4 repos | ⚠️ | ⚠️ | ✅ | ⚠️ | ⚠️ | ⚠️ | 🔍 |
| **A2** | Milestones span repos | ❌ | 🔍 | **✅** | **⚠️** | ❌ | ⚠️ | 🔍 |
| **A3** | Milestone exit criterion | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | 🔍 |
| **A4** | Sub-tasks schedulable | ✅ | ⚠️ | 🔍 | **✅** | ❌ | ⚠️ | ✅ |
| **A5** | Parent roll-up, no double-count | ⚠️ | 🔍 | 💰 | 🔍 | ❌ | 🔍 | **✅** |
| **B1** | Numeric Fibonacci estimate | ⚠️ | ❌ | 💰 | ⚠️ | ⚠️ | **✅** | ✅ |
| **B2** | Estimate visible in lists | ❌ | ❌ | 💰 | ⚠️ | 🔍 | **✅** | 🔍 |
| **B3** | ">5 must split" enforceable | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **C1** | Velocity per week | ⚠️ | ❌ | 💰 | ❌ | ⚠️ | ❌ | ⚠️ |
| **C2** | Duration from estimate × velocity | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **C3** | Frozen baseline | ⚠️ | ❌ | ❌ | **🔍** | ❌ | ❌ | ❌ |
| **C4** | Re-baseline deliberate + recorded | ⚠️ | ❌ | ❌ | 🔍 | ❌ | ❌ | ❌ |
| **C5** | Actuals derived from evidence | ⚠️ | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | 🔍 |
| **D1** | Lane / contention dimension | ⚠️ | **✅** | 💰 | ✅ | 🔍 | ✅ | ⚠️ |
| **D2** | Board groups by lane | ⚠️ | **❌** | **❌** | 💰 | 🔍 | **⚠️** | 🔍 |
| **D3** | "What can I start now" | ❌ | **✅** | ❌ | ❌ | ❌ | ❌ | **✅** |
| **D4** | Lane single-valued | ⚠️ | ⚠️ | 💰 | ✅ | 🔍 | ✅ | 🔍 |
| **E1** | First-class blocks/blocked-by | ❌ | **✅** | 💰 | **✅** | ❌ | **❌** | **✅** |
| **E2** | Cycle detection | ❌ | **✅** | ❌ | **✅** | ❌ | **⚠️** | 🔍 |
| **E3** | New urgent outranks older | ⚠️ | **✅** | 🔍 | ✅ | 🔍 | 🔍 | 🔍 |
| **F1** | Icebox: visible, unscheduled | ⚠️ | ✅ | ⚠️ | ⚠️ | 🔍 | 🔍 | 🔍 |
| **F2** | States orderable | ✅ | ✅ | ⚠️ | ✅ | 🔍 | ✅ | ✅ |
| **F4** | Orthogonal taxonomy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **G1** | Data is reviewable evidence | ⚠️ | **✅** | ⚠️ | ⚠️ | ⚠️ | 🔍 | ❌ |
| **G2** | Full documented export | ✅ | **✅** | ✅ | ✅ | ⚠️ | 🔍 | 🔍 |
| **G3** | No new credential | ✅ | **✅** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| **G4** | Low ops burden | ✅ | ✅ | ❌ | ⚠️ | ❌ | ⚠️ | ✅ |
| **G5** | Change history on tracking data | ⚠️ | **✅** | ⚠️ | **✅** | 🔍 | 🔍 | 🔍 |
| **H1** | Scriptable from CLI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **H2** | Bulk writes, no rate-limit wall | ❌ | **✅** | 🔍 | **❌** | ⚠️ | 🔍 | ⚠️ |
| **H3** | Fields readable by script | ⚠️ | ✅ | ✅ | ✅ | ✅ | 🔍 | 🔍 |
| **H4** | Fields on the item itself | ❌ | **❌** | ✅ | ✅ | ✅ | ✅ | 🔍 |
| **H5** | Automatic membership | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **I1** | Free | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **I2** | Open source | ❌ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ❌ |
| **I3** | No depended-on feature paid | ⚠️ | ✅ | **❌** | **💰** | ✅ | 🔍 | 🔍 |
| **I4** | Maintained | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Tally

| | GH | Backlog.md | GitLab F | Redmine | Taiga | Leantime | Shortcut |
|---|---|---|---|---|---|---|---|
| ✅ | 9 | 21 | 10 | 17 | 9 | 12 | 12 |
| ⚠️ | 19 | 4 | 7 | 8 | 7 | 7 | 4 |
| 💰 | 0 | 0 | 7 | 2 | 0 | 0 | 0 |
| ❌ | 9 | 10 | 10 | 7 | 13 | 9 | 6 |
| 🔍 | 0 | 2 | 3 | 3 | 8 | 9 | 15 |

**Nobody passes C3/C4 — a frozen baseline exists in no free tool, anywhere.** Four surveys now
agree. **B3 fails universally** too: no tracker validates an estimate rule server-side. Those two
are permanent lint work whatever we pick.

## Notes per column

**GH** — baseline. ❌ clusters on dependencies (`E1 E2`), discovery (`B2 D3`), bulk writes (`H2`,
hard-stopped at ~20 project mutations with 4,900 of 5,000 primary calls unused).

**Backlog.md** — MIT, v1.53.0, push 2026-10-07. Tasks are **plain `.md` files in the repo**, which
carries `G1 G2 G3 G5 H5` by construction and makes `H2` meaningless — no remote API to rate-limit.
Natively does four things we wrote Python for: `task list --ready` (**D3**), `--dep` with a rendered
graph (**E1**), ordered `priorities` (**E3**), `--json` with a versioned `schemaVersion` (**H3**).
**Killer flaw: no estimate field and no custom fields** — `B1 B2 B4 C2` dead.

**Redmine** — *much stronger than the earlier survey credited.* Verified **in source**: `blocks` /
`precedes` / `follows` / `relates` **with cycle rejection** (`circular_dependency?` in
`issue_relation.rb`), so `E1` and `E2` are ✅ — the two things GitHub lacks outright. Versions are
**shareable across projects** (`sharing != 'none'`) giving a partial `A2`. Native parent/child with
own dates and estimates (`A4`); journals via `include=journals` (`G5`). **Costs:** no kanban in core
at all, so lanes need the **Agile plugin with swimlanes at PRO, $499** (`D2` 💰, and whether PRO
swimlanes group by a custom field is 🔍). **No bulk endpoints whatsoever** (`H2` ❌).

**GitLab Free** — the only tool that truly solves `A2`: group milestones span every project in a
group. Then charges for nearly everything else — weights, blocking issues, scoped labels,
iterations, epics, roadmap all **Premium**. And `D2` is **not purchasable at any tier**: swimlanes
group by *epic* only; label swimlanes do not exist. CE is the same free feature set plus an
8 vCPU / 16 GB ops burden.

**Taiga** — richest agile model (milestones with dates, points, `bulk_create`, project dump), but
**points live on user stories only, not tasks** (`A4`) and dependencies are a bare `is_blocked` flag
plus free text (`E1`).

**Leantime** — AGPL, v3.11.0 2026-10-09, very active. Has a real **`storypoints`** column (`B1` ✅,
rare here) and a swimlane concept with `swimlaneId`. But **dependencies are a single
`dependingTicketId` parent — no blocks/blocked-by** (`E1` ❌), and cycles break only at *display*
time rather than being prevented (`E2` ⚠️). Whether swimlanes group by a custom field is the
highest-value unknown in the survey (`D2` 🔍).

**Shortcut** — best SaaS fit: customisable numeric estimate scale, blocked/blocking with
**`is:blocked` / `is:blocker` search operators** (the only hosted tool with a real `D3`), and
**sub-task points roll up into the parent** (`A5`). Hosted and closed, so `G1` ❌; Free-tier gating
of story links and estimates unverified; 200 req/min, no confirmed bulk endpoint.

## Corrections to earlier claims in this project

From source and primary listings, not vendor summaries:

- 🔧 **Huly is no longer viable.** `hcengineering/platform` is **frozen**, the hosted service
  **discontinued**, and the active fork has no releases. **ADR 0001 names Huly as its fallback —
  that choice is void** and the ADR needs amending.
- 🔧 **Easy Gantt may be free, not paid.** The redmine.org listing (v6.0, 2025-02-19, GPL-2) says
  the "Pro" plugin is "completely FREE to download" and lists **baselines**. Vendor page 404s so
  terms are 🔍 — but ADR 0001 states flatly that it is paid, and that is not safe. **If it is free
  and works, Redmine becomes the only free tool with real schedule baselines.**
- 🔧 **OpenProject and Redmine both have cycle detection**, verified in source
  (`circular_dependency?`). I had recorded `E2` as universally absent. Wrong.
- 🔧 **OpenProject's board types are fixed** — Assignee, Basic, Status, Subproject, Subtasks,
  Version, Sprint. No custom-field board service, so `D2` fails **structurally**, not by licensing.

## Disqualified on verified facts

| Tool | Why |
|---|---|
| **Huly** | **Hosted service discontinued; `hcengineering/platform` frozen.** Active fork has no releases. ⚠️ *This was ADR 0001's named fallback — that choice is now void* |
| **Plane** | GitHub integration **and bulk operations** are Pro (pricing page, confirmed). API 60 req/min |
| **Height** | Shut down 2025-09-24 |
| **Focalboard** | README: "currently not maintained" |
| **Radicle** | Own guide: private repos have "severe security vulnerabilities… unfit for use today" |
| **Zenhub** | Free tier caps at **2 connected repos**; we need four |
| **ClickUp** | Custom fields and sprint points are **Trial-only** on Free → `D1/D2/D4`, `B1` |
| **Monday** | 3-seat minimum ≈ $27/mo, and no API below Standard |
| **Notion** | 7-day history on Free (`G5`); no repo model at all (`C5`) |
| **Jira** | Free-tier feature gating entirely unverified; heavy for one user |
| **git-bug** | No milestones, priority, dependencies, boards or fields |
| **Fossil** | Per-repo by construction. Has real custom fields — the only other git-native tool that does |
| **Gitea / Forgejo** | Hosted DB (`G1`), token for automation (`G3`), ops burden (`G4`) |
| **git-issue · sit · ticgit-ng** | Stale or dead |
| **OpenProject CE** | **Board types fixed in source** — no custom-field board, so `D2` fails structurally. Baselines are Enterprise and are a table diff |
| **Kanboard** | **Swimlanes are project-only** (`SwimlaneModel.php`) → `D2`. Has `blocks` links but **no cycle check**. No bulk API |
| **Wekan** | Typed card dependencies and an `estimation` field, but **no cycle check** and no group-by-field board found |
| **Tuleap** | **No source repo found** (404), no licence stated. Unverifiable, so unusable under a cite-or-flag rule |
| **Vikunja** | Real cross-project dependencies, but **no estimates and no milestones at all** |
| **Linear** | Free tier caps at **250 issues**; every `D1/D2/D4` question unverified |
| **ProjectLibre** | Real Gantt baselines, cannot see GitHub at all, desktop only |

## Two ideas worth stealing regardless

- **Gitea's scoped labels** — a label with `/` is exclusive within its scope, so
  `lane/a-enforcement` is single-valued. That is **D4 solved with labels**, which GitHub cannot do
  and GitLab charges Premium for.
- **Backlog.md's `isReady`** — a computed flag, not a field: unfinished *and* all dependencies
  resolved. Our `render_lanes.py` recomputes this every run; it should be the primary output.

## Open tests, cheap and decisive

1. **Backlog.md custom frontmatter** — does arbitrary YAML survive and appear in `--json`? If yes,
   `B1` and `H4` are recovered and it takes first place outright. **~20 minutes, throwaway repo.**
2. **Backlog.md cycle rejection** (`E2`) and board grouping by `projects` (`D2`).
3. **Shortcut and Linear free accounts** — can a board group by a single-select field (`D1/D2/D4`)?
   Ten minutes each, and it resolves 37 unverified cells.
4. **Group 5 — mature OSS PM** (Redmine, OpenProject CE, Leantime, Tuleap, Kanboard, Wekan) is
   still running.

---

## Verified by hands-on test, 2026-10-10

### Backlog.md — installed v1.53.0, throwaway git repo

| Test | Result |
|---|---|
| **Custom frontmatter for estimates (`B1`/`H4`)** | ❌ **FAILS DESTRUCTIVELY.** Injected `story_points`, `lane`, `baseline_start`; absent from `--json`; and **the next `task edit` silently deleted all three.** Reproduced twice on different tasks |
| JSON schema | `id title status priority ordinal project milestone parentTaskId isReady labels assignees dueDate createdAt updatedAt type reporter references modifiedFiles acceptanceCriteria*` — **no estimate key of any kind** |
| **Cycle rejection (`E2`)** | ✅ Rejected with `These dependencies would create a cycle: TASK-2 -> TASK-1 -> TASK-2` |
| **Ready queue (`D3`)** | ✅ `isReady` computed correctly — `false` for the blocked task, `true` for its blocker |
| **Lane dimension (`D1`/`D4`)** | ✅ `project` is single-valued and validated against a configured list — it refuses an unconfigured value |
| **Board grouping by lane (`D2`)** | ❌ Board groups by **status** only, with `-m` for milestone. No `--group-by project` |
| `ordinal` | ✅ A readable, writable integer rank — `--ordinal` — which GitHub has no equivalent for |

**Verdict: Backlog.md is out.** Not because estimates are missing, but because adding them is
*actively unsafe* — the tool destroys unknown frontmatter on every edit. That turns the gap from a
workaround into silent data loss, and it also kills the lane board (`D2`).

### Leantime — source inspection of v3.11 (not a live instance)

The swimlane question is answered by `getGroupByFieldOptions()` in
`app/Domain/Tickets/Services/Tickets.php`. **Swimlane grouping is real**, with eleven options:

`all · dueDate · effort · milestone · parentTask · priority · project · sprint · status · type · user`

| Finding | Consequence |
|---|---|
| **`effort` maps to the `storypoints` column** — confirmed at `Repositories/Tickets.php:631` (`zp_tickets.storypoints`) | **`B1` ✅ and `B2` ✅** — a board that groups by estimate. The only tool surveyed that does |
| The option list is **hardcoded**; grep for `customfield`/`hook` in it returns **0** | **`D2` ⚠️** — swimlanes are genuine but a bespoke lane must be mapped onto an existing field. Mapping lanes onto `project` collides with milestones being project-scoped |
| `parentTask` maps to `dependingTicketId` — a **single parent** | **`E1` ❌** confirmed. No blocks/blocked-by, so `D3` cannot exist either |

**Verdict: Leantime is the estimate/board story without the dependency story.** The inverse of
Backlog.md. ⚠️ This is source inspection, not a running instance — grouping was not exercised.

### Test 3 — not run

Creating Shortcut and Linear accounts means signing up under your name and accepting their terms.
That is yours to do, not mine. Fifteen minutes gets ~25 🔍 cells resolved; the questions are:

1. Can a board group by a **custom single-select** field? (`D1 D2 D4`)
2. Can a sub-task carry its **own** estimate, and does it roll up without double-counting? (`A4 A5`)
3. Is there a **full export** in a documented format? (`G1 G2`)
4. Shortcut: are **story links and estimates** available on Free at all?

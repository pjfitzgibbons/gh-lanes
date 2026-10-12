# ADR 0006: Tracked time comes from an external time tracker, snapshotted into the item file

<a id="status"></a>
## 1. Status

Proposed.

<a id="context"></a>
## 2. Context

Estimates are points ([`B1`](../requirements.md)), and planned-versus-actual variance is wanted per
item and per milestone ([`C6`](../requirements.md)). Points say how big an item is, but not what it cost.
Tracking and reporting on cost needs the time spent on each item.

Open-source and commercial time trackers all record the same thing: spans of time carrying tags
or a project.

The tracker is not GitHub and not git. Its data lives outside both stores that this tool already
treats as authoritative ([ADR 0001](0001-git-is-the-database.md),
[ADR 0003](0003-disjoint-field-ownership.md)). Reading it means a third kind of I/O, alongside the
`gh` and `git` subprocesses.

<a id="decision"></a>
## 3. Decision

Estimates stay in points, and hours come from a calibration. `config.yml` carries
`hours_per_point`, which defaults to 8 (one point is one working day). A project that sizes a point
as an hour sets it to 1. An item's estimated hours are `estimate × hours_per_point`. No item has an
hours estimate of its own.

Actual time is read from an external time tracker through one vendor-neutral interface. Each
vendor gets one adapter module under `src/ghlanes/timekeeping/`. Core code sees only the interface,
which returns the tracker's time entries for a work item. A tracker is optional, and with none
configured the feature is off.

`gh.py`, `git.py` and the `timekeeping/` adapters are the only modules that spawn a process or
open a network connection. Everything else stays pure.

Time entries are tied to an issue by a tag, `gh:<owner>/<repo>#<n>`. Every tracker considered
supports free-form tags, and the tag is set by whoever starts the timer.

The total is snapshotted into the item file when the issue closes. Reconcile already moves a
closed issue's item to `Done`. In the same write it records the total tracked time and where it came
from. Reports read the snapshot. They never query the tracker live.

How a networked adapter authenticates is decided when the first networked adapter is built.

Design detail is in [design 0002](../design/0002-tracked-time.md).

<a id="alternatives"></a>
## 4. Alternatives considered

- An hours estimate on each item, alongside points. It is a second estimate that drifts from the
  first, and nothing reconciles them.
- Building timers into gh-lanes (`lanes start`, `lanes stop`). That makes the tool a time tracker,
  which is a product of its own, and existing ones already do the job.
- Calling one vendor directly with no interface. It ties item data and reports to that vendor, and
  changing trackers then means changing core code.
- Querying the tracker live at report time. Reports then depend on a system outside git, fail
  offline, and change when someone edits an old entry. The figure is not reproducible from the repo.
- Copying every time entry into the item file. It turns each file into a log and churns its
  history. The total, the entry count and the query that produced them are enough to reproduce or
  audit the number.
- Recording time on GitHub, for example as issue comments. It adds a write-back, and ADR 0003 holds
  the title prefix as the only one.
- Tying entries to an issue through a task or activity entity in the tracker. It needs gh-lanes to
  create those entities, which is a write to another system, and not every tracker has them.
- Tying entries to an issue by git branch. Only automatic trackers (WakaTime, Wakapi) record the
  branch, so it cannot be the common key. An adapter for one of those can still match on branch.

<a id="consequences"></a>
## 5. Consequences

- `C6` gets an hours view: estimated hours against tracked hours per item and per milestone, and
  the observed hours per point against the configured `hours_per_point`.
- `actual_time` joins the tracker-owned fields. It is written by reconcile and by `lanes time`,
  never pushed to GitHub, and never typed by hand.
- The figure is evidence with provenance: tracker, tag, entry count and fetch time sit next to the
  total, and `git log -p` shows when it changed ([`G5`](../requirements.md)).
- A tracker that is unreachable at close does not block reconcile. The item goes to `Done` without
  a snapshot, `validate` warns, and `lanes time N --apply` fills it in later.
- Time logged after the close is not counted until someone re-snapshots the item.
- The process rule in [ADR 0004](0004-python-no-docker.md) and the
  [design 0001 layout](../design/0001-phase-1.md#layout) widens to include `timekeeping/`. Adapters
  are tested against recorded tracker output, the same way `gh.py` is.
- An issue transfer changes both parts of the tag key. Entries tagged under the old key are not
  found until transfer handling (Phase 3) adds the old key to the query.

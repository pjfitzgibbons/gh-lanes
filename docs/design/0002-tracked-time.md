# Design 0002: Tracked time

**Implements:** [ADR 0006](../adr/0006-tracked-time.md) · **Requirements:**
[`C6`, `C9`](../requirements.md) · **Status:** draft

<a id="scope"></a>
## 1. Scope

**In:** `hours_per_point` calibration · the `TimeSource` interface · the `actual_time` snapshot in
item files · snapshot on close in reconcile · `lanes time` · `lanes report time` · validation rules
· index columns.

**Out:** any specific vendor adapter, and how a networked adapter authenticates. Both are settled
when the first adapter is built. §10 records how each surveyed tracker would map onto the
interface.

<a id="config"></a>
## 2. Config

Two keys join `.tracker/config.yml` ([design 0001, *Config*](0001-phase-1.md#config)):

```yaml
# .tracker/config.yml
hours_per_point: 8.0     # one point = one working day. A project sizing a point as an hour sets 1.0
time_source:             # absent = tracked time is off
  kind: timewarrior      # selects the adapter module in src/ghlanes/timekeeping/
```

`hours_per_point` converts an estimate into hours for reporting. It is unrelated to
`points_per_week`: velocity is elapsed calendar time ([`C1`](../requirements.md)), while
`hours_per_point` is effort. A point can be eight hours of effort and still take most of a week to
land.

The value is set by hand. `lanes report time` prints the observed hours per point next to it, and
whoever owns the config decides whether to change it.

Any further keys under `time_source` belong to the adapter named by `kind`.

<a id="data-model"></a>
## 3. Data model

```python
# model.py
class ActualTime(BaseModel):
    seconds: int                 # sum of closed entries; running entries excluded
    entries: int                 # how many closed entries were summed
    running: int = 0             # entries still open at fetch time, not counted
    source: str                  # time_source.kind that produced it
    key: str                     # the tag queried, e.g. "gh:example-org/web-app#23"
    fetched_at: datetime

class Item(BaseModel):
    ...
    actual_time: ActualTime | None = None   # written by reconcile and `lanes time --apply` only
```

In an item file:

```yaml
# .tracker/items/web-app/23.yml
estimate: 2
status: Done
actual_time:
  seconds: 15300         # 4.25 h
  entries: 7
  source: timewarrior
  key: "gh:example-org/web-app#23"
  fetched_at: 2026-10-11T18:04:00Z
```

Estimated hours are never stored. They are `estimate × hours_per_point`, computed at report time,
so changing the calibration rescales every report without touching an item file.

`actual_time` is tracker-owned and is never pushed to GitHub. Nobody types it: `set` has no flag
for it, and `validate` does not check it against anything except its own shape.

<a id="key"></a>
## 4. The correlation key

A time entry belongs to an item when it carries the tag `gh:<owner>/<repo>#<n>`, built from
`config.repos[repo].gh` and `issue`. Whoever starts the timer adds the tag. With Timewarrior:

```
timew start "gh:example-org/web-app#23"
```

`lanes show N` prints the tag, so it can be copied rather than typed.

An entry can carry other tags too, and one entry with two item tags counts toward both items. To
split a span between items, split it in the time tracker.

<a id="interface"></a>
## 5. The `TimeSource` interface

```python
# timekeeping/__init__.py
@dataclass(frozen=True)
class WorkKey:
    tag: str                          # "gh:example-org/web-app#23"
    repo: str                         # "example-org/web-app"
    issue: int
    branches: tuple[str, ...] = ()    # for adapters that match on git branch

@dataclass(frozen=True)
class TimeEntry:
    source_id: str          # the vendor's own id, so one entry is never counted twice
    start: datetime         # UTC
    end: datetime | None    # None = still running
    tags: frozenset[str]

class TimeSource(Protocol):
    kind: str
    def entries(self, key: WorkKey) -> list[TimeEntry]: ...

class TimeSourceError(Exception): ...   # unreachable, misconfigured, or bad output

def load(config: TimeSourceConfig) -> TimeSource: ...   # picks the module by `kind`
```

`entries` is the whole contract. It reads and never writes: gh-lanes does not start, stop, create
or edit anything in the time tracker. An adapter raises `TimeSourceError` for any failure and never
returns a partial list.

Summing is pure and lives outside the adapters:

```python
# timekeeping/total.py
def snapshot(key: WorkKey, entries: list[TimeEntry], kind: str, now: datetime) -> ActualTime
```

It drops duplicate `source_id`s, sums `end - start` over closed entries, and counts open ones in
`running`.

Adapters, like `gh.py` and `git.py`, are allowed to spawn a process or open a connection. Nothing
else in `timekeeping/` is.

<a id="lifecycle"></a>
## 6. When the snapshot is taken

The trigger is the issue closing. A PR that merges with `Closes #N` closes the issue, so a merge
reaches the trigger through that. A merge that leaves the issue open takes no snapshot, because
time is counted per issue, not per PR.

| Event | What happens |
|---|---|
| Reconcile sees a closed issue whose item is not `Done` | Sets `status: Done` and writes `actual_time` in the same file write. Dry by default, like all of reconcile |
| No `time_source` configured | Reconcile sets `Done` and writes no `actual_time` |
| Time tracker fails | Reconcile still sets `Done`, prints the `TimeSourceError`, and leaves `actual_time` absent. `validate` warns until someone runs `lanes time N --apply` |
| Issue reopened | The snapshot stays: it is what was tracked up to that close. The next close overwrites it, and git keeps the earlier value |
| Time logged after the close | Not counted until `lanes time N --apply` |
| Issue transferred | Both parts of the tag change, so entries tagged with the old key are missed. Phase 3 transfer handling adds the old key to the query |

Reconcile collects the items that close in one run and queries the tracker once per item. All of
the writes are local file writes, so nothing here touches GitHub's rate limits.

<a id="commands"></a>
## 7. Commands

| Command | What it does |
|---|---|
| `lanes time N` | Prints the stored snapshot next to a live total from the tracker, and the difference. Writes nothing |
| `lanes time N --apply` | Takes a fresh snapshot and writes it. Works on open items too, for a mid-flight check that gets committed |
| `lanes report time [--milestone M]` | Estimate against actuals, per item and in total (§8) |

`lanes time` and `lanes report time` take `--json`, like every other read.

<a id="report"></a>
## 8. `lanes report time`

```
$ lanes report time --milestone beta
#     est  est h   actual h   variance
#14    3    24.0     19.5      -4.5   -19%
#9     5    40.0     52.0     +12.0   +30%
#23    2    16.0      4.3     -11.7   -73%
#31    3    24.0       —          no snapshot
───
       10   80.0     75.8      -4.2    -5%     (3 of 4 items with a snapshot)
hours per point: configured 8.0 · observed 7.6
```

- Only `Done` items with a snapshot count toward the totals and the observed hours per point. An
  item without one is listed and counted in the footnote, so a gap is visible rather than read as
  zero.
- A parent with children has no estimate ([design 0001, *Validation*](0001-phase-1.md#validation)).
  Its row sums its children's estimates and snapshots, plus its own snapshot if time was tagged to
  the parent itself. That row is for display only: totals count each child's estimate and snapshot
  once, from the child's own row, and add only the time tagged to the parent itself.
- Observed hours per point is total actual hours over total estimated points, with the same rule,
  so no estimate or snapshot is counted twice.

<a id="index"></a>
## 9. Index and validation

The `item` table gains `actual_seconds INT`, `actual_entries INT` and `actual_source TEXT`, and
`v_work` carries them through. Rebuilding the index never calls the time tracker; it reads the
snapshots in the files.

Rules added to [design 0001 §9](0001-phase-1.md#validation):

| Rule | Level | Message |
|---|---|---|
| `time_source.kind` names an installed adapter | ERROR | `time_source kind 'x' has no adapter` |
| `actual_time` only on an item with an issue | ERROR | `#N is a draft and has actual_time` |
| Done item has a snapshot, when a `time_source` is configured | WARN | `#N is Done with no tracked time — run lanes time N --apply` |
| No timer was running at snapshot | WARN | `#N had 1 timer running at snapshot; that time is not counted` |
| Snapshot has entries | WARN | `#N is Done with 0 tracked entries for gh:owner/repo#N` |

<a id="adapters"></a>
## 10. How each tracker would implement `entries`

None of these is built yet. The table records how each surveyed tracker would map onto §5, so the
interface is known to fit more than one.

| Tracker | Query | Matched by | Notes |
|---|---|---|---|
| Timewarrior | `timew export <tag>` over a subprocess. Returns a JSON array of `id`, `start`, `end`, `tags`, `annotation` | tag | Local, no credential. Its documented sample output has a trailing comma, so parse leniently 🔍 |
| Kimai | `GET /api/timesheets?tags[]=<tag>`, paginated with `page` and `size` | tag | Bearer token. Requests fail if none of the tags exist, which the adapter treats as zero entries |
| solidtime | REST, scoped to an organisation | task or tag 🔍 | API token. Endpoint details unverified 🔍 |
| Traggo | GraphQL | key:value tag, e.g. `issue:` | Its model is only tagged time spans, with no tasks |
| WakaTime / Wakapi | summaries filtered by `project` and `branches` | `WorkKey.branches` | Automatic: no timer to start. WakaTime records `branch` per heartbeat; Wakapi's branch support is unverified 🔍. A summary has no per-entry ids, so the adapter synthesises one entry per day |
| ActivityWatch | `GET /api/0/buckets/<id>/events` on `localhost:5600` | none | Records applications and windows, not tasks. Not a fit |
| Watson | reads its frames file | tag | No release since 2.1.0 (May 2022) |

<a id="testing"></a>
## 11. Testing

- `snapshot()` is pure. It gets cases for duplicate ids, running entries, an empty list, and one
  entry carrying two item tags.
- Reconcile is tested with a fake `TimeSource` covering three cases: it returns entries, it returns
  none, and it raises. The raise case asserts the item still reaches `Done`.
- Each adapter, when built, is tested against recorded tracker output committed as a fixture, with
  synthetic tags and times. No network in the suite.

<a id="requirements-coverage"></a>
## 12. Requirements coverage

| # | Requirement | How |
|---|---|---|
| C6 | Planned against actual, per item and per milestone | `lanes report time`, in hours, per item and per milestone |
| C9 | Tracked effort per item, calibrated against points | `actual_time` snapshot, `hours_per_point`, observed hours per point in the report |
| G5 | History of tracking data | the snapshot is committed YAML; `git log -p` shows every re-snapshot |

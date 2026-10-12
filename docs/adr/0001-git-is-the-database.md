# ADR 0001: Git is the database; SQLite is a disposable index

<a id="status"></a>
## 1. Status

Proposed.

<a id="context"></a>
## 2. Context

Tracking data has to be reviewable evidence: committed or exportable, diffable, and readable by
someone with no account ([`G1`](../requirements.md)). Changes to an estimate or a baseline need a
history of who changed them and when ([`G5`](../requirements.md)). The store should not be another
system to back up, patch and validate ([`G4`](../requirements.md)).

A tracker whose history is git history gives the planning data the same audit trail as the code. A
reviewer can follow derived facts and the commits that changed them.

Commands and the web views still need to sort, filter and join planning data with GitHub facts
without re-parsing every item file on each request.

<a id="decision"></a>
## 3. Decision

The source of truth is one YAML file per item at `.tracker/items/<repo>/<n>.yml` and one per milestone at
`.tracker/milestones/<id>.yml`, committed in git. Nothing authoritative lives anywhere else.

SQLite at `.tracker/.cache/index.db` is a derived index of those files joined with GitHub facts. It
is gitignored, can be deleted at any time, and `plan reindex` rebuilds it from the committed
files.

Where `.tracker/` lives is [ADR 0002](0002-tracker-per-repo.md). Which fields an item file may hold
is [ADR 0003](0003-disjoint-field-ownership.md).

<a id="alternatives"></a>
## 4. Alternatives considered

- Postgres. It fails `G1` and `G4`: a service to run, back up and patch, holding the authoritative
  data outside git, for a single-user tool.
- SQLite as the source of truth. It fails `G1` and `G5`. A binary file is not diffable or
  reviewable, and `git log -p` on it says nothing.
- One big YAML file. Every edit touches the same file, so git history cannot answer "who changed
  this estimate", and concurrent sessions conflict constantly.
- Frontmatter in the issue body. It needs no new files, but it fights GitHub's editor and invites
  people to mangle it. The [alternatives survey](../alternatives-survey.md) records a tool that
  silently deleted unknown frontmatter on edit.
- Git notes or an orphan branch. Both work technically and are invisible in practice, which fails
  `G1`'s "readable by someone with no account".
- JSON instead of YAML. JSON has no comments, and item files are hand-edited with comments that
  explain them.

<a id="consequences"></a>
## 5. Consequences

- `G1`, `G2`: the data is committed YAML, readable in a browser on GitHub, with no export step and
  no lock-in.
- `G5`: `git log -p .tracker/items/web-app/23.yml` shows who changed an estimate or baseline, when, and the
  commit that explains why.
- `G4`: there is no database to operate. A corrupt index is deleted and rebuilt.
- [`C3`, `C4`](../requirements.md): a frozen baseline is a value in a committed file, and
  re-baselining shows up as a diff with a commit message.
- [`B3`](../requirements.md): validation runs at write time, in the tool's own code, so the split
  rule is enforced rather than linted afterwards.
- Several requirements come free with this choice
  ([design 0001, *Requirements coverage*](../design/0001-phase-1.md#requirements-coverage)).
- Two sessions editing different items touch different files and merge cleanly. Two sessions
  editing the same item get an ordinary git conflict in a short YAML file.
- The index can be stale. Commands refresh it from GitHub when it is old, and `--offline` works
  from it alone, because every tracker-owned field is local.

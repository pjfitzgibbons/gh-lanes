# ADR 0003: GitHub and the tracker never hold the same field

<a id="status"></a>
## 1. Status

Superseded by [ADR 0008](0008-file-native-items.md), which puts every field in the item file.

<a id="context"></a>
## 2. Context

GitHub and the tracker both describe the same issues. Any field held in both places can diverge,
and keeping it in step needs a sync engine with conflict rules.

GitHub already owns identity, title, body, state, labels, assignee, comments, sub-issue links and
`closedAt`. It also has native dependencies: the GraphQL `Issue` type has `blockedBy`, `blocking`
and `issueDependenciesSummary`, with `addBlockedBy` and `removeBlockedBy` mutations, and
`gh issue edit` has `--add-blocked-by` and `--remove-blocked-by` (verified against the API on `gh`
2.102.0). Planning fields have no good home on GitHub. Project fields live on the project item
rather than the issue, so an issue outside the project has no values and a transfer drops them. Some native project
fields are display-only. Writing project fields one at a time trips GitHub's secondary rate limit.

[ADR 0001](0001-git-is-the-database.md) makes committed item files the source of truth for
whatever the tracker owns.

<a id="decision"></a>
## 3. Decision

Field ownership is disjoint.

- GitHub-owned fields (title, body, state, labels, assignee, comments, sub-issue links and parent,
  dependencies through blocked-by, `closedAt`) are never stored in an item file. They are read
  through `gh` and cached in the index.
- Tracker-owned fields (estimate, priority, status, ordinal, lane, baseline, milestone, actual
  time) live in item files and are never pushed to GitHub.
- The only write-back is the `[N]` estimate prefix in the issue title
  ([`B2`](../requirements.md)), one field in one direction, applied by `plan mirror`.

Dependencies are GitHub-owned because GitHub has the feature natively, and a second dependency
store in item files would duplicate it. The tool is read-only for them: pull reads `blockedBy` and
caches the edges in the index. People edit dependencies in GitHub or with
`gh issue edit --add-blocked-by` and `--remove-blocked-by`.

<a id="alternatives"></a>
## 4. Alternatives considered

- Two-way field sync. Every synced field can drift, and each one needs rules for which side wins.
  That is the sync-drift problem the tool exists to remove.
- Planning fields in GitHub project fields. They attach to the project item, not the issue,
  some are display-only, and batches of writes trip the secondary rate limit.
- A tracker-owned `depends_on` list in each item file, validated at write time and never pushed to
  GitHub.

<a id="consequences"></a>
## 5. Consequences

- No file holds a copy of a GitHub field, so there is nothing to reconcile field by field.
  Reconcile handles membership: an issue with no item file, an item whose issue no longer resolves,
  and an item's status when its issue closes or reopens.
- Each further write-back would add a reconciliation problem, so the title prefix is the only one.
  When someone edits the title on GitHub and drops the prefix, mirror detects the drift and
  re-applies it.
- A GitHub milestone or labels set on a new issue are offered as triage suggestions and never
  imported, because GitHub's milestones are not the tracker's ([`A2`](../requirements.md)).
- Dependencies are visible to anyone reading GitHub, and there is one place to edit them.
- The tool cannot reject a dependency at write time, because it never writes one. GitHub's
  `addBlockedBy` rejects a self-dependency and a cycle between two issues, but accepts a longer
  cycle such as A blocked by B, B by C and C by A (verified against the API on `gh` 2.102.0,
  2026-10-11). `plan validate` therefore checks the pulled graph for cycles
  ([`E2`](../requirements.md)).
- Dependency changes are not in git history with the other planning fields
  ([`G5`](../requirements.md)).
- Someone reading only GitHub sees estimates through the title prefix and nothing else the tracker
  owns.

# Test fixtures

These are synthetic `.tracker/` trees and the `gh` output a pull would record for them. The suite runs against them with no network. Every owner is `example-org`, and every node ID is invented (`I_example_<repo>_<n>`). No real name, login, email, node ID or repo appears here, and `test_fixtures.py` checks the owners.

## Layout

Each tree is a tracker root. The recorded output sits where a real pull caches it, `.tracker/.cache/gh/<repo>.json`, one file per configured repo, named by the repo's short name in `config.repos`.

```
valid/web-app/                         the tracker root of a two-repo plan
  .tracker/                            config, milestones alpha and beta, items for both repos, one draft
  .tracker/.cache/gh/web-app.json      gh issue list output for example-org/web-app
  .tracker/.cache/gh/billing-api.json  ... and for example-org/billing-api
broken/<rule>/                         one tree per design 0001 §9 rule
  .tracker/
  .tracker/.cache/gh/web-app.json
```

In a real tracker `.cache/` is gitignored, by the `.tracker/.gitignore` that `plan init` writes. The fixture trees have no `.tracker/.gitignore`, so their recordings are committed, and `test_fixtures.py` checks that none appears.

## valid/

`valid/web-app/` passes every rule in design 0001 §9. The `billing-api` sibling (`path: "../billing-api"`) isn't on disk, because nothing that reads this tree opens a repo's working tree. The tree holds:

- **Items in every status.** `web-app#1` and `#10` are Done, `#2` and `billing-api#2` are In Progress, `#4` is Blocked, `#5` is Icebox, and the rest are Todo.
- **Closed issues of both kinds.** `#1` was closed as completed and `#10` as not planned.
- **A needs-triage item.** `#6` has no estimate. Validation reports it as a WARN, and it's the only finding.
- **A parent with children.** `#7` has two sub-issues, `#8` and `#9`, and no estimate.
- **A blocker in the other repo.** `#4` is blocked by `billing-api#2`, which is open and in the same milestone.
- **A baseline,** on `#2`.
- **A draft,** `items/web-app/draft-01JA7Z3K8M.json`.
- **Two milestones,** `alpha` (order 100) and `beta` (order 200).

`plan next` here returns `billing-api#1`, the only P0.

## broken/

Each directory is named for the one §9 rule it trips. Apart from that one fault, every tree is valid. Tracker files carry no comments ([ADR 0007](../../docs/adr/0007-tracker-files-are-json.md)), so each tree's fault is listed here:

| Tree | Fault |
|---|---|
| `blocked-by-cycle` | `#1` is blocked by `#2`, `#2` by `#3`, `#3` by `#1`. GitHub accepts a three-issue cycle |
| `blocked-by-other-milestone` | `#2` (beta) is blocked by `#1` (alpha); milestone order already says so |
| `blocked-without-blocker` | `#1` is Blocked but nothing blocks it |
| `blocker-outside-repos` | `#1` is blocked by `example-org/shared-lib#7`, a repo not in `config.repos` |
| `done-but-open` | `#1` is Done but its issue is open |
| `estimate-not-allowed` | `#1` has estimate 8: a refusal code, not a size |
| `lane-not-configured` | `#1` is in lane `mobile`, which `config.lanes` doesn't list |
| `milestone-absent-not-icebox` | `#1` has no milestone but its status is Todo, not Icebox |
| `milestone-file-missing` | `#1` is in milestone `gamma`, which has no `milestones/gamma.json` |
| `milestone-order-duplicate` | `alpha` and `beta` share order 100 |
| `needs-triage` | `#1` has an estimate but no lane |
| `ordinal-duplicate` | `#1` and `#2` share ordinal 100 in lane `api` |
| `orphan-item` | `items/web-app/2.json` names an issue GitHub doesn't return |
| `parent-with-estimate` | `#1` has a child, `#2`, and still carries an estimate |
| `status-not-in-schema` | `#1` has status `In Review`, which isn't one of the five |
| `title-estimate-mismatch` | `#1`'s title says `[3]`; its estimate is 2 |
| `untracked-issue` | `#2` is open on GitHub and has no item file |

Only two trees fail before any rule runs, because the schema itself rejects their items: `estimate-not-allowed` (estimate 8) and `status-not-in-schema` (status `In Review`).

The rule "baseline frozen for a closed milestone" has no message in §9, and milestones have no closed state, so it has no tree yet. It gets one when #15 defines it.

`test_fixtures.py` maps every directory to its §9 rule. It also reads the rule table from the design doc, so adding a rule there without a tree here fails the suite.

## Recorded gh output

Every `.tracker/.cache/gh/<repo>.json` is what this call returns, with the same keys and nesting, newest issue first:

```sh
gh issue list --repo R --state all --limit 500 \
  --json number,id,title,state,stateReason,closedAt,labels,blockedBy,parent,subIssuesSummary
```

The shape was checked by hand against live calls on **gh 2.102.0, 2026-10-13**:

| Field | Shape |
|---|---|
| `blockedBy` | `{nodes: [{id, number, state, title, url}], totalCount}` |
| `parent` | `null`, or `{id, number, state, title, url}` |
| `subIssuesSummary` | `{completed, percentCompleted, total}` |
| `labels` | `[{color, description, id, name}]` |
| `stateReason` | `""` while open; `COMPLETED` or `NOT_PLANNED` once closed |
| `closedAt` | `null` while open; an ISO 8601 timestamp once closed |

### When gh's output changes

1. Run the call above against any repo you can read. Look only at the keys, nesting and types, never the values.
2. Update the table above and `ISSUE_KEYS`, `REF_KEYS`, `LABEL_KEYS` and `SUMMARY_KEYS` in `test_fixtures.py`, then edit the JSON files until the suite passes. Rebuild them by hand: never paste live output, because it carries real titles, logins and node IDs.
3. Record the new `gh` version and the date in the heading above.

---
title: "Items are file-native: ADRs 0007 and 0008, requirements"
type: chore
status: Done
estimate: 3
priority: P1
ordinal: 100
lane: infra
milestone: bootstrap
started: 2026-10-14T13:19:36Z
---
### Summary
gh-plan becomes its own tracker. An item is a Markdown file with YAML front matter, committed in the repo it belongs to, and GitHub Issues is no longer used; pull requests are the one GitHub integration. This ticket records the decision: ADR 0008 (file-native items), ADR 0007 rewritten in place (every tracker file is YAML, items and milestones are Markdown), and the requirements it changes or adds. The design and architecture docs follow in a separate ticket.

### Scope
- **ADR 0008, new.** Each repo keeps its own items in `.tracker/items/<id>.md`. IDs are the repo's prefix and a random pronounceable CVCVC word (`pl-bakor`), with a blocklist; the prefix can be dropped inside its own repo, and any unique prefix of the word, a title word, or the current branch identifies an item. Dependencies and parents are in the file, cycle-checked across the plan. Any repo's `.tracker/` can also list member repos and become a plan, holding the milestones that span repos; an item's milestone is looked up in its own repo first. The repo's default branch (`main`, or `develop` under git-flow) carries the tracker's current state. Work happens on a branch named for the item (`feat/pl-bakor-slug`). A skill calling `plan start <id>`, or a `post-checkout` hook on branch creation or `git worktree add`, makes a curated tool commit (`plan: start <id>`) to the default branch setting In Progress and `started`, pushes it, and the item's branch contains it; `plan stop <id>` abandons a start. The finish is the merge: the branch sets `status: Done`, and the actual finish is the commit on the default branch that made it Done. The tool's only remote write is a `git push` of its own commits; it reads PRs only for report links. Supersedes ADR 0003.
- **ADR 0007, rewritten in place.** Every committed tracker file is YAML: items and milestones as Markdown with front matter, `config.yml` and `focus.yml` as plain YAML. Read as YAML 1.2 with ruamel.yaml's safe loader, then type-checked by the schema. One canonical form, quoting any string a YAML 1.1 or 1.2 reader would type otherwise; the Markdown body is written back unchanged. No comments are kept.
- **Requirements changed by the decision:**
  - `C5`: actual start is the tool's start commit on the default branch; actual finish is the commit on the default branch that makes the item Done, not an issue's close event.
  - `E1`: blocked-by lives in the item file; the reference to GitHub's native relationship goes.
  - `F4`: labels live in the item file, not on a GitHub issue.
  - `H5`: an item joins the plan by existing as a file; restate or drop.
  - `H6`: "server-side" becomes a pre-commit hook or a CI check.
  - `I5` stays a COULD: `C5` reads local git, not PRs.
  - `D1`, `D3`, `D4` stay as they are here; #71 rewrites them (lanes as themes, `ready` as the top N).
- **Requirements added:**
  - `D6` SHOULD: `.tracker/ready.yml` is the committed answer to `plan ready`: the next 20 ready items with what `ready` reports (ID, title, estimate, duration, lane, milestone, priority, focus, what each unblocks), plus when and at which commit it was generated. A second section lists the items in flight: each branch on `origin` that names an item, with the item's ID and title, the branch, its `started` and `started_via`, and the date of its last commit. Only pushed branches are listed, so the file is the same whichever machine generates it. A viewer reads it on GitHub or in an editor with no tool installed.
  - `G7` SHOULD: an item's front matter shows the data behind `plan why` without a tool. `blocked_by` is a list of `"<id> - <title>"` strings; the ID is authoritative, and the tool rewrites the title part on every write.
- **Prefix:** this repo's prefix is `pl`, and the examples in ADR 0008 use it.
- **`CLAUDE.md`:** "It is not an issue tracker" and "GitHub Issues keeps owning identity, state, labels and dependencies" are no longer true, and "never commit straight to `main`" gains an exception for the tool's `plan:` commits.
- Out of scope:
  - architecture, designs 0001 and 0002, ADRs 0001 to 0004 and 0006, the README, `tests/fixtures/README.md` and the `CLAUDE.md` invariants list, which follow in a separate ticket;
  - the converters (JSON to YAML, issues to item files) and the code;
  - a new name for the tool, now that GitHub is one integration rather than the centre.

### Acceptance
- ADR 0008 is in `docs/adr/`, and ADR 0007 states the YAML and Markdown format.
- `requirements.md` has the changes and the two additions above, and the `CLAUDE.md` statements are corrected.
- Every claim about an outside tool or library in both ADRs is cited or marked 🔍.
- The prose has had a humanizer pass.

### Tests
None: documentation only.

### Lenses
- [x] L1 Security: the safe loader refuses object tags; the tool needs no token, since it only reads PRs through `gh`
- [x] L2 Privacy and data: titles and bodies are now committed in the repo, so they are exactly as public as the repo
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: JSON trackers convert to YAML and Markdown; open issues convert to item files once
- [x] L7 Usability and accessibility: `ready.yml` and readable `blocked_by` entries answer the daily question without the tool
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [x] L10 Docs impact: two ADRs, requirements and `CLAUDE.md` here; the rest in the follow-up ticket
- [x] L11 Invariants: invariants 2, 4 and 6 go; invariant 10 keeps only tracked time
- [x] L12 Offline and concurrency: every query, start and finish included, works offline; random IDs keep concurrent worktrees from colliding; a second branch for an item already started finds `started` set and leaves it, and `plan validate` reports a `started` later than the item's first tracked time; `ready.yml` conflicts on merge and is regenerated

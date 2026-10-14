# ADR 0008: Items are file-native, and git records their progress

<a id="status"></a>
## 1. Status

Proposed. Supersedes [ADR 0003](0003-disjoint-field-ownership.md), and amends
[ADR 0002](0002-tracker-per-repo.md) and [ADR 0006](0006-tracked-time.md).

<a id="context"></a>
## 2. Context

Under [ADR 0003](0003-disjoint-field-ownership.md) an item is a GitHub issue plus a tracker file.
GitHub owns identity, title, body, state, labels, sub-issues and blocked-by, and the file owns the
planning fields. Keeping the two in step is most of the tool's GitHub code:

- `pull` caches each repo's issues, and `reconcile` creates, closes and reports orphaned item files
  from that cache ([architecture §6](../architecture.md#operations)).
- `mirror` writes the `[N]` estimate prefix into issue titles, the one write-back, and every write is
  paced by the secondary rate limit (invariant 6).

The planning data is meant to live beside the code and docs it plans, committed in the same repo
([ADR 0001](0001-git-is-the-database.md), [ADR 0002](0002-tracker-per-repo.md)). With issues on
GitHub, only half of each item does: its title, body, state and dependencies stay in GitHub, outside
the repo's history.

GitHub Issues gives this project an issue number, a web page per issue, and `Closes #N` closing an
issue when its PR merges. It is used by one person ([requirements](../requirements.md)), so issue
comments, notifications and assignment do little that the commit history does not.

Actual start and finish come from evidence, not typed dates ([`C5`](../requirements.md)). Work
happens on a branch and lands on the default branch as one squash commit, so the default branch's
history keeps the merge but not the branch's commits or its name. A squash commit's message can be
edited at merge time, so it is not reliable evidence either.

The default branch is the one GitHub has configured for the repo: `main` in a repo that merges
straight to it, `develop` in one using git-flow, where pull requests target `develop` and releases
go to `main`. It is the branch a viewer of the repo sees first.

<a id="decision"></a>
## 3. Decision

The tracker files are the whole record of an item, and they live in the repo the item belongs to.
GitHub Issues is not used.

- Each repo keeps its own items in its own `.tracker/items/<id>.md`, committed with its code
  and docs. A repo is planned on its own with no other repo present.
- An item file is a Markdown body under a front matter header. The body follows the issue
  outline (Summary, Scope, Acceptance, Tests, Lenses). The header holds every field: title, status,
  estimate, priority, ordinal, lane, milestone, labels, parent, blocked-by, started and baseline.
  The header's syntax is [ADR 0007](0007-tracker-files-are-yaml.md)'s.
- IDs are the repo's prefix and a random pronounceable word, such as `pl-bakor` in gh-plan.
  The word alternates consonant and vowel, five letters long (CVCVC), from 16 consonants and 5
  vowels: about 102,000 words per repo, with a blocklist for words that read badly. The prefix is
  set in the repo's `config` and names the repo, so an ID means the same item in any plan that
  includes it. The tool picks a word no existing file uses, so two worktrees creating items at once
  are unlikely to collide ([`D5`](../requirements.md)), and no counter needs merging. A word can be
  said aloud and typed from memory.
- An ID is rarely typed in full. Inside its own repo the prefix may be left off. Any unique
  prefix of the word is enough (`bak`), and so is a unique word from the title. Commands run on a
  branch named for an item take its ID from the branch, and shell completion offers IDs with their
  titles.
- Dependencies are `blocked_by` in the file, and may name an item in another repo of the same
  plan. The tool checks every write for a cycle across the whole plan
  ([`E1`, `E2`](../requirements.md)). A parent is `parent: <id>` on the child
  ([`A4`](../requirements.md)).
- Every repo's `.tracker/` is a plan. One that also lists member repos by path spans them, and
  reads their items in place. It keeps its own items like any repo, and also holds the milestones
  that span repos ([`A2`](../requirements.md)). Every query across the plan reads the members' files
  ([`A1`](../requirements.md)). Sibling repos find the plan through the root pointer (#77).
- A milestone named on an item is looked up in the item's own repo first, then in the plan that
  lists the repo as a member. A repo can keep milestones of its own beside that plan's.
- Work on an item happens on a branch named for it, `<type>/<id>-<slug>`, such as
  `feat/pl-bakor-json-files`, in the item's own repo.
- The default branch carries the tracker's current state. Whatever it says about an item is
  the item's status, and the tool commits to it directly when work starts or stops. Every other
  change to the tracker reaches it through a pull request, like code.
- The start is a tool commit on the default branch. Two signals start an item: a skill calls
  `plan start <id>`, or a `post-checkout` hook, which git runs when a branch is created or checked
  out and after `git worktree add`, sees a branch name carrying an ID. The tool sets
  `status: In Progress`, `started` (UTC, to the second) and `started_via`, regenerates
  `ready.yml`, commits both to the default branch and pushes. It never overwrites an existing
  `started`.
- The item's branch contains its start commit. `plan start` commits the start first and then
  creates the branch from it. The hook finds the branch already made, so it fast-forwards the
  branch onto the start commit if the branch has no commits of its own yet. Otherwise it writes
  the same change into the branch's working tree, and `plan validate` reports the branch as not
  containing its start.
- `plan stop <id>` abandons a start, committing the item back to Todo on the default branch
  and keeping `started` out of the file.
- The finish is the merge. The branch sets `status: Done` before it merges, and the change
  reaches the default branch in the same squash commit as the work. Its actual finish is the
  committer date of the first-parent commit on the default branch that made it Done. An item worked
  across several branches is set Done by the last of them.
- A tool commit is curated. It touches only one item's `status`, `started` and `started_via`,
  plus `ready.yml`. The tool builds it on the tip of the default branch through a temporary index,
  without checking that branch out, so nothing else in the working tree can get into it and the
  working tree does not change. Its message is fixed, `plan: start <id>` or `plan: stop <id>`, so
  `git log --grep '^plan:'` finds every one. Offline, the commit is kept locally and pushed by the
  next `plan sync` or `git push`.
- The tool's only remote write is a `git push` of its own commits. It never writes through
  GitHub's API. Reading a repo's pull requests through `gh` only adds the PR number and link to
  reports.

<a id="alternatives"></a>
## 4. Alternatives considered

- Keep GitHub Issues ([ADR 0003](0003-disjoint-field-ownership.md)). Issues give a web page,
  comments and closing by keyword. The cost is the sync above, half of each item living outside the
  repo, and the rate limit on every write.
- One central tracker for every repo in a plan. All items in one directory, each listing the
  repos it touches. Cross-repo work and ordering are simpler, but an item no longer sits beside the
  code it plans, and a repo cannot be planned or cloned with its own backlog.
- Issues for intake only. Others file issues; the tracker imports each one once and closes it
  with a link to the item. It keeps a public front door and adds an import path. No one else files
  issues in these repos yet, so it waits until someone does.
- Sequential IDs (`pl-12`). Easier to say and type. Two branches that each create an item take
  the same number, and the second merge has to renumber the file and every reference to it.
  gh-issue-sync handles this with temporary IDs rewritten after a push
  ([gh-issue-sync](https://github.com/mitsuhiko/gh-issue-sync)); random IDs avoid the problem.
- Random base32 IDs (`pl-7k3q`), as ticket and beads use. Four characters give about a million
  IDs, but a string like `7k3q` cannot be said aloud or remembered, and mixes letters and digits
  that are easy to confuse.
- A merged PR whose body says `Closes <id>` sets the item Done. It needs a GitHub read for every
  finish, and the keyword is the tool's own, so GitHub does not check it.
- A trailer in the squash commit message (`Closes: <id>`), read from local history. The message
  is edited at merge time, so the evidence is only as good as that edit.
- Merge commits instead of squash. The branch's commits and name survive in the default branch's
  history, so start and finish can be read from git alone. It gives up squash-merging, which keeps
  the default branch one commit per change.
- git notes on the merge commit. They need a step after every merge, and notes are not pushed
  or fetched by default.
- The start recorded only on the item's branch, reaching the default branch with the work.
  A false start never leaves the branch, and the tool never commits on its own. But the default
  branch never shows an item In Progress, because the start and the finish reach it in one squash
  commit, so no one but the person doing the work sees what is under way.
- A separate branch holding only tracker commits. It keeps tool commits out of the code's
  history, but the item file then lives on two branches that have to be merged with each other
  regularly, and a viewer has to know to look there.
- A Claude Code hook that starts an item when a request mentions its ID. A request can mention an
  item without starting work on it, so a skill that begins work calls `plan start` itself.
- Adopt a file-native tracker. Backlog.md deletes frontmatter it does not know on the next edit
  ([alternatives survey](../alternatives-survey.md)), so it cannot hold estimates or baselines.
  beads gives each item a source repo and combines several repos into one view, but stores its data
  in Dolt rather than plain files, and its GitHub sync takes a token
  ([beads sync](https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md)),
  which [`G3`](../requirements.md) rules out. ticket keeps Markdown files with random IDs and
  readiness commands, but has no estimates or milestones
  ([ticket](https://github.com/wedow/ticket)).

<a id="consequences"></a>
## 5. Consequences

- `pull`'s issue cache, `reconcile` and `mirror` go away. Invariants 2, 4 and 6 are removed, and
  invariant 10 keeps only tracked time.
- Start, finish and Done are all read from the files and local git, so every query works offline
  and `C5` needs no GitHub read. Only sharing a start needs the network. `I5` stays a COULD.
- The tool now owns what GitHub did: titles, bodies, labels, parents, dependencies and cycle
  checks. Each needs a command or a validated hand edit ([`G6`](../requirements.md)).
- Anyone reading the default branch sees which items are In Progress. `ready.yml` adds the
  branches on `origin` that name an item, with each one's last commit.
- A false start is shared as soon as it is pushed, so it needs `plan stop`.
- Because the branch contains its start commit, the branch's own change from In Progress to Done
  merges without a conflict. A branch that missed its start conflicts on the `status` line.
- Two branches that each create an item can, rarely, pick the same word. The second merge
  conflicts on the new file, and `plan validate` reports a duplicate ID.
- A second branch for an item already started finds `started` set and leaves it.
  `plan validate` reports a `started` later than the first tracked time for the item.
- The tool finds the default branch from `refs/remotes/origin/HEAD`, which `git clone` sets and
  `git remote set-head origin --auto` refreshes, so it needs no GitHub read.
- Branch protection must let the owner push to the default branch. On gh-plan, `main` requires the
  `pytest` check, and `enforce_admins` is off, so an admin's push goes through (read from the branch
  protection API on 2026-10-14). The rule is also strict: a pull request must be up to date with
  `main` before it merges, so every tool commit puts each open pull request one commit behind.
- `CLAUDE.md`'s rule "never commit straight to `main`" gains one exception: the tool's `plan:`
  commits.
- Tool commits make up part of the default branch's history. A git-flow release to `main` carries
  them too.
- `plan hooks install` writes the `post-checkout` hook beside the `post-merge` hook of
  [design 0002](../design/0002-tracked-time.md#post-merge). Git takes `post-checkout`'s exit status
  as the checkout's, so the hook always exits 0.
- A branch for an item lives in the item's repo. Work an item needs in another repo is a child item
  there.
- A plan across repos depends on their checkouts sitting where the plan's config says. A member
  missing on disk is reported, and the plan is answered without it.
- A change that touches several repos, such as moving items into a shared milestone, is one commit
  per repo. Nothing makes them atomic.
- A cross-repo `blocked_by` is checked only from a plan that lists both repos. A repo validated on
  its own reports a reference to another repo as unresolved, not as an error.
- There is no web page per item until the web UI exists. GitHub renders the Markdown file, which
  covers reading.
- Discussion lives in PR reviews and commit messages. Nothing replaces issue comments.
- Requirements change: `C5`'s start is the tool's start commit and its finish the commit on the
  default branch that makes an item Done, `E1` no longer cites GitHub's blocked-by, and `F4`
  labels live in the file.
- ADR 0002 keeps a `.tracker/` per repo, and any of them can list member repos to span them.
  That plan's `config.repos` names checkouts by path, not GitHub repos holding issues.
- A repo milestone with the same ID as a milestone in a plan that lists the repo hides that plan's
  milestone for the repo's items. `plan validate` reports the shadowing.
- ADR 0006 tags time entries with the item ID (`pl-bakor`) instead of `<owner>/<repo>#<n>`.
- The issue-based skills (`gh-issues`, `worktask`, the `plan` stand-in) and tt's branch parsing
  change to the new IDs and branch names, and `worktask` calls `plan start`.
- The open issues in each repo are converted once into that repo's item files, keeping each body,
  and then closed on GitHub with a pointer to the file.

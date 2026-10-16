# ADR 0010: Plan state lives on a `gh-plan` branch, checked out at `.tracker/`

## Contents

- [1. Status](#status)
- [2. Context](#context)
- [3. Decision](#decision)
  - [3.1 Where it lives](#where)
  - [3.2 Commits](#commits)
  - [3.3 The finish](#finish)
  - [3.4 Without `.tracker/`](#detached)
  - [3.5 Invariants](#invariants)
  - [3.6 Moving an existing repo](#migration)
- [4. Alternatives considered](#alternatives)
- [5. Consequences](#consequences)

<a id="status"></a>
## 1. Status

Proposed. Amends [ADR 0001](0001-git-is-the-database.md), [ADR 0002](0002-tracker-per-repo.md) and
[ADR 0008](0008-file-native-items.md).

<a id="context"></a>
## 2. Context

Under [ADR 0008](0008-file-native-items.md) the tracker lives on the default branch. The tool
commits each start and stop straight to it, and every other change to an item rides on a branch and
reaches it in a pull request, beside the code.

Two costs of that show up on every item:

- On gh-plan, `main` requires pull requests to be up to date before they merge, so each
  `plan: start` puts every open pull request one commit behind. Each of them then needs a rebase
  that has nothing to do with its own change, which is why design 0003 has a `rebase` card.
- Every branch regenerates `ready.yml`. Two branches in flight conflict on it, and whichever merges
  second fixes it by hand.

The default branch also has to allow the owner's direct push, the one exception to
"everything reaches it by pull request".

Git keeps a branch checked out in at most one worktree. Asked to check out a branch already in use,
`git worktree add` refuses: "'gh-plan' is already used by worktree at …" (Apple Git 2.54, tried on
2026-10-16; [git-worktree(1)](https://git-scm.com/docs/git-worktree#_description)). In a clone,
`git worktree add <path> <branch>` creates the branch tracking `origin/<branch>` when only the remote
has it ([git-worktree(1)](https://git-scm.com/docs/git-worktree#Documentation/git-worktree.txt-addltpathgtltcommit-ishgt)).

<a id="decision"></a>
## 3. Decision

A repo's plan state lives on its own branch, `gh-plan`, and nowhere else. The default branch carries
the code and none of the tracker.

<a id="where"></a>
### 3.1 Where it lives

- `gh-plan` is an orphan branch. Its root holds what `.tracker/` held: `items/`, `archive/`,
  `milestones/`, `config.yml`, `ready.yml`, `focus.yml` and the `.gitignore` for `.cache/` and
  `out/`.
- The default branch's `.gitignore` has `/.tracker`. It has no trailing slash, so it also matches
  a symlink.
- The main checkout has `gh-plan` checked out as a worktree at `.tracker/`, with
  `git worktree add .tracker gh-plan`. Nothing is copied or synced by hand.
- Item worktrees share that one worktree. `worktask start` makes a symlink at the item worktree's
  `.tracker`, pointing at the main checkout's `.tracker/`. Discovery's walk up from the working
  directory then finds it, and an item's path is `.tracker/items/<id>.md` in every checkout.
- Where no `.tracker/` is found by walking up, discovery tries the main worktree, the directory
  holding `git rev-parse --path-format=absolute --git-common-dir`.
- A fresh clone sees its plan with one command, `git worktree add .tracker gh-plan`. `plan init`
  in a repo with no `gh-plan` branch creates it as an orphan and attaches it.

<a id="commits"></a>
### 3.2 Commits

- Every change to the tracker is a commit on `gh-plan`, pushed straight to `origin/gh-plan`. No pull
  request targets `gh-plan`.
- Tool commits are `plan: start <id>`, `plan: stop <id>` and `plan: done <id>`. The tool builds each
  one from `gh-plan`'s tip through a temporary index, and moves `refs/heads/gh-plan` by
  compare-and-swap, as ADR 0008 decides for the default branch. It then writes the same change into
  the `.tracker/` working tree and its index entry for those paths. An uncommitted hand edit to the
  same item is kept and stays uncommitted.
- Other edits, such as an item's body, its outline or its Done ticks, are made in `.tracker/`, reviewed
  with `git -C .tracker diff`, and committed from a plan-board card. The card commits only the paths
  it names.
- The item's branch no longer contains its start. It holds code and docs only, so nothing about the
  item conflicts at merge.
- Two starts can race as before. When a push to `gh-plan` is rejected because it moved, the tool
  fetches, re-reads the item on the new tip, and either does nothing or rebuilds its commit there.
  A rejected push of a hand commit is `git -C .tracker pull --rebase`; a conflict on `ready.yml` is
  resolved by regenerating it.

<a id="finish"></a>
### 3.3 The finish

The item file is no longer in the pull request, so the merge no longer finishes it.

- `plan done <id>` finishes it. It sets `status: Done`, moves the file to `archive/`, writes the
  `actual_time` snapshot and `merge: <sha>`, regenerates `ready.yml`, and commits `plan: done <id>`.
- `<sha>` is the commit the pull request made on the default branch. `worktask done` already reads
  the pull request's state with `gh pr view`, and the same read gives the merge commit. The tool
  checks that `<sha>` is on the default branch's first-parent history before it commits.
- The actual finish is the committer date of `<sha>`, read from local git. The one GitHub read
  happens when `plan done` runs, and every later query uses only local git.
- Offline, `plan done` refuses before it writes anything, because the pull request cannot be read.

<a id="detached"></a>
### 3.4 Without `.tracker/`

A checkout without the `.tracker/` worktree still has the `gh-plan` ref.

| Command | No `.tracker/` worktree, `gh-plan` ref present | No `gh-plan` ref |
|---|---|---|
| Reads: `ready`, `next`, `list`, `show`, `report` | Read the ref with `git show` and warn, naming `git worktree add .tracker gh-plan`. Uncommitted edits elsewhere are not seen | Exit 2, naming `git fetch origin gh-plan` and the attach command |
| Writes: `start`, `stop`, `done`, `new`, `edit`, `freeze` | Refuse, exit 2, naming the attach command | Refuse, exit 2, naming `plan init` |
| `validate` | Validates the ref and warns | Exit 2 |

<a id="invariants"></a>
### 3.5 Invariants

Architecture §10's invariants 2, 3 and 5 become:

- **2.** `gh-plan` carries the tracker's current state. What it says about an item is the item's
  status. The default branch carries none of the tracker, and every change reaches it through a
  pull request, with no exception.
- **3.** A tool commit is a commit on `gh-plan` that touches one item and `ready.yml`, with the
  message `plan: start <id>`, `plan: stop <id>` or `plan: done <id>`. Start and stop touch only
  `status` and `started`. Done touches `status`, `actual_time` and `merge`, and moves the file to
  `archive/`.
- **5.** The tool's only remote write is a `git push` of its own commits to `gh-plan`. It never writes
   through GitHub's API. `plan done` reads one pull request through `gh`. Outside the tool, a
   plan-board card Peter presses may push an item branch or `gh-plan`, open or update a pull request
   with `gh pc` or `gh pb`, and request Copilot's review of a pull request it opens.

<a id="migration"></a>
### 3.6 Moving an existing repo

History moves with `git subtree split`, which rewrites the commits that touched `.tracker/` with the
paths at the root and keeps each commit's author and committer dates (Apple Git 2.54, tried on
2026-10-16).

1. In the main checkout, on an up-to-date default branch:
   `git subtree split --prefix=.tracker -b gh-plan`, then `git push -u origin gh-plan`.
2. A pull request on the default branch runs `git rm -r --cached .tracker` and adds `/.tracker` to
   `.gitignore`. It is merged like any other.
3. After it merges, each checkout pulls, then runs `rm -rf .tracker` and
   `git worktree add .tracker gh-plan`. Each item worktree gets the symlink from step 3.1.

Items already Done keep their finish. Their Done commit's committer date is carried onto `gh-plan`
by the split, and the tool reads an archived item without `merge` from that date. An item In Progress
during the move is finished with `plan done` like any other.

<a id="alternatives"></a>
## 4. Alternatives considered

- Keep the tracker on the default branch ([ADR 0008](0008-file-native-items.md)). An item lands in
  the same squash commit as its code, and one branch shows everything. The cost is the context
  above, paid on every item.
- An orphan branch rejected as invisible ([ADR 0001](0001-git-is-the-database.md)), and a separate
  tracker branch rejected because the item file lives on two branches that must be merged
  ([ADR 0008](0008-file-native-items.md)). Here the file lives on one branch only, so nothing merges
  between them. It is readable on GitHub at the branch's tree, and the default branch's README links
  to it, so `G1`'s reader with no account still reads it.
- A copy of `.tracker/` in each item worktree, each a worktree of its own branch off `gh-plan`.
  Every session would have a stale plan, and the copies would merge into `gh-plan` the way branches
  merge into `main` now.
- Discovery through `--git-common-dir` alone, with no symlink. The tool finds the plan, but Claude
  and the editor see the item file at a path outside the worktree.
- Finish found from a squash commit whose subject starts `<id>:`. It needs no GitHub read, but the
  subject is edited at merge time, which ADR 0008 rejects as evidence.
- Finish set by a `post-merge` hook when a pull brings in a commit naming the item. It is local,
  but it rests on the same edited message.
- Pull requests into `gh-plan` for item edits. They keep GitHub's review, at the cost of a branch
  for every edit to a Markdown file that `git diff` already shows.
- A git submodule holding the tracker. It needs a second repo, and the default branch would record
  a submodule pointer that moves with every plan change, putting a commit back on it for each one.

<a id="consequences"></a>
## 5. Consequences

- A `plan:` commit no longer puts open pull requests behind, and branches no longer conflict on
  `ready.yml`. Most `rebase` cards go away.
- The default branch has no direct-push exception, so its branch protection can apply to admins.
- Every session reads the same `.tracker/`, so a start, an edit or a new item is seen at once,
  without a rebase.
- An item no longer lands in the same squash commit as its code. A pull request does not show the
  item's Done ticks, and reverting a pull request does not reopen its item.
- The finish is a step after the merge, and needs the network once. An item whose `plan done` never
  runs stays In Progress; `ready.yml` lists it in flight with no branch on `origin`, which shows it.
- The plan is not on the branch a visitor sees first. They reach it through the README's link or the
  branch list.
- A fresh clone needs `git worktree add .tracker gh-plan` before it sees its plan; until then reads
  work from the ref and warn.
- `git clean -ffdx` in the main checkout deletes `.tracker/`, including its uncommitted edits;
  `git clean -fdx` leaves it. Pushed commits come back with the attach command.
- The `post-checkout` hook also runs when `.tracker/` is attached. The branch `gh-plan` names no
  item, so it does nothing.
- A plan that spans repos is unchanged: `config.repos` names checkouts by path, and each member's
  `.tracker/` is its own `gh-plan` worktree.
- Freeze commits its baselines on `gh-plan`, with the reason in the commit message, instead of in a
  pull request ([`C3`, `C4`](../requirements.md)).
- Requirements change: `C5`'s start is the tool's start commit on `gh-plan` and its finish the
  committer date of the merge commit `plan done` records; `D6`'s `ready.yml` is on `gh-plan`.
- Docs change: ADRs 0001, 0002 and 0008 point here; architecture §3, §7, §8 and §10; design 0001's
  *Discovery*; design 0003's `worktask-start` check and ready list, which read `origin/gh-plan`;
  and `CLAUDE.md`'s *Done differently*. `worktask start` makes the symlink and `worktask done`
  runs `plan done`.

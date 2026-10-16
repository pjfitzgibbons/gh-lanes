# ADR 0009: The plan board

## Contents

- [1. Status](#status)
- [2. Context](#context)
- [3. Decision](#decision)
- [4. Alternatives considered](#alternatives)
- [5. Consequences](#consequences)

<a id="status"></a>
## 1. Status

Proposed. Amends invariant 5 in [architecture §10](../architecture.md#invariants). Designed in
[design 0003](../design/0003-plan-board.md).

<a id="context"></a>
## 2. Context

Claude does an item's work in a worktree, and Peter runs every commit, push and `gh` write. Each of
those steps reaches him as a command line, which he copies into a terminal: `worktask start`, the
post-pr line, a rebase after another PR merged, `gh pb` after a follow-up commit, and
`worktask done` from the main checkout. One item's session hands over six or more of them, across
two VS Code windows.

Copying commands has three costs. Peter reads a command, not what it will do to which files.
Claude finds out what ran only by reading `git log`, so it can go on editing a commit message that
was already committed. And a step Claude may not run, such as `git rebase`, which this repo's
settings deny, turns into a question in chat that Peter answers by running the command anyway.

Two constraints hold. No design may need paid API tokens: anything Claude does runs through the
Claude Code CLI under Peter's subscription ([`I1`](../requirements.md)). And no agent pushes or
writes to GitHub; that stays Peter's ([architecture §10](../architecture.md#invariants),
invariants 2 and 5).

<a id="decision"></a>
## 3. Decision

Claude prepares and Peter presses Go.

- **Cards.** For each step Claude would hand over, it writes a card, a small YAML file in the main
  checkout's `.tmp/plan-board/<id>/`, that names one recipe and the files the recipe uses, with each
  file's SHA-256, and lists in `steps` every command ▶ will run, verbatim and in order. The runner
  works out its recipe's commands again at ▶ and refuses a card whose steps differ. An item's
  cards are its steps in order, starting with 01 `worktask-start`. They outlive the worktree, and
  each repo keeps the cards of its last three items done.
- **Recipes.** The runner, `plan_board.py`, knows eight recipes: `worktask-start`, `commit`,
  `rebase`, `ship`, `pr-body`, `review`, `issue-close` and `worktask-done`. Each one checks its preconditions, runs
  in its own directory, and refuses rather than guesses. A card whose files changed since it was
  planted is refused.
- **The plan board.** A VS Code sidebar lists, across the repos Peter lists, each repo's ready
  items, each item in progress with its current card, and the last three items done. ▶ *Start* on a
  ready item plants card 01 and runs it. Peter reviews a card's files in the diff editor and presses
  ▶, which runs the card in a named terminal. Clicking an item switches to its worktree's window.
  When `ship` opens a PR it requests Copilot's review, and the runner plants a `review` card, which
  the sidebar polls each minute until the review is posted. Claude's fixes for it go out in a new
  `ship` card, which waits for ▶ like any other. The sidebar grows out of worktask's existing
  extension.
- **Results.** The runner appends each step's record to its card: the tool versions, the log and
  the result. A Claude Code hook gives Claude the results it hasn't seen at the start of its next
  turn, and Claude reads a card's result before it plants the next.
- **Claude never runs a recipe.** A `PreToolUse` hook denies Claude's Bash any command that names
  the runner, and the runner refuses to start under Claude's Bash tool.
- The runner, the hooks and the extension live in `~/.claude/skills/plan-board/`, beside `worktask`.
  gh-plan gains no code that spawns a process.

<a id="alternatives"></a>
## 4. Alternatives considered

- **A FastAPI console that hosts agents through the Agent SDK.** One page would run every item's
  agent and show its buttons. The Agent SDK authenticates with an API key and bills per token, which
  breaks the no-paid-tokens constraint, and it would be a second agent host beside Claude Code.
- **Claude Desktop** (pl-zupak, iced). One Desktop session per item worktree, with its sidebar as
  the view of everything in flight, and the hand-over as a skill and later a mod button. The spike
  didn't give the hand-over Peter wanted, and Desktop's worktree and archive behaviour isn't
  documented well enough to build on.
- **A terminal-only runner.** The same cards and recipes, run with `plan_board.py next` in a
  terminal. It needs no extension, but Peter still types, reviews files in another window, and has
  no one view of the items in flight. The runner is this alternative's core, so it can still be used
  this way.
- **An HTML board**, generalising `complete.py serve`, the Complete explainer's button. A page on
  127.0.0.1 lists the cards and runs one on a click. It needs a server, a port, a per-launch token
  and a Host check for every board, and it reviews files as text in a page instead of in the diff
  editor Peter already reads. The sidebar needs no port.

<a id="consequences"></a>
## 5. Consequences

- Peter copies no commands. Every push and `gh` write still happens only when he presses ▶.
- Invariant 5 gains an exception outside the tool: a card Peter presses may push an item branch,
  open or update its PR with `gh pc` or `gh pb`, request Copilot's review of a PR it opens, and
  close the issues an import moved into item files. Invariant 6 is unchanged, because gh-plan gains no code that spawns a process.
- The hand-over in `post-pr`, `worktask` and the gh-issues *Complete* page changes from a command
  line to a card. Until the runner ships, Peter runs a card's steps himself, copied from the card.
- The eight recipes are the whole vocabulary. A step none of them covers is a new recipe, added to
  the runner and reviewed like code, never a command added to a card.
- The sidebar depends on VS Code's extension API and on the `gh` CLI being signed in. The runner
  works without the sidebar, from a terminal.
- `rebase` and `ship` do what this repo's settings deny Claude (`git rebase`, `git push`). The deny
  rules stay, because Claude still must not run them itself.

---
title: "Design 0003 and ADR 0009: the Go board"
type: chore
status: In Progress
estimate: 3
priority: P2
ordinal: 20660
lane: web
milestone: phase-2
started: 2026-10-16T02:38:44Z
---
### Task
Design the Go board: Claude writes action cards for each step it would otherwise hand over as a command, and Peter reviews each card's files and runs it with one press, in VS Code first. Commands are no longer copied into a terminal by hand, and no paid API tokens are spent.
- The card format (`.tmp/go/<id>/<nn>-<slug>.yml`) and the fixed recipe list, with the checks each recipe makes before it runs.
- The `go` runner, and the `PreToolUse` hook that keeps Claude from running it.
- The VS Code sidebar: the Go tree, review in the diff editor, ▶ in a named terminal, the status bar and toast, and "Send back to Claude".
- `docs/design/0003-go-board.md` in the global outline plus §6 to §8, and ADR 0009 *Go board*, with the alternatives considered: a FastAPI console hosting agents through the Agent SDK (needs paid tokens), Claude Desktop (the spike), a terminal-only `go`, and an HTML board.
- The doc edits: invariant 5's exception for a push and `gh pc` Peter presses; the CLAUDE.md boundaries on agent commits and on handing over commands as cards; a requirement for one view of every item in progress across repos.
- pl-gokul loses its stale "auto-pull applies" line.

### Guardrails
- No code: nothing under `src/`, `tests/` or `~/.claude` changes. Building goes to the §8 items.
- Each doc edit is agreed in chat first, then made in place on the branch.
- Every existing requirement ID is kept.
- Every push and `gh` write runs only when Peter presses Go; no agent runs a recipe.
- No paid API use and no token or key anywhere (G3, I1).
- Sample items and repos in the docs are synthetic.

### Lenses
- [x] L1 Security: recipes are a fixed list, never shell from a card; the runner binds no network port for the sidebar; a `PreToolUse` hook denies Claude the runner
- [x] L2 Privacy and data: cards live in `.tmp/`, ignored, never committed
- [x] L3 Reliability and failure: a recipe failing partway, a card whose files changed after review, a rejected push, a stale card after a merge
- [ ] L4 Performance and limits
- [x] L5 Observability: live output in a named terminal, each card's result recorded, failures one click from Claude
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: one Go tree for every item in flight across repos, keyboard-operable
- [x] L8 Testability: the runner's recipes and checks are testable without the network
- [x] L9 Operations and cost: no paid tokens; the extension installs from a local `.vsix`
- [x] L10 Docs impact: ADR 0009, architecture §10, requirements, CLAUDE.md
- [x] L11 Invariants: 5 gains the Go exception; 6 holds, because gh-plan gains no code that spawns a process
- [x] L12 Offline and concurrency: several worktrees' cards at once; two presses of one card never both run

### Done
- [ ] `docs/design/0003-go-board.md` exists, and its §5 answers every lens L1 to L12.
- [ ] The design specifies the card format and each recipe's steps and checks.
- [ ] Design §7 maps each requirement it meets; §8 lists its items, each estimated 1, 2, 3 or 5.
- [ ] ADR 0009 is written in the repo's ADR shape, with the alternatives considered.
- [ ] L1: the design lists the recipes, says no card carries shell, and names the hook that denies Claude the runner.
- [ ] L2: the design says where cards live and that none is committed.
- [ ] L3: the design has a failure-modes section covering each case in the lens.
- [ ] L5: the design says what Peter sees while a recipe runs and when it fails.
- [ ] L7: the design shows the Go tree across repos and one card's review.
- [ ] L8: the design's §6 says how the runner is tested without the network.
- [ ] L9: the design records that no paid tokens or credentials are added.
- [ ] L10: architecture §10, the requirements and CLAUDE.md carry the agreed edits.
- [ ] L11: invariant 5 is amended and invariant 6 is shown to hold.
- [ ] L12: the design says how one card is kept from running twice.
- [ ] pl-gokul no longer says "auto-pull applies".
- [ ] pl-zupak is Icebox.
- [ ] `uv run pytest` passes, coverage gate included.

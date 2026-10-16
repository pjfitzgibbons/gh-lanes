---
title: "Design 0003 and ADR 0009: the work console in Claude Desktop"
type: chore
status: In Progress
estimate: 3
priority: P2
ordinal: 20650
lane: web
milestone: phase-2
blocked_by:
  - "pl-veles - Import gh-plan's open GitHub issues into .tracker/items, then close them"
started: 2026-10-16T01:53:25Z
---
### Task
Design how Claude Desktop runs an item's work: one Desktop session per item worktree, every item in flight visible in Desktop's sidebar, and the hand-off of commit, push, PR and cleanup as a skill now and a mod button later. This replaces the localhost console that hosts agents through the Agent SDK, and `worktask`'s VS Code hand-off, which relies on undocumented parts of the Claude Code extension.
- A spike in Desktop first. It answers whether Desktop's worktree option fires `WorktreeCreate` and under what name, whether a session can open an existing worktree, whether Archive fires `WorktreeRemove`, and what Create PR writes in a PR body.
- `docs/design/0003-work-console.md`, in the global design outline plus §6 to §8. It covers the start path the spike picks, the session lifecycle, the agent Bash policy, the hand-off skill, failure modes, the requirements it meets (§7), and the items that build it (§8): the hooks, the `worktask` changes, the hand-off skill and the mod.
- ADR 0009 *Work console*: the console is Claude Desktop plus hooks and skills. Alternatives considered: a FastAPI console hosting agents through the Agent SDK, the VS Code extension, and the CLI under tmux.
- The doc edits the ADR needs: invariant 5 gains a console exception (the push and `gh pc` behind a button Peter presses, never run by an agent); CLAUDE.md gains the boundary that an agent commits only on its own item branch; a requirement for one view of every item in progress across repos.
- pl-gokul loses its stale "auto-pull applies" line, once pl-veles merges and this branch is rebased onto it.

### Guardrails
- No code: nothing under `src/`, `tests/` or `~/.claude` changes. Building goes to the §8 items.
- Each doc edit is agreed in chat first, then made in place on the branch.
- Every existing requirement ID is kept.
- `plan:` commits go to `main` and nothing else does (invariant 2). Every push and `gh` write stays Peter's.
- No token or API key anywhere (G3). Desktop sessions run under Peter's own Claude login.
- Sample items and repos in the docs are synthetic. The spike runs in a throwaway repo.
- Out of scope: `plan serve` (pl-gokul), which stays a separate read-only web UI.

### Lenses
- [x] L1 Security: an agent's Bash is limited by a `PreToolUse` hook (commit on its own item branch, no push, no `gh` write); hooks and mods run unsandboxed with Peter's permissions
- [x] L2 Privacy and data: transcripts and session IDs stay in `~/.claude/projects`, never committed
- [x] L3 Reliability and failure: a failing `WorktreeCreate` hook, a `worktask` failure, Archive before the PR merges, a rejected push
- [ ] L4 Performance and limits
- [x] L5 Observability: what Desktop shows while a session runs, when a hook fails, and at hand-off
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: Desktop's sidebar as the one view of every item in flight, across repos
- [x] L8 Testability: the spike's hook log is the evidence for every claim about Desktop's behaviour
- [x] L9 Operations and cost: no new credential and no cost beyond Peter's subscription
- [x] L10 Docs impact: ADR 0009, architecture §10, requirements, CLAUDE.md
- [x] L11 Invariants: 5 gains the console exception; 6 holds, because gh-plan gains no code that spawns a process
- [x] L12 Offline and concurrency: several sessions at once, and a session moving between Desktop and the terminal with `claude --resume`

### Done
- [ ] The spike's four questions are answered from the hook log and recorded in the design, each claim with its source or marked 🔍 unverified.
- [ ] `docs/design/0003-work-console.md` exists, and its §5 answers every lens L1 to L12.
- [ ] Design §7 maps each requirement the console meets; §8 lists its items, each estimated 1, 2, 3 or 5.
- [ ] ADR 0009 is written in the repo's ADR shape, with the alternatives considered.
- [ ] Every collision between the console and the docs is resolved in a doc or named as an open question in the design.
- [ ] L1: the design names the Bash policy's allow and deny rules, and that a `PreToolUse` hook enforces them.
- [ ] L2: the design says where transcripts and session IDs live, and that none is committed.
- [ ] L3: the design has a failure-modes section covering each case in the lens.
- [ ] L5: the design says what Peter sees while a session runs, when a hook fails, and at hand-off.
- [ ] L7: the design shows how the in-flight items across repos and one item's session appear in Desktop.
- [ ] L8: each Desktop behaviour the design relies on cites the spike or the docs.
- [ ] L9: the design records that no credential is added and no cost beyond the subscription.
- [ ] L10: architecture §10, the requirements and CLAUDE.md carry the agreed edits.
- [ ] L11: invariant 5 is amended and invariant 6 is shown to hold.
- [ ] L12: the design says how several sessions run at once, and how a session moves between Desktop and the terminal.
- [ ] pl-gokul no longer says "auto-pull applies".
- [ ] `uv run pytest` passes, coverage gate included.

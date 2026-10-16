---
title: "Design 0003 and ADR 0009: the work console"
type: chore
status: Todo
estimate: 5
priority: P2
ordinal: 20600
lane: web
milestone: phase-2
blocked_by:
  - "pl-veles - Import gh-plan's open GitHub issues into .tracker/items, then close them"
---
### Task
Design a local web console that starts and finishes item worktrees, runs one Claude agent per item, and turns the commands handed over between steps into buttons. Today several worktrees, terminals and Claude sessions are hard to see at once, `worktask`'s editor hand-off is unreliable, and commits, `gh pc` and close scripts are copied into a terminal by hand.
- `docs/design/0003-work-console.md`, in the global design outline plus §6 to §8: page layout, server routes and the SSE stream, the agent session lifecycle, the Bash policy, session storage, the hand-off button, failure modes, the requirements it meets (§7), and the items that build it (§8).
- ADR 0009 *Work console*: the stack (FastAPI, Jinja, HTMX, SSE; no Node), agents hosted by the console through the Claude Agent SDK, and agent commit scope (own item branch only).
- The architecture, requirements and CLAUDE.md edits the ADR needs: architecture §6.1, §6.2, §6.3's Web UI row and invariants 5 and 6; a requirement for one view of every item in progress across repos; the CLAUDE.md boundary on commits.
- pl-gokul loses its stale "auto-pull applies" line.

### Guardrails
- No code: nothing under `src/` or `tests/` changes.
- Each doc edit is agreed in chat first, then made in place on the branch.
- Every existing requirement ID is kept.
- `plan:` commits go to `main` and nothing else does (invariant 2). Every push and `gh` write stays Peter's, in the console as a button he presses.
- No token or API key in any repo (G3). How agents authenticate is decided with Peter before the agent half of the design is written.
- Sample items and repos in the docs are synthetic.
- Out of scope: building any of the §8 items.

### Lenses
- [x] L1 Security: what an agent may run, enforced by a `PreToolUse` hook on Bash, not the permission callback
- [x] L2 Privacy and data: where agent transcripts and session IDs are stored
- [x] L3 Reliability and failure: agent crash, server restart, `worktask` failure, a rejected push
- [ ] L4 Performance and limits
- [x] L5 Observability: live output of `worktask` and each agent in the page
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: one page for every item in flight, across repos
- [ ] L8 Testability
- [x] L9 Operations and cost: agent auth and its cost (G3, I1); about 1 GiB of RAM per agent
- [x] L10 Docs impact: ADR 0009, architecture §6 and §10, requirements, CLAUDE.md
- [x] L11 Invariants: 5 (the only remote write) and 6 (which modules spawn processes) change or gain an exception
- [x] L12 Offline and concurrency: several agents at once, and the page and the terminal never driving one session together

### Done
- [ ] `docs/design/0003-work-console.md` exists, and its §5 answers every lens L1 to L12.
- [ ] Design §7 maps each requirement the console meets; §8 lists its items, each estimated 1, 2, 3 or 5.
- [ ] ADR 0009 is written in the repo's ADR shape, with the alternatives considered.
- [ ] Every collision between the console and the docs is resolved in a doc or named as an open question in the design.
- [ ] L1: the design names the Bash policy's allow and deny rules, and that a hook enforces them.
- [ ] L2: the design says where transcripts and session IDs live, and that none is committed.
- [ ] L3: the design has a failure-modes section covering each case in the lens.
- [ ] L5: the design says what the page shows while `worktask` and an agent run, and when either fails.
- [ ] L7: the design's page layout shows the in-progress list across repos and an item's page.
- [ ] L9: agent auth is decided with Peter and recorded, with its cost.
- [ ] L10: architecture §6 and §10, the requirements and CLAUDE.md carry the agreed edits.
- [ ] L11: each invariant the console touches is amended or shown to hold.
- [ ] L12: the design says how several agents run at once, and how a session moves between the page and the terminal.
- [ ] pl-gokul no longer says "auto-pull applies".
- [ ] `uv run pytest` passes, coverage gate included.

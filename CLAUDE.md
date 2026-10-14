# gh-plan — repo instructions

**GH Plan** is a file-native tracker: a local CLI (later a localhost web UI) over Markdown item
files committed in the repo each item belongs to. It does not use GitHub Issues; pull requests are
its one GitHub integration ([ADR 0008](docs/adr/0008-file-native-items.md)).

Read `docs/design/0001-phase-1.md` before writing code. `docs/architecture.md` is the
architecture, `docs/adr/` holds the decisions behind it, and `docs/requirements.md` is the spec.

## ⚠️ This repo inherits nothing

`gh-plan` lives at `~/programming/gh-plan`, outside the `~/programming/ms-security/` workspace, so
**no `CLAUDE.md`, `settings.json` or `.mcp.json` from that workspace reaches here.** That is the
verified config-resolution rule, not a guess: `CLAUDE.md` inherits from ancestor directories only,
and `settings.json` anchors to the launch directory. There is no ancestor `CLAUDE.md` above
`~/programming/`.

Everything this repo needs is therefore stated here or committed in `.claude/`.

## Hard rules

- **An AI is never an author; it is recorded as the tool that generated the work.** This follows
  the Linux kernel's rule for AI coding assistants
  ([coding-assistants](https://docs.kernel.org/process/coding-assistants.html)). No
  `Co-Authored-By`, `Signed-off-by`, `Claude-Session` or "Generated with" line may name an AI, in a
  commit, a PR description or a document. Peter is the sole author of record: he reviews,
  understands, signs and takes responsibility for every change. Every commit Claude makes ends with
  `Assisted-by: AGENT_NAME:MODEL_VERSION`, for example `Assisted-by: Claude:claude-opus-5-5`, which
  Claude Code adds through `attribution.commit` in `.claude/settings.json`. A `PreToolUse` hook
  enforces both halves: `.claude/hooks/no_ai_attribution.py`, exit 2 blocks. **Memory is context
  and can be ignored; a hook cannot.**
- **Never commit secrets.** No tokens, keys or connection strings. This tool authenticates by
  shelling out to `gh`, which is already authenticated — **that is a design requirement (`G3`), not
  a convenience.** Do not introduce a library that needs a PAT.
- **Never use real personal data** in fixtures, tests or examples. Synthetic only.
- **Branch, then squash.** Short-lived branches off `main`, squash-merged. Never commit straight to
  `main`, except for the tool's own `plan:` commits
  ([ADR 0008](docs/adr/0008-file-native-items.md)). Commit or push only when asked.
- **No speculative files.** Do not create a directory or file until something goes in it.

## Working agreement

- **Explain before doing.** State why a step exists before giving the command.
- **Peter runs the commands.** Hand him the command rather than executing it — except reads,
  inspections, running the test suite, and cleaning up your own mess.
- **Cite or flag.** A claim about GitHub's API behaviour gets a verified source or is marked 🔍
  unverified.
- **Verify against the API, not the docs, where they disagree.** This project has already found
  GitHub docs and GitHub behaviour differing — display-only project fields, and `gh` sub-issue
  support that was reported absent and is present.

## Design invariants: do not break these without changing the architecture

The authoritative list, with the reasons, is
[`docs/architecture.md` §10](docs/architecture.md#invariants). The two lists keep the same numbers.

1. **Git is the database. SQLite is a disposable index**, rebuilt by `plan reindex`.
2. **The default branch carries the current state.** Everything reaches it by PR, except `plan:` commits.
3. **A tool commit touches one item's `status` and `started`, plus `ready.yml`**, as `plan: start <id>` or `plan: stop <id>`.
4. **`started` is written once.** `plan stop` leaves it, and a later start keeps it.
5. **The only remote write is a `git push` of the tool's own commits.** Nothing goes through GitHub's API.
6. **`gh.py`, `git.py` and the `timekeeping/` adapters are the only modules that spawn a process or open a network connection.**
7. **Estimates are `Literal[1, 2, 3, 5]`.** 8 and 13 mean "split this" and are not representable.
8. **An item has at most one lane.**
9. **A parent with children has no estimate.**
10. **A baseline is written only by freeze.**
11. **Tracked time is read, never written.** The write that sets an item Done writes the `actual_time` snapshot.

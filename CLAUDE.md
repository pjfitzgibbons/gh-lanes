# gh-lanes — repo instructions

**GH Lanes** is a planning layer over GitHub Issues: a local CLI (later a localhost web UI) that
owns the planning fields, while GitHub Issues keeps owning identity, state, labels and
dependencies. It is **not** an issue tracker.

Read `docs/design/0001-phase-1.md` before writing code. `docs/architecture.md` is the
architecture, `docs/adr/` holds the decisions behind it, and `docs/requirements.md` is the spec.

## ⚠️ This repo inherits nothing

`gh-lanes` lives at `~/programming/gh-lanes`, outside the `~/programming/ms-security/` workspace, so
**no `CLAUDE.md`, `settings.json` or `.mcp.json` from that workspace reaches here.** That is the
verified config-resolution rule, not a guess: `CLAUDE.md` inherits from ancestor directories only,
and `settings.json` anchors to the launch directory. There is no ancestor `CLAUDE.md` above
`~/programming/`.

Everything this repo needs is therefore stated here or committed in `.claude/`.

## Hard rules

- **Never add `Co-Authored-By`, `Claude-Session`, "Generated with Claude Code", or any other AI
  attribution to a commit message, PR description, or document.** Peter is the sole author of
  record. He owns every decision and must be able to explain and defend it. Claude drafts; Peter
  reviews, understands, and signs. A `PreToolUse` hook enforces this —
  `.claude/hooks/no_ai_attribution.py`, wired by `.claude/settings.json`, exit 2 blocks. **Memory is
  context and can be ignored; a hook cannot.**
- **Never commit secrets.** No tokens, keys or connection strings. This tool authenticates by
  shelling out to `gh`, which is already authenticated — **that is a design requirement (`G3`), not
  a convenience.** Do not introduce a library that needs a PAT.
- **Never use real personal data** in fixtures, tests or examples. Synthetic only.
- **Branch, then squash.** Short-lived branches off `main`, squash-merged. Never commit straight to
  `main`. Commit or push only when asked.
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
[`docs/architecture.md` §12](docs/architecture.md#invariants).

1. **Git is the database. SQLite is a disposable index**, rebuilt by `lanes reindex`.
2. **Field ownership is disjoint.** The only write-back to GitHub is the `[N]` title prefix.
3. **`gh.py`, `git.py` and the `timekeeping/` adapters are the only modules that spawn a process or
   open a network connection.** Everything else stays pure and testable without a network.
4. **GitHub first, then the file.** Always choose the failure mode that repairs itself.
5. **Estimates are `Literal[1, 2, 3, 5]`.** 8 and 13 mean "split this" and are not representable.
6. **Pace GitHub mutations** by `write_pause_seconds` (default 3). The secondary rate limit counts them.

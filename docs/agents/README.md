# Specialist instructions for this repo

Each file here extends the global specialist of the same name (`~/.claude/agents/<specialist>.md`) with what is true only in this repo. Every specialist reads its file here before starting. Where the two conflict, the file here wins.

The convention, what belongs here and what stays global, is defined once in `~/.claude/specialists/README.md`. That is the canonical copy; this file only points to it.

<a id="agents-readme-rules"></a>

## 1. Rules for these files

- One file per specialist, named exactly as the specialist: `technical-writer.md`, not `writer.md`.
- Only what would be false in another repo. Do not restate the global rules.
- Never define a specialist in `.claude/agents/` here. A project agent with the same name replaces the global one completely.

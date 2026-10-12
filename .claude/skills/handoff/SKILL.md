---
name: handoff
description: End the current session cleanly - file durable learnings into their owning docs, snapshot session state to a handoff file, and output a verbatim copy-paste prompt for a fresh session. Use when the user says /handoff, "prepare for a new session", or wants to wrap up and continue in a new session.
---

# Handoff

When invoked:

1. **Inventory session state.** Collect: the task and its goal, what is done, what is in progress, decisions made this session, open questions, next steps, files touched.
2. **Map the project's doc structure.** Read project CLAUDE.md and list the doc folders it points at (plus obvious homes: `docs/`, `.planning/`, `System Development/`, README). Build a picture of which existing file owns which concern — planning, specs, architecture, verification, decisions, memory.
3. **File each item with its owner.** Route every inventory item by concern to the file that owns it: learnings about how the system works → specs/architecture doc; next steps → planning doc; test or verification results → verification doc; user preferences and durable facts → CLAUDE.md or memory per its rules. Update as many files as have matching owners. Only items with no owning doc remain for step 4.
4. **Write the handoff file.** Write what remains to `HANDOFF.md` in the project root: create it if missing, overwrite it if present — it is a snapshot of the latest handoff, never a log. Write it in the present tense, as the position the work is in now, not as a report of what this session did. Use the template below. When every item found an owner in step 3, still write `HANDOFF.md` with the Task, State, and Pointers sections so the new session has one entry point.
5. **Leave git alone.** Never commit, stage, or discard changes. If the working tree is dirty, list the uncommitted files in the handoff file and what each one holds.
6. **Emit the prompt.** The final message of the turn is ONLY a fenced code block containing the new-session prompt — no text before it, no text after it, no commentary, no caveats. Every open question and to-do already lives in the handoff file, so the prompt never carries warnings or checklists.

## HANDOFF.md template

```markdown
# Session Handoff — <YYYY-MM-DD>

## Task
<goal, 1-2 sentences>

## State
<where things stand now, present tense: what is working, what is half-built,
what is decided. Not what happened this session. Under 20 lines.>

## Next steps
1. <ordered, concrete>

## Open questions
- <question, and who/what can answer it>

## Uncommitted changes
<dirty files and what each holds; or "clean">

## Pointers
- <file or doc>: <why the new session needs it>
```

## New-session prompt template

```text
Continue: <task in one clause>. Read HANDOFF.md<, plus other updated docs if central to the next step,> for current state and open questions, then start with: <first next step>.
```

Keep the prompt under 5 lines. It points at the handoff file rather than restating it.

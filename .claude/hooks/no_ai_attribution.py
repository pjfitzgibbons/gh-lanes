#!/usr/bin/env python3
"""PreToolUse hook (matcher: Bash). Enforces the Linux kernel's rule for AI
assistance on git commits and PR descriptions.

An AI is never an author. Only the human who reviewed the change can sign it
off and take responsibility for it, so no Co-Authored-By, Signed-off-by or
"Generated with" line may name an AI. The AI is recorded as the tool that
generated the work, with an Assisted-by trailer, and every commit Claude makes
must carry one:

    Assisted-by: AGENT_NAME:MODEL_VERSION [TOOL1] [TOOL2]

Source: https://docs.kernel.org/process/coding-assistants.html

A CLAUDE.md rule says so; this hook enforces it. Context might be ignored;
enforcement cannot.

Claude Code sends the pending tool call as JSON on stdin:
    {"tool_name": "Bash", "cwd": "...", "tool_input": {"command": "..."}}

Exit 0 allows the call. Exit 2 blocks it and returns stderr to the model,
which then rewrites the message.
"""

import json
import re
import sys
from pathlib import Path

# A commit or PR verb counts only in command position: the start of a line, or
# right after ; && || | ( $(. Prose that merely *mentions* "git commit" (in a
# heredoc that edits a document, say) is not a commit and must pass.
COMMAND_POSITION = r"(?:^|[;&|(]\s*|\$\(\s*)"
GIT_GLOBAL_OPTIONS = r"(?:\s+-\S+(?:\s+[^-\s]\S*)?)*"  # -C <path>, -c k=v, --no-pager
GIT_COMMIT = COMMAND_POSITION + r"git" + GIT_GLOBAL_OPTIONS + r"\s+commit(?:\s|$)"
CHANGE_RECORD = re.compile(
    r"(?:" + GIT_COMMIT + r"|" + COMMAND_POSITION + r"gh\s+pr\s+(?:create|edit)(?:\s|$))",
    re.MULTILINE,
)
COMMIT = re.compile(GIT_COMMIT, re.MULTILINE)

# Markers of AI authorship. A Co-Authored-By or Signed-off-by naming a human is
# a legitimate record and does not match.
AI_AUTHORSHIP = re.compile(
    # [^\n"']* keeps each match inside one trailer, so a human's Co-Authored-By
    # beside an Assisted-by: Claude trailer on the same command line still passes.
    r"(?:co-authored-by|signed-off-by):[^\n\"']*(?:claude|anthropic)"
    r"|claude-session:"
    r"|generated with[^\n\"']*claude"
    r"|claude\.ai/code",
    re.IGNORECASE,
)

# The kernel's attribution trailer: an agent name and a model version.
ASSISTED_BY = re.compile(r"(?:^|[\s\"'])Assisted-by:\s*[A-Za-z][\w.-]*:[\w.-]+", re.MULTILINE)

# Commit options that keep an existing message instead of writing a new one.
REUSES_MESSAGE = re.compile(r"\s(?:--no-edit|-C|--reuse-message|--fixup|--squash)(?:[\s=]|$)")

# git commit -F <file> and gh pr --body-file <file> keep the message where the
# command string can't show it. Those files are read too.
MESSAGE_FILE = re.compile(r"(?:-F|--file|--body-file)[= ]+['\"]?([^\s'\"]+)")

BLOCKED_AUTHORSHIP = """\
BLOCKED: commit message or PR description names an AI as an author.
An AI never co-authors or signs off; only the human who reviewed the change does.
Remove the Co-Authored-By, Signed-off-by, Claude-Session or "Generated with" line,
record the AI as `Assisted-by: AGENT_NAME:MODEL_VERSION`, and retry.
"""

BLOCKED_MISSING = """\
BLOCKED: commit message has no Assisted-by trailer.
Every commit Claude makes records the AI as the tool that generated it, for example:
    Assisted-by: Claude:claude-opus-5-5
Add the trailer as the last line of the message and retry.
"""


def is_change_record(command: str) -> bool:
    """True if the command commits or writes a PR description."""
    return CHANGE_RECORD.search(command) is not None


def message_text(command: str, cwd: str = ".") -> str:
    """The command plus the contents of any message file it names."""
    text = command
    for match in MESSAGE_FILE.finditer(command):
        path = Path(match.group(1))
        if not path.is_absolute():
            path = Path(cwd) / path
        if path.is_file():
            text += "\n" + path.read_text(errors="replace")
    return text


def writes_new_commit_message(command: str) -> bool:
    """True if the command makes a commit with a message of its own."""
    match = COMMIT.search(command)
    if match is None:
        return False
    return REUSES_MESSAGE.search(command[match.end() - 1:]) is None


def violation(command: str, cwd: str = ".") -> str | None:
    """The whole rule. Returns the reason to block, or None to allow."""
    if not is_change_record(command):
        return None
    text = message_text(command, cwd)
    if AI_AUTHORSHIP.search(text):
        return BLOCKED_AUTHORSHIP
    if writes_new_commit_message(command) and not ASSISTED_BY.search(text):
        return BLOCKED_MISSING
    return None


def should_block(command: str, cwd: str = ".") -> bool:
    return violation(command, cwd) is not None


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        # Hand-check from a shell, no JSON needed:
        #   python3 no_ai_attribution.py --check 'git commit -m "..."'
        command, cwd = " ".join(sys.argv[2:]), "."
    else:
        payload = json.load(sys.stdin)
        command = (payload.get("tool_input") or {}).get("command") or ""
        cwd = payload.get("cwd") or "."
    reason = violation(command, cwd)
    if reason:
        sys.stderr.write(reason)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

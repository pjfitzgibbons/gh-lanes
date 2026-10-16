"""Move a repo's GitHub issues into item files, once (ADR 0008; pl-veles).

The importer makes no GitHub call. It reads issues Peter saved with `gh` (DUMP_COMMAND), and a
triage file saying which to import and which to close. It writes the item files, and prints the
closes as a shell script for Peter to run, paced, once the items have merged. It is dry unless
`--apply` is given: the values are the tool's inference from the issue text.

The Planning block at the end of an issue body moves into the front matter, and the rest of the body
is kept as it is; it is rewritten to the item outline when the item is picked up.

    uv run python -m ghplan.importer ISSUES.jsonl TRIAGE.yml [--apply] [--close-script PATH]
"""

import argparse
import json
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ghplan.config import Tracker, discover
from ghplan.ids import ID, draw_word, item_ids, load_blocklist
from ghplan.model import Item
from ghplan.store import FileFormatError, load_yaml, write_markdown

DUMP_COMMAND = (
    "gh api graphql --paginate -F owner=OWNER -F name=REPO --jq '.data.repository.issues.nodes[]' "
    "-f query='query($owner:String!,$name:String!,$endCursor:String){repository(owner:$owner,name:$name)"
    "{issues(first:50,states:OPEN,after:$endCursor){pageInfo{hasNextPage endCursor} nodes{number title "
    "body labels(first:20){nodes{name}} parent{number} blockedBy(first:50){nodes{number}}}}}}'"
)
PAUSE_SECONDS = 3  # between closes: each is two writes, under GitHub's secondary rate limit
LETTER_BANDS = {"A": 10, "U": 30}  # a lettered backlog ID sorts after every phase, as #25 mapped it

_ESTIMATE_PREFIX = re.compile(r"\[(\d+)\]\s*")
_PLANNING = re.compile(r"^#{2,3} Planning[ \t]*\n.*?(?=^#{1,3} |\Z)", re.M | re.S)
_PLANNING_FIELD = re.compile(r"^- ([\w ]+): (.+?)\s*$", re.M)
_BACKLOG_ID = re.compile(r"(?P<band>\d+|[A-Z])\.(?P<n>\d+)")


class ImportFailed(Exception):
    """The issues or the triage can't be imported as they stand. The message says why."""


class Close(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    reason: Literal["completed", "not planned"] = "not planned"
    comment: str


class Triage(BaseModel):
    """Every open issue, sorted: imported, or closed with a comment."""

    model_config = ConfigDict(extra="forbid", strict=True)

    repo: str  # owner/name, for the close script and the links in its comments
    branch: str = "main"  # where the item files will be once their PR merges
    import_: list[int] = Field(default=[], alias="import")
    close: dict[int, Close] = {}


@dataclass
class Issue:
    number: int
    title: str
    body: str
    labels: list[str]
    parent: int | None
    blocked_by: list[int]


@dataclass
class Planned:
    """One issue's item: its new ID, the file's model and body, and what was left behind."""

    issue: Issue
    id: str
    item: Item
    body: str
    dropped: list[str] = field(default_factory=list)


@dataclass
class Plan:
    items: list[Planned]
    closes: dict[int, tuple[Issue, Close]]


def read_issues(path: Path) -> list[Issue]:
    """The issues `gh` saved: one JSON object a line, as DUMP_COMMAND writes them, or one array."""
    text = path.read_text(encoding="utf-8").strip()
    try:
        nodes = json.loads(text) if text.startswith("[") else [json.loads(l) for l in text.splitlines()]
    except json.JSONDecodeError as e:
        raise ImportFailed(f"{path}: not JSON lines or a JSON array: {e}") from e
    return [
        Issue(
            number=n["number"],
            title=n["title"],
            body=n.get("body") or "",
            labels=[label["name"] for label in (n.get("labels") or {}).get("nodes", [])],
            parent=(n.get("parent") or {}).get("number"),
            blocked_by=[b["number"] for b in (n.get("blockedBy") or {}).get("nodes", [])],
        )
        for n in nodes
    ]


def planning(body: str) -> dict[str, str]:
    """The body's Planning block, `- Key: value` lines, as a mapping. Empty if it has none."""
    m = _PLANNING.search(body)
    return dict(_PLANNING_FIELD.findall(m.group(0))) if m else {}


def strip_planning(body: str) -> str:
    """The body without its Planning block, whose values the front matter now holds."""
    return _PLANNING.sub("", body).strip() + "\n"


def ordinal(backlog_id: str | None) -> int | None:
    """A backlog ID as a sparse ordinal: `1.4` → 10400, `A.1` → 100100, `U.3` → 300300."""
    if not backlog_id:
        return None
    m = _BACKLOG_ID.fullmatch(backlog_id.strip())
    if not m:
        raise ImportFailed(f"backlog ID {backlog_id!r} is not <phase>.<n> or <letter>.<n>")
    band = m["band"]
    if band.isdigit():
        major = int(band)
    elif band in LETTER_BANDS:
        major = LETTER_BANDS[band]
    else:
        raise ImportFailed(f"backlog ID {backlog_id!r}: no ordinal band for {band!r}")
    return major * 10000 + int(m["n"]) * 100


def split_title(title: str) -> tuple[str, int | None]:
    """An issue title's `[N] ` estimate prefix, taken off: the title, then N."""
    m = _ESTIMATE_PREFIX.match(title)
    return (title[m.end() :], int(m[1])) if m else (title, None)


def _milestone(value: str | None) -> str | None:
    # "— (Icebox)" and any other non-slug means no milestone: the item is iced.
    return value if value and re.fullmatch(r"[a-z0-9-]+", value) else None


def plan(issues: list[Issue], triage: Triage, tracker: Tracker, rng: random.Random) -> Plan:
    """Sort the issues as the triage says and build each imported one's item. Writes nothing."""
    by_number = {i.number: i for i in issues}
    _check_triage(by_number, triage)

    taken = {m["word"] for id in item_ids(tracker.tracker_dir) if (m := ID.fullmatch(id))}
    blocklist = load_blocklist()
    ids: dict[int, str] = {}
    for number in sorted(triage.import_):
        word = draw_word(rng, taken, blocklist)
        taken.add(word)
        ids[number] = f"{tracker.config.prefix}-{word}"

    milestones = {p.stem for p in tracker.milestone_files()}
    titles = {n: split_title(by_number[n].title)[0] for n in ids}
    items = [
        _item(by_number[n], ids, titles, tracker, milestones) for n in sorted(triage.import_)
    ]
    closes = {n: (by_number[n], c) for n, c in sorted(triage.close.items())}
    return Plan(items=items, closes=closes)


def _check_triage(by_number: dict[int, Issue], triage: Triage) -> None:
    triaged = set(triage.import_) | set(triage.close)
    problems = []
    if both := sorted(set(triage.import_) & set(triage.close)):
        problems.append(f"both imported and closed: {_numbers(both)}")
    if unknown := sorted(triaged - set(by_number)):
        problems.append(f"in the triage but not among the open issues: {_numbers(unknown)}")
    if missing := sorted(set(by_number) - triaged):
        problems.append(f"open but not in the triage: {_numbers(missing)}")
    if problems:
        raise ImportFailed("the triage does not sort every open issue once:\n  " + "\n  ".join(problems))


def _numbers(numbers: list[int]) -> str:
    return ", ".join(f"#{n}" for n in numbers)


def _item(
    issue: Issue, ids: dict[int, str], titles: dict[int, str], tracker: Tracker, milestones: set[str]
) -> Planned:
    fields = planning(issue.body)
    title, estimate = split_title(issue.title)
    lane = fields.get("Lane")
    milestone = _milestone(fields.get("Milestone"))
    where = f"#{issue.number}"
    if lane is not None and lane not in tracker.config.lanes:
        raise ImportFailed(f"{where}: lane {lane!r} is not in config.yml's lanes")
    if milestone is not None and milestone not in milestones:
        raise ImportFailed(f"{where}: milestone {milestone!r} has no file in .tracker/milestones/")

    dropped = []
    blocked_by = []
    for n in issue.blocked_by:
        if n in ids:
            blocked_by.append(f"{ids[n]} - {titles[n]}")
        else:
            dropped.append(f"blocked by #{n}: closed, not imported")
    parent = ids.get(issue.parent) if issue.parent else None
    if issue.parent and not parent:
        dropped.append(f"parent #{issue.parent}: closed, not imported")

    try:
        item = Item.model_validate(
            {
                "title": title,
                "type": "bug" if "bug" in issue.labels else "feat",
                "status": "Todo" if milestone else "Icebox",
                "estimate": estimate,
                "ordinal": ordinal(fields.get("Backlog ID")),
                "lane": lane,
                "milestone": milestone,
                "labels": issue.labels,
                "parent": parent,
                "blocked_by": blocked_by,
            }
        )
    except ValueError as e:
        raise ImportFailed(f"{where}: {e}") from e
    return Planned(issue, ids[issue.number], item, strip_planning(issue.body), dropped)


def describe(p: Plan, tracker: Tracker) -> str:
    """What `--apply` would write and what the close script would close, one line each."""
    out = [f"Import {len(p.items)} issues:"]
    for planned in p.items:
        i = planned.item
        path = (tracker.tracker_dir / "items" / f"{planned.id}.md").relative_to(tracker.root)
        out.append(
            f"  write {path}  #{planned.issue.number}  [{i.estimate or '-'}] {i.lane or '-'} "
            f"{i.milestone or 'Icebox'} ordinal {i.ordinal}  {i.title}"
        )
        out += [f"      blocked by {b}" for b in i.blocked_by]
        out += [f"      dropped: {d}" for d in planned.dropped]
    out.append(f"Close {len(p.items) + len(p.closes)} issues, once the item files are on the default branch:")
    for number, comment, reason in _closes(p, None):
        out.append(f"  close #{number} as {reason}: {comment}")
    return "\n".join(out) + "\n"


def _closes(p: Plan, triage: Triage | None) -> list[tuple[int, str, str]]:
    def link(id: str) -> str:
        path = f".tracker/items/{id}.md"
        if triage is None:
            return path
        return f"[{path}](https://github.com/{triage.repo}/blob/{triage.branch}/{path})"

    rows = [
        (
            planned.issue.number,
            f"Moved to {planned.id}, {link(planned.id)}: gh-plan tracks its work in item files now (ADR 0008).",
            "not planned",
        )
        for planned in p.items
    ]
    rows += [(n, c.comment, c.reason) for n, (_, c) in p.closes.items()]
    return sorted(rows)


def close_script(p: Plan, triage: Triage) -> str:
    """A shell script that closes every issue in the plan, pausing between closes."""
    rows = _closes(p, triage)
    lines = [
        "#!/bin/sh",
        f"# Closes {len(rows)} issues in {triage.repo} (pl-veles). Run it after the items merge.",
        "set -eu",
    ]
    for k, (number, comment, reason) in enumerate(rows):
        if k:
            lines.append(f"sleep {PAUSE_SECONDS}")
        lines.append(
            f"gh issue close {number} -R {_sh(triage.repo)} --reason {_sh(reason)} --comment {_sh(comment)}"
        )
    return "\n".join(lines) + "\n"


def _sh(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


def apply(p: Plan, tracker: Tracker) -> list[Path]:
    """Write each item file. Refuses, writing nothing, if any of them exists already."""
    paths = [tracker.tracker_dir / "items" / f"{planned.id}.md" for planned in p.items]
    if existing := [str(path) for path in paths if path.exists()]:
        raise ImportFailed(f"would overwrite {', '.join(existing)}")
    for path, planned in zip(paths, p.items, strict=True):
        write_markdown(path, planned.item, planned.body)
    return paths


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ghplan.importer",
        description="Import open GitHub issues into .tracker/items. Dry unless --apply.",
        epilog=f"Save the issues with:\n  {DUMP_COMMAND} > issues.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("issues", type=Path, help="the issues gh saved, as JSON lines")
    parser.add_argument("triage", type=Path, help="YAML: repo, import (numbers), close (number: comment)")
    parser.add_argument("--apply", action="store_true", help="write the item files")
    parser.add_argument("--close-script", type=Path, help="write the close script here")
    parser.add_argument("--seed", default="pl-veles", help="seeds the ID draw, so a dry run shows the IDs --apply writes")
    args = parser.parse_args(argv)

    try:
        tracker = discover(cwd)
        triage = load_yaml(args.triage, Triage)
        p = plan(read_issues(args.issues), triage, tracker, random.Random(args.seed))
        sys.stdout.write(describe(p, tracker))
        if args.close_script:
            args.close_script.write_text(close_script(p, triage), encoding="utf-8")
            args.close_script.chmod(0o755)
            print(f"Wrote the close script to {args.close_script}.")
        if args.apply:
            written = apply(p, tracker)
            print(f"Wrote {len(written)} item files.")
        else:
            print("Dry run: nothing written. Add --apply to write the item files.")
    except (ImportFailed, FileFormatError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

"""importer.py: moving open GitHub issues into item files, once (pl-veles)."""

import json
import random
import subprocess
from pathlib import Path

import pytest

from ghplan import importer
from ghplan.config import discover
from ghplan.importer import (
    Close,
    ImportFailed,
    Issue,
    Triage,
    close_script,
    main,
    ordinal,
    plan,
    planning,
    read_issues,
    split_title,
    strip_planning,
)
from ghplan.model import Item
from ghplan.store import load_markdown, load_yaml

CONFIG = """\
prefix: wa
points_per_week: 10
project_start: 2026-01-05
lanes: [api, web]
"""
MILESTONE = "---\ntitle: Beta\norder: 100\n---\nEvery item in this milestone is Done.\n"
EXISTING = "---\ntitle: Already here\ntype: feat\n---\n"


def body(text: str, backlog: str, estimate: int, lane: str, milestone: str) -> str:
    return (
        f"{text}\n\n## Planning\n\n- Backlog ID: {backlog}\n- Estimate: {estimate}\n"
        f"- Lane: {lane}\n- Milestone: {milestone}\n"
    )


# Synthetic issues in the shape DUMP_COMMAND saves them.
NODES = [
    {
        "number": 3,
        "title": "[3] Retry failed webhook deliveries",
        "body": body("Retry with backoff.", "1.4", 3, "api", "beta"),
        "labels": {"nodes": []},
        "parent": None,
        "blockedBy": {"nodes": [{"number": 7}, {"number": 1}]},
    },
    {
        "number": 7,
        "title": "[2] Sign webhook payloads",
        "body": "### Summary\nSign them.\n\n### Planning\n- Backlog ID: A.1\n- Estimate: 2\n- Lane: api\n- Milestone: — (Icebox)\n",
        "labels": {"nodes": [{"name": "bug"}]},
        "parent": None,
        "blockedBy": {"nodes": []},
    },
    {
        "number": 8,
        "title": "[1] Show delivery status on the board",
        "body": body("A column.", "U.3", 1, "web", "beta"),
        "labels": {"nodes": [{"name": "ui"}]},
        "parent": {"number": 3},
        "blockedBy": {"nodes": []},
    },
    {
        "number": 9,
        "title": "Pull deliveries from the old queue",
        "body": None,
        "labels": {"nodes": []},
        "parent": {"number": 5},
        "blockedBy": {"nodes": []},
    },
    {
        "number": 5,
        "title": "[1] Mirror titles to the old queue",
        "body": "Gone.",
        "labels": None,
        "parent": None,
        "blockedBy": None,
    },
]
TRIAGE = """\
repo: example-org/web-app
import: [3, 7, 8, 9]
close:
  5: {comment: "Superseded: there's no old queue."}
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    tracker = tmp_path / ".tracker"
    (tracker / "items").mkdir(parents=True)
    (tracker / "milestones").mkdir()
    (tracker / "config.yml").write_text(CONFIG, encoding="utf-8")
    (tracker / "milestones" / "beta.md").write_text(MILESTONE, encoding="utf-8")
    (tracker / "items" / "wa-tunep.md").write_text(EXISTING, encoding="utf-8")
    (tmp_path / "issues.jsonl").write_text("\n".join(json.dumps(n) for n in NODES), encoding="utf-8")
    (tmp_path / "triage.yml").write_text(TRIAGE, encoding="utf-8")
    return tmp_path


def run(repo: Path, *args: str) -> int:
    return main([str(repo / "issues.jsonl"), str(repo / "triage.yml"), *args], cwd=repo)


def items(repo: Path) -> dict[str, tuple[Item, str]]:
    """The imported items, by title: the existing item file is left out."""
    loaded = [load_markdown(p, Item) for p in sorted((repo / ".tracker" / "items").glob("*.md"))]
    return {item.title: (item, text) for item, text in loaded if item.title != "Already here"}


def the_plan(repo: Path, triage: str = TRIAGE, seed: str = "s") -> importer.Plan:
    (repo / "triage.yml").write_text(triage, encoding="utf-8")
    return plan(
        read_issues(repo / "issues.jsonl"),
        load_yaml(repo / "triage.yml", Triage),
        discover(repo),
        random.Random(seed),
    )


def test_a_dry_run_lists_every_write_and_close_and_writes_nothing(repo, capsys):
    assert run(repo) == 0
    out = capsys.readouterr().out
    assert out.count("  write .tracker/items/wa-") == 4
    assert out.count("  close #") == 5
    assert "close #5 as not planned: Superseded: there's no old queue." in out
    assert "dropped: blocked by #1: closed, not imported" in out
    assert "dropped: parent #5: closed, not imported" in out
    assert "Dry run: nothing written" in out
    assert sorted(p.name for p in (repo / ".tracker" / "items").iterdir()) == ["wa-tunep.md"]


def test_apply_writes_the_ids_the_dry_run_showed(repo, capsys):
    run(repo)
    dry = capsys.readouterr().out
    assert run(repo, "--apply") == 0
    assert "Wrote 4 item files." in capsys.readouterr().out
    for path in (repo / ".tracker" / "items").glob("wa-*.md"):
        if path.stem != "wa-tunep":
            assert f"write .tracker/items/{path.name}" in dry


def test_fields_come_from_the_title_labels_and_planning_block(repo):
    run(repo, "--apply")
    got = items(repo)
    retry, text = got["Retry failed webhook deliveries"]
    assert (retry.type, retry.status, retry.estimate, retry.priority) == ("feat", "Todo", 3, "P2")
    assert (retry.ordinal, retry.lane, retry.milestone) == (10400, "api", "beta")
    assert text == "Retry with backoff.\n"

    sign, text = got["Sign webhook payloads"]
    assert (sign.type, sign.status, sign.milestone, sign.ordinal) == ("bug", "Icebox", None, 100100)
    assert sign.labels == ["bug"]
    assert text == "### Summary\nSign them.\n"

    board, _ = got["Show delivery status on the board"]
    assert (board.ordinal, board.labels) == (300300, ["ui"])

    pull, text = got["Pull deliveries from the old queue"]
    assert (pull.estimate, pull.ordinal, pull.lane, pull.parent) == (None, None, None, None)
    assert text == "\n"


def test_edges_between_imported_issues_name_the_new_ids(repo):
    run(repo, "--apply")
    got = items(repo)
    ids = {
        load_markdown(path, Item)[0].title: path.stem for path in (repo / ".tracker" / "items").glob("*.md")
    }
    retry, _ = got["Retry failed webhook deliveries"]
    assert retry.blocked_by == [f"{ids['Sign webhook payloads']} - Sign webhook payloads"]
    board, _ = got["Show delivery status on the board"]
    assert board.parent == ids["Retry failed webhook deliveries"]


def test_drawn_ids_avoid_existing_files_and_each_other(repo):
    p = the_plan(repo)
    ids = [planned.id for planned in p.items]
    assert len(set(ids)) == len(ids) == 4
    assert "wa-tunep" not in ids
    assert all(id.startswith("wa-") for id in ids)


def test_apply_refuses_to_overwrite_and_writes_nothing(repo):
    # The draw avoids taken IDs, so a clash means a file appeared between the plan and the apply.
    p = the_plan(repo)
    clash = repo / ".tracker" / "items" / f"{p.items[-1].id}.md"
    clash.write_text(EXISTING, encoding="utf-8")
    with pytest.raises(ImportFailed, match="would overwrite"):
        importer.apply(p, discover(repo))
    assert len(list((repo / ".tracker" / "items").glob("*.md"))) == 2


def test_the_close_script_pauses_between_closes_and_links_each_item(repo, capsys):
    script = repo / "close.sh"
    assert run(repo, "--close-script", str(script)) == 0
    text = script.read_text()
    lines = text.splitlines()
    assert lines[0] == "#!/bin/sh" and "set -eu" in lines
    closes = [line for line in lines if line.startswith("gh issue close")]
    assert len(closes) == 5
    assert text.count(f"sleep {importer.PAUSE_SECONDS}") == 4
    assert "https://github.com/example-org/web-app/blob/main/.tracker/items/wa-" in text
    assert script.stat().st_mode & 0o111
    subprocess.run(["sh", "-n", str(script)], check=True)


def test_the_close_script_quotes_for_the_shell(tmp_path):
    triage = Triage.model_validate({"repo": "o/r", "close": {1: {"comment": "it's $HOME `x`"}}})
    issue = Issue(1, "t", "", [], None, [])
    script = close_script(importer.Plan(items=[], closes={1: (issue, triage.close[1])}), triage)
    path = tmp_path / "s.sh"
    path.write_text(script.replace("gh issue close", "printf '%s\\n'"))
    out = subprocess.run(["sh", str(path)], capture_output=True, text=True, check=True).stdout
    assert "it's $HOME `x`" in out


def test_a_close_can_be_completed():
    assert Close.model_validate({"reason": "completed", "comment": "Done elsewhere."}).reason == "completed"
    with pytest.raises(ValueError):
        Close.model_validate({"reason": "wontfix", "comment": "x"})


@pytest.mark.parametrize(
    ("triage", "message"),
    [
        ("repo: o/r\nimport: [3, 7, 8, 9, 5]\nclose:\n  5: {comment: x}\n", "both imported and closed: #5"),
        ("repo: o/r\nimport: [3, 7, 8, 9, 5, 42]\n", "not among the open issues: #42"),
        ("repo: o/r\nimport: [3, 7]\n", "open but not in the triage: #5, #8, #9"),
    ],
)
def test_the_triage_sorts_every_open_issue_once(repo, capsys, triage, message):
    (repo / "triage.yml").write_text(triage, encoding="utf-8")
    assert run(repo) == 1
    assert message in capsys.readouterr().err


def test_a_lane_the_config_lacks_is_refused(repo, capsys):
    NODES_BAD = [dict(NODES[0], body=body("x", "1.1", 3, "mobile", "beta"))]
    (repo / "issues.jsonl").write_text(json.dumps(NODES_BAD), encoding="utf-8")
    (repo / "triage.yml").write_text("repo: o/r\nimport: [3]\n", encoding="utf-8")
    assert run(repo) == 1
    assert "#3: lane 'mobile' is not in config.yml's lanes" in capsys.readouterr().err


def test_a_milestone_without_a_file_is_refused(repo, capsys):
    (repo / "issues.jsonl").write_text(json.dumps([dict(NODES[0], body=body("x", "1.1", 3, "api", "gamma"))]))
    (repo / "triage.yml").write_text("repo: o/r\nimport: [3]\n", encoding="utf-8")
    assert run(repo) == 1
    assert "#3: milestone 'gamma' has no file" in capsys.readouterr().err


def test_an_estimate_the_schema_refuses_names_the_issue(repo, capsys):
    (repo / "issues.jsonl").write_text(json.dumps([dict(NODES[0], title="[8] Too big", blockedBy=None)]))
    (repo / "triage.yml").write_text("repo: o/r\nimport: [3]\n", encoding="utf-8")
    assert run(repo) == 1
    assert "#3: " in capsys.readouterr().err


def test_issues_that_are_not_json_are_refused(repo, capsys):
    (repo / "issues.jsonl").write_text("{not json", encoding="utf-8")
    assert run(repo) == 1
    assert "not JSON lines or a JSON array" in capsys.readouterr().err


def test_a_missing_triage_file_is_reported(repo, capsys):
    (repo / "triage.yml").unlink()
    assert run(repo) == 1
    assert "triage.yml" in capsys.readouterr().err


def test_planning_and_strip_planning():
    text = "Intro.\n\n### Planning\n- Lane: api\n- Estimate: 2\n\n### After\nKept.\n"
    assert planning(text) == {"Lane": "api", "Estimate": "2"}
    assert strip_planning(text) == "Intro.\n\n### After\nKept.\n"
    assert planning("No block.") == {}
    assert strip_planning("No block.") == "No block.\n"


@pytest.mark.parametrize(
    ("backlog", "expected"),
    [("1.4", 10400), ("0.1", 100), ("3.13", 31300), ("A.1", 100100), ("U.3", 300300), (None, None), ("", None)],
)
def test_ordinal(backlog, expected):
    assert ordinal(backlog) == expected


@pytest.mark.parametrize(("backlog", "message"), [("1.x", "is not"), ("Q.1", "no ordinal band for 'Q'")])
def test_ordinal_refuses(backlog, message):
    with pytest.raises(ImportFailed, match=message):
        ordinal(backlog)


def test_split_title():
    assert split_title("[3] Retry") == ("Retry", 3)
    assert split_title("Retry [3]") == ("Retry [3]", None)

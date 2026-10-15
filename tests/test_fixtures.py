"""The committed fixture trees: they load with the models, and the broken ones cover design §9.

Every later module tests against these trees instead of the network, so a fixture that drifted
from the schema, from gh's output shape or from the rule table would mislead every test after it.
"""

import json
import re
from pathlib import Path

import pytest

# The trees are in the JSON layout, which the schemas no longer read; pl-nahuj converts them.
pytest.skip("the fixture trees convert to YAML and Markdown with pl-nahuj", allow_module_level=True)

from pydantic import ValidationError  # noqa: E402

from ghplan.config import Config, load  # noqa: E402
from ghplan.model import Item, Milestone, dumps, read_json  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
VALID = FIXTURES / "valid" / "web-app"
BROKEN = FIXTURES / "broken"
DESIGN = Path(__file__).parents[1] / "docs" / "design" / "0001-phase-1.md"

# Each broken tree, and the design 0001 §9 rule it trips.
RULES = {
    "estimate-not-allowed": "estimate in {1,2,3,5}",
    "parent-with-estimate": "parent with children has no estimate",
    "lane-not-configured": "`lane` in `config.lanes`",
    "blocked-by-cycle": "no cycle in the pulled blocked-by graph",
    "blocker-outside-repos": "blocker is in a configured repo",
    "blocked-by-other-milestone": "blocked-by is intra-milestone",
    "milestone-absent-not-icebox": "milestone absent ⟺ status Icebox",
    "status-not-in-schema": "item file matches the schema",
    "milestone-file-missing": "item `milestone` names a milestone file",
    "milestone-order-duplicate": "milestone `order` unique",
    "done-but-open": "status Done ⟺ issue closed",
    "blocked-without-blocker": "stored Blocked agrees with blocked-by",
    "ordinal-duplicate": "`ordinal` unique within a lane",
    "untracked-issue": "every open issue has an item",
    "orphan-item": "item resolves to a live issue",
    "title-estimate-mismatch": "title `[N]` matches estimate",
    "needs-triage": "estimate and lane present",
}
# Trees whose item is rejected by the schema itself, before any rule runs.
SCHEMA_TREES = {"estimate-not-allowed", "status-not-in-schema"}

# `gh issue list --json` with design §10's fields, as gh 2.102.0 returns them.
ISSUE_KEYS = {"blockedBy", "closedAt", "id", "labels", "number", "parent", "state",
              "stateReason", "subIssuesSummary", "title"}
REF_KEYS = {"id", "number", "state", "title", "url"}  # a blockedBy node, and parent
LABEL_KEYS = {"color", "description", "id", "name"}
SUMMARY_KEYS = {"completed", "percentCompleted", "total"}

def trees():
    return [VALID, *sorted(p for p in BROKEN.iterdir() if p.is_dir())]


def item_files(root):
    return sorted((root / ".tracker" / "items").glob("*/*.json"))


def milestone_files(root):
    return sorted((root / ".tracker" / "milestones").glob("*.json"))


def gh_rows(root):
    """The recorded pull, where a real pull caches it: `.tracker/.cache/gh/<repo>.json`."""
    cache = root / ".tracker" / ".cache" / "gh"
    return {p.stem: json.loads(p.read_text()) for p in sorted(cache.glob("*.json"))}


def section_9_rules():
    """The rule column of design §9's table, for the rows that have a message."""
    text = DESIGN.read_text(encoding="utf-8")
    table = text.split('<a id="validation"></a>')[1].split("<a id=")[0]
    rows = re.findall(r"^\| (.+?) \| (ERROR|WARN) \| (.+?) \|$", table, re.M)
    return {rule for rule, _, message in rows if message != "—"}


# ------------------------------------------------------------------ valid/


def test_valid_config_loads():
    config = load(VALID)
    assert set(config.repos) == {"web-app", "billing-api"}


@pytest.mark.parametrize("path", item_files(VALID), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_valid_items_load(path):
    Item.model_validate(read_json(path))


@pytest.mark.parametrize("path", milestone_files(VALID), ids=lambda p: p.name)
def test_valid_milestones_load(path):
    Milestone.model_validate(read_json(path), context={"stem": path.stem})


def test_valid_covers_what_the_ticket_lists():
    items = [Item.model_validate(read_json(p)) for p in item_files(VALID)]
    assert {i.status for i in items} == {"Icebox", "Todo", "In Progress", "Blocked", "Done"}
    assert any(i.draft for i in items)
    assert any(i.baseline for i in items)
    issues = [r for rows in gh_rows(VALID).values() for r in rows]
    # web-app#6 is the needs-triage item. #7 has no estimate either, but as a parent.
    triage = next(i for i in items if (i.repo, i.issue) == ("web-app", 6))
    assert triage.estimate is None and triage.status not in ("Icebox", "Done")
    six = next(r for r in gh_rows(VALID)["web-app"] if r["number"] == 6)
    assert six["subIssuesSummary"]["total"] == 0
    assert any(r["subIssuesSummary"]["total"] for r in issues)
    assert {r["stateReason"] for r in issues} == {"", "COMPLETED", "NOT_PLANNED"}
    orders = [Milestone.model_validate(read_json(p)).order
              for p in milestone_files(VALID)]
    assert len(orders) == 2 and len(set(orders)) == 2


def test_valid_items_match_their_issues():
    """Every non-draft item is in its repo's recorded output, under the same node id."""
    by_repo = {repo: {r["number"]: r for r in rows} for repo, rows in gh_rows(VALID).items()}
    for path in item_files(VALID):
        item = Item.model_validate(read_json(path))
        if item.draft:
            continue
        assert path.parent.name == item.repo and path.stem == str(item.issue)
        assert by_repo[item.repo][item.issue]["id"] == item.node_id


# ------------------------------------------------------------------ broken/


def test_every_broken_tree_names_one_section_9_rule():
    dirs = {p.name for p in BROKEN.iterdir() if p.is_dir()}
    assert dirs == set(RULES)


@pytest.mark.xfail(strict=True, reason="design §9 is file-native; the trees convert with pl-nahuj")
def test_every_section_9_rule_with_a_message_has_a_tree():
    assert set(RULES.values()) == section_9_rules()


@pytest.mark.parametrize("name", sorted(RULES))
def test_broken_tree_loads_except_its_schema_fault(name):
    """Only the schema trees fail to load, so every other tree trips a rule, not the schema."""
    root = BROKEN / name
    load(root)
    for path in milestone_files(root):
        Milestone.model_validate(read_json(path), context={"stem": path.stem})
    failures = []
    for path in item_files(root):
        try:
            Item.model_validate(read_json(path))
        except ValidationError:
            failures.append(path.name)
    assert bool(failures) == (name in SCHEMA_TREES)


# ------------------------------------------------------------------ file format


def test_no_yaml_is_left():
    assert list(FIXTURES.rglob("*.yml")) == []


@pytest.mark.parametrize("root", trees(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_every_tracker_file_is_canonical(root):
    """Design 0001 *File format*: re-dumping a file reproduces it byte for byte.

    A file the schema rejects can't be re-dumped through its model, so its layout and key order are
    checked instead, and an item must still carry the defaults every item file is written with.
    """
    config = root / ".tracker" / "config.json"
    files = [(config, Config, {}), *((p, Item, {}) for p in item_files(root)),
             *((p, Milestone, {"stem": p.stem}) for p in milestone_files(root))]
    for path, model, context in files:
        text = path.read_bytes().decode("utf-8")
        data = json.loads(text)
        assert text == json.dumps(data, indent=2, ensure_ascii=False) + "\n", path
        try:
            parsed = model.model_validate(data, context=context)
        except ValidationError:
            assert root.name in SCHEMA_TREES, path
            fields = list(model.model_fields)
            assert list(data) == sorted(data, key=fields.index), path
            assert model is not Item or {"draft", "priority", "status"} <= set(data), path
            continue
        assert dumps(parsed) == text, path


# ------------------------------------------------------------------ recorded gh output


@pytest.mark.parametrize("root", trees(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_recorded_output_has_gh_2_102_shape(root):
    for repo, rows in gh_rows(root).items():
        numbers = [r["number"] for r in rows]
        assert numbers == sorted(numbers, reverse=True), f"{repo}: gh lists newest first"
        for r in rows:
            assert set(r) == ISSUE_KEYS
            assert set(r["blockedBy"]) == {"nodes", "totalCount"}
            assert r["blockedBy"]["totalCount"] == len(r["blockedBy"]["nodes"])
            assert all(set(n) == REF_KEYS for n in r["blockedBy"]["nodes"])
            assert r["parent"] is None or set(r["parent"]) == REF_KEYS
            assert all(set(label) == LABEL_KEYS for label in r["labels"])
            assert set(r["subIssuesSummary"]) == SUMMARY_KEYS
            is_open = r["state"] == "OPEN"
            assert (r["stateReason"] == "") == is_open
            assert (r["closedAt"] is None) == is_open


@pytest.mark.parametrize("root", trees(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_each_repo_has_a_recording_and_no_tracker_gitignore(root):
    """A real tracker's .gitignore ignores .cache/, which would drop these recordings from git."""
    assert set(gh_rows(root)) == set(load(root).repos)
    assert not (root / ".tracker" / ".gitignore").exists()


@pytest.mark.parametrize("root", trees(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_no_real_owners(root):
    """Synthetic only: every repo and URL is under example-org."""
    text = "".join(p.read_text() for p in root.rglob("*") if p.is_file())
    owners = set(re.findall(r'"gh": "([^/"]+)/', text)) | set(re.findall(r"github\.com/([^/]+)/", text))
    assert owners == {"example-org"}

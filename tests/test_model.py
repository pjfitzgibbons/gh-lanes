"""model.py: the item, baseline and milestone schemas, read from and written to their files."""

from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML

from ghplan.model import Item, Milestone
from ghplan.store import (
    FileFormatError,
    dumps_markdown,
    load_markdown,
    split_front_matter,
)

# The design 0001 *Item* example, in the canonical form of design 0001 *File format*.
ITEM_FILE = """\
---
title: Retry failed webhook deliveries
type: feat
status: Todo
estimate: 3
priority: P1
ordinal: 100
lane: api
milestone: beta
labels:
  - area:webhooks
parent: wa-ridal
blocked_by:
  - "ba-sokim - Sign webhook payloads"
started: 2026-10-14T09:30:00Z
baseline:
  start: 2026-10-13
  finish: 2026-10-18
  frozen_at: 2026-10-10T16:00:00Z
  reason: Beta checkpoint
---
### Summary
A webhook delivery that fails is dropped. Retry it with backoff before giving up.
"""

MILESTONE_FILE = """\
---
title: Beta
order: 200
---
Every P0 and P1 item in `api` and `frontend` is Done, and signup has run end to end on staging.
"""

MINIMAL = {"title": "Retry failed webhook deliveries", "type": "feat"}
REPO_TRACKER = Path(__file__).parents[1] / ".tracker"


def front(text: str) -> dict:
    """The front matter as YAML types it: dates and datetimes, not strings."""
    return YAML(typ="safe").load(split_front_matter(text, Path("example.md"))[0])


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_the_design_example():
    item = Item.model_validate(front(ITEM_FILE))
    assert (item.title, item.type, item.estimate) == ("Retry failed webhook deliveries", "feat", 3)
    assert item.parent == "wa-ridal"
    assert item.blocker_ids == ["ba-sokim"]
    assert item.started == datetime(2026, 10, 14, 9, 30, tzinfo=UTC)
    assert item.baseline.finish == date(2026, 10, 18)


def test_defaults():
    item = Item.model_validate(MINIMAL)
    assert (item.status, item.priority, item.estimate, item.milestone) == ("Icebox", "P2", None, None)
    assert (item.labels, item.parent, item.blocked_by, item.started) == ([], None, [], None)


@pytest.mark.parametrize("missing", ["title", "type"])
def test_title_and_type_are_required(missing):
    data = dict(MINIMAL)
    del data[missing]
    with pytest.raises(ValidationError, match=missing):
        Item.model_validate(data)


@pytest.mark.parametrize("type", ["feat", "bug", "chore"])
def test_accepts_each_type(type):
    assert Item.model_validate(MINIMAL | {"type": type}).type == type


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"estimate": 8}, "estimate"),
        ({"estimate": 13}, "estimate"),
        ({"estimate": 4}, "estimate"),
        ({"estimate": True}, "estimate"),
        ({"estimate": "3"}, "estimate"),
        ({"ordinal": "100"}, "ordinal"),
        ({"type": "fix"}, "type"),
        ({"priority": "P4"}, "priority"),
        ({"status": "In Review"}, "status"),
        ({"labels": "area:webhooks"}, "labels"),
        ({"parent": "ridal"}, "not an item ID"),
        ({"parent": "wa-ridal - Webhooks"}, "not an item ID"),
        ({"blocked_by": ["Sign webhook payloads"]}, "does not start with an item ID"),
        ({"blocked_by": ["ba-sokim: Sign webhook payloads"]}, "does not start with an item ID"),
        ({"started": "2026-10-14T09:30:00Z"}, "started"),
        # GitHub identity and the old JSON fields are gone, so a file still carrying them fails.
        ({"issue": 23}, "issue"),
        ({"node_id": "I_kwDOA1b2c3"}, "node_id"),
        ({"draft": False}, "draft"),
        ({"repo": "web-app"}, "repo"),
        ({"id": "wa-tunep"}, "id"),
        (
            {"baseline": {"start": date(2026, 10, 15), "finish": date(2026, 10, 13),
                          "frozen_at": datetime(2026, 10, 10, 16, tzinfo=UTC), "reason": "r"}},
            "finishes 2026-10-13 before it starts",
        ),
    ],
)
def test_rejects_bad_item(change, message):
    with pytest.raises(ValidationError, match=message):
        Item.model_validate(MINIMAL | change)


def test_a_blocker_may_omit_its_title():
    assert Item.model_validate(MINIMAL | {"blocked_by": ["ba-sokim"]}).blocker_ids == ["ba-sokim"]


def test_loads_a_milestone():
    m = Milestone.model_validate(front(MILESTONE_FILE))
    assert (m.title, m.order) == ("Beta", 200)


@pytest.mark.parametrize(
    "change", [{"id": "beta"}, {"exit_criterion": "Done"}, {"order": "200"}, {"order": True}]
)
def test_rejects_bad_milestone(change):
    with pytest.raises(ValidationError, match=next(iter(change))):
        Milestone.model_validate(front(MILESTONE_FILE) | change)


@pytest.mark.parametrize("missing", ["title", "order"])
def test_milestone_fields_are_required(missing):
    data = front(MILESTONE_FILE)
    del data[missing]
    with pytest.raises(ValidationError, match=missing):
        Milestone.model_validate(data)


# The canonical form


def test_the_design_examples_are_canonical(tmp_path):
    for name, model, text in [("wa-tunep.md", Item, ITEM_FILE), ("beta.md", Milestone, MILESTONE_FILE)]:
        assert dumps_markdown(*load_markdown(write(tmp_path, name, text), model)) == text


def test_keys_follow_the_field_order_whatever_the_input_order():
    item = Item.model_validate(dict(reversed(list(front(ITEM_FILE).items()))))
    body = ITEM_FILE.split("---\n", 2)[2]
    assert dumps_markdown(item, body) == ITEM_FILE


def test_only_null_and_empty_fields_are_left_out():
    """A default is still written, so every item file carries title, type, status and priority."""
    assert dumps_markdown(Item.model_validate(MINIMAL), "") == (
        "---\ntitle: Retry failed webhook deliveries\ntype: feat\nstatus: Icebox\npriority: P2\n---\n"
    )


def test_each_blocker_is_double_quoted_even_when_plain_would_do():
    item = Item.model_validate(MINIMAL | {"blocked_by": ["ba-sokim", "ba-kipes - Sign payloads"]})
    assert '  - "ba-sokim"\n  - "ba-kipes - Sign payloads"\n' in dumps_markdown(item, "")


def test_a_json_dump_has_plain_strings():
    item = Item.model_validate(MINIMAL | {"blocked_by": ["ba-sokim"]})
    assert type(item.model_dump(mode="json")["blocked_by"][0]) is str


@pytest.mark.parametrize(
    "started",
    [
        datetime(2026, 10, 14, 10, 30, tzinfo=timezone(timedelta(hours=1))),
        datetime(2026, 10, 14, 9, 30, 0, 123456, tzinfo=UTC),
    ],
    ids=["offset", "fractional"],
)
def test_a_datetime_is_held_as_utc_to_the_second(started):
    item = Item.model_validate(front(ITEM_FILE) | {"started": started})
    assert item.started == datetime(2026, 10, 14, 9, 30, tzinfo=UTC)


def test_a_datetime_without_a_time_zone_is_rejected():
    with pytest.raises(ValidationError, match="has no time zone"):
        Item.model_validate(MINIMAL | {"started": datetime(2026, 10, 14, 9, 30)})


# Reading a file


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("lanee: api\n", "lanee"),
        ("estimate: 8\n", "estimate"),
        ("ordinal: high\n", "ordinal"),
    ],
    ids=["unknown-key", "estimate-not-allowed", "wrong-type"],
)
def test_a_bad_item_fails_naming_the_file(tmp_path, change, message):
    text = ITEM_FILE.replace("estimate: 3\n", "").replace("ordinal: 100\n", "")
    path = write(tmp_path, "wa-tunep.md", text.replace("type: feat\n", f"type: feat\n{change}"))
    with pytest.raises(FileFormatError, match=message) as e:
        load_markdown(path, Item)
    assert str(path) in str(e.value)


def test_this_repos_tracker_validates():
    """gh-plan's own items and milestones load against the schemas."""
    files = [(p, Item) for p in sorted((REPO_TRACKER / "items").glob("*.md"))]
    files += [(p, Milestone) for p in sorted((REPO_TRACKER / "milestones").glob("*.md"))]
    assert files
    for path, model in files:
        load_markdown(path, model)

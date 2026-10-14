"""model.py: the item, baseline and milestone schemas, and the canonical JSON form."""

import json
from datetime import date

import pytest
from pydantic import ValidationError

from ghplan.model import FileFormatError, Item, Milestone, dumps, read_json

# The design 0001 *Item* example, in the canonical form of design 0001 *File format*.
ITEM_FILE = """\
{
  "issue": 23,
  "node_id": "I_kwDOA1b2c3",
  "draft": false,
  "repo": "web-app",
  "estimate": 2,
  "priority": "P0",
  "status": "Todo",
  "ordinal": 100,
  "lane": "frontend",
  "milestone": "beta",
  "baseline": {
    "start": "2026-10-13",
    "finish": "2026-10-15",
    "frozen_at": "2026-10-10T16:00:00Z",
    "reason": "Beta checkpoint"
  }
}
"""

MILESTONE_FILE = """\
{
  "id": "beta",
  "title": "Beta",
  "exit_criterion": "Every beta issue closed and the checkout flow demoed",
  "order": 200
}
"""

IDENTITY = {"node_id": "I_kwDOA1b2c3", "issue": 23, "repo": "web-app"}


def load(text: str):
    return json.loads(text)


def test_loads_the_design_example():
    item = Item.model_validate(load(ITEM_FILE))
    assert item.estimate == 2
    assert item.baseline.finish == date(2026, 10, 15)
    assert item.baseline.frozen_at.tzinfo is not None


def test_defaults():
    item = Item.model_validate(IDENTITY)
    assert (item.status, item.priority, item.estimate, item.milestone) == ("Icebox", "P2", None, None)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"estimate": 8}, "estimate"),
        ({"estimate": 13}, "estimate"),
        ({"estimate": 4}, "estimate"),
        ({"priority": "P4"}, "priority"),
        ({"status": "In Review"}, "status"),
        ({"title": "Copied from GitHub"}, "title"),
        ({"depends_on": [12]}, "depends_on"),
        ({"draft": True}, "a draft has no node_id"),
        ({"node_id": None}, "needs node_id and issue"),
        ({"issue": None}, "needs node_id and issue"),
        (
            {"baseline": {"start": "2026-10-15", "finish": "2026-10-13",
                          "frozen_at": "2026-10-10T16:00:00Z", "reason": "r"}},
            "finishes 2026-10-13 before it starts",
        ),
    ],
)
def test_rejects_bad_item(change, message):
    with pytest.raises(ValidationError, match=message):
        Item.model_validate(IDENTITY | change)


def test_a_draft_has_no_identity():
    item = Item.model_validate({"repo": "web-app", "draft": True, "estimate": 1})
    assert (item.node_id, item.issue) == (None, None)


def test_loads_a_milestone_checked_against_its_stem():
    m = Milestone.model_validate(load(MILESTONE_FILE), context={"stem": "beta"})
    assert (m.id, m.order) == ("beta", 200)


def test_milestone_id_must_equal_the_stem():
    with pytest.raises(ValidationError, match="must equal the file name 'beta-2'"):
        Milestone.model_validate(load(MILESTONE_FILE), context={"stem": "beta-2"})


@pytest.mark.parametrize("missing", ["id", "title", "exit_criterion", "order"])
def test_milestone_fields_are_required(missing):
    data = load(MILESTONE_FILE)
    del data[missing]
    with pytest.raises(ValidationError, match=missing):
        Milestone.model_validate(data)


# The canonical form


def test_the_design_example_is_canonical():
    assert dumps(Item.model_validate(load(ITEM_FILE))) == ITEM_FILE
    assert dumps(Milestone.model_validate(load(MILESTONE_FILE))) == MILESTONE_FILE


def test_keys_follow_the_field_order_whatever_the_input_order():
    item = Item.model_validate(dict(reversed(list(load(ITEM_FILE).items()))))
    assert list(json.loads(dumps(item))) == list(Item.model_fields)  # the example sets every field


def test_only_null_fields_are_left_out():
    """A default is still written, so equal items give identical files however they were built."""
    assert json.loads(dumps(Item.model_validate(IDENTITY))) == {
        "issue": 23, "node_id": "I_kwDOA1b2c3", "draft": False, "repo": "web-app",
        "priority": "P2", "status": "Icebox",
    }


def test_a_utc_datetime_ends_in_z():
    assert '"frozen_at": "2026-10-10T16:00:00Z"' in dumps(Item.model_validate(load(ITEM_FILE)))


@pytest.mark.parametrize(
    "frozen_at",
    ["2026-10-10T17:00:00+01:00", "2026-10-10T16:00:00.123456Z", "2026-10-10T16:00:00+00:00"],
    ids=["offset", "fractional", "plus-zero"],
)
def test_a_datetime_is_held_as_utc_to_the_second(frozen_at):
    data = load(ITEM_FILE)
    data["baseline"]["frozen_at"] = frozen_at
    assert dumps(Item.model_validate(data)) == ITEM_FILE


def test_a_datetime_without_a_time_zone_is_rejected():
    data = load(ITEM_FILE)
    data["baseline"]["frozen_at"] = "2026-10-10T16:00:00"
    with pytest.raises(ValidationError, match="has no time zone"):
        Item.model_validate(data)


def test_non_ascii_is_written_as_itself():
    m = Milestone.model_validate(load(MILESTONE_FILE) | {"title": "Café"})
    assert '"title": "Café"' in dumps(m)


# Reading a file


def test_reads_utf8_without_escapes(tmp_path):
    path = tmp_path / "beta.json"
    path.write_text(MILESTONE_FILE.replace("Beta", "Café"), encoding="utf-8")
    assert read_json(path)["title"] == "Café"


def test_a_leading_byte_order_mark_is_accepted(tmp_path):
    path = tmp_path / "beta.json"
    path.write_bytes(b"\xef\xbb\xbf" + MILESTONE_FILE.encode())
    m = Milestone.model_validate(read_json(path))
    assert not dumps(m).startswith("\ufeff")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b'{"title": "Caf\xe9"}', "not valid UTF-8"),
        (b'{"title": ', "not valid JSON"),
        (b'{"order": NaN}', "NaN is not a JSON number"),
        (b'{"order": -Infinity}', "-Infinity is not a JSON number"),
    ],
    ids=["latin-1", "truncated", "nan", "infinity"],
)
def test_an_unreadable_file_is_reported_by_name(tmp_path, content, message):
    path = tmp_path / "beta.json"
    path.write_bytes(content)
    with pytest.raises(FileFormatError, match=message) as e:
        read_json(path)
    assert str(path) in str(e.value)

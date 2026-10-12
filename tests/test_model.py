"""model.py: the item, baseline and milestone schemas."""

from datetime import date

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML

from ghplan.model import Item, Milestone

# The design 0001 *Item* example.
ITEM_FILE = """\
issue: 23
node_id: I_kwDOA1b2c3
repo: web-app
estimate: 2
priority: P0
status: Todo
ordinal: 100
lane: frontend
milestone: beta
baseline:
  start: 2026-10-13
  finish: 2026-10-15
  frozen_at: 2026-10-10T16:00:00Z
  reason: "Beta checkpoint"
"""

MILESTONE_FILE = """\
id: beta
title: Beta
exit_criterion: Every beta issue closed and the checkout flow demoed
order: 200
"""

IDENTITY = {"node_id": "I_kwDOA1b2c3", "issue": 23, "repo": "web-app"}


def load(text: str):
    return YAML(typ="safe", pure=True).load(text)


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

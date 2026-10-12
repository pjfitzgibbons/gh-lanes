"""config.py: the config.yml model and `.tracker/` discovery."""

from datetime import date
from pathlib import Path

import pytest

from ghplan import config
from ghplan.config import Config, NotFoundError, TrackerError

# The design 0001 *Config* example, plus the two keys design 0002 adds.
EXAMPLE = """\
points_per_week: 5.0
project_start: 2026-10-13
stale_after_minutes: 15
write_pause_seconds: 1.0       # pause between GitHub mutations
repos:
  web-app:     { path: ".", gh: "example-org/web-app" }
  billing-api: { path: "../billing-api", gh: "example-org/billing-api" }
lanes: [api, frontend, docs, infra]
statuses: [Icebox, Todo, "In Progress", Blocked, Done]
hours_per_point: 8.0
time_source:
  kind: timewarrior
  extra_tag: synthetic
"""

MINIMAL = """\
points_per_week: 5
project_start: 2026-10-13
repos: { web-app: { path: ".", gh: "example-org/web-app" } }
lanes: [api]
"""


def make_tracker(root: Path, text: str = MINIMAL) -> Path:
    (root / ".tracker").mkdir(parents=True)
    (root / ".tracker" / "config.yml").write_text(text, encoding="utf-8")
    return root


# Discovery


def test_walks_up_from_a_nested_directory(tmp_path):
    make_tracker(tmp_path)
    nested = tmp_path / "src" / "deep"
    nested.mkdir(parents=True)
    assert config.find_root(nested, env={}) == tmp_path.resolve()


def test_nearest_tracker_wins(tmp_path):
    make_tracker(tmp_path)
    inner = make_tracker(tmp_path / "inner")
    assert config.find_root(inner, env={}) == inner.resolve()


def test_a_tracker_dir_without_config_is_skipped(tmp_path):
    make_tracker(tmp_path)
    (tmp_path / "child" / ".tracker").mkdir(parents=True)
    assert config.find_root(tmp_path / "child", env={}) == tmp_path.resolve()


def test_plan_root_overrides_the_walk(tmp_path):
    here = make_tracker(tmp_path / "here")
    there = make_tracker(tmp_path / "there")
    assert config.find_root(here, env={"PLAN_ROOT": str(there)}) == there.resolve()


def test_plan_root_without_a_tracker_fails_naming_only_that_path(tmp_path):
    make_tracker(tmp_path)
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(NotFoundError) as e:
        config.find_root(tmp_path, env={"PLAN_ROOT": str(empty)})
    assert e.value.searched == [empty.resolve() / ".tracker" / "config.yml"]
    assert e.value.exit_code == 2


def test_not_found_names_every_path_up_to_the_filesystem_root(tmp_path):
    start = tmp_path / "a" / "b"
    start.mkdir(parents=True)
    with pytest.raises(NotFoundError) as e:
        config.find_root(start, env={})
    searched = e.value.searched
    assert searched[0] == start.resolve() / ".tracker" / "config.yml"
    assert searched[-1] == Path("/.tracker/config.yml")
    assert len(searched) == len(start.resolve().parents) + 1
    assert str(searched[0]) in str(e.value)


def test_defaults_to_the_working_directory_and_environment(tmp_path, monkeypatch):
    make_tracker(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PLAN_ROOT", raising=False)
    assert config.discover().root == tmp_path.resolve()


# The config model


def test_loads_the_design_example(tmp_path):
    tracker = config.discover(make_tracker(tmp_path, EXAMPLE), env={})
    c = tracker.config
    assert c.points_per_week == 5.0
    assert c.project_start == date(2026, 10, 13)
    assert c.repos["billing-api"].gh == "example-org/billing-api"
    assert c.lanes == ["api", "frontend", "docs", "infra"]
    assert c.time_source.kind == "timewarrior"
    assert c.time_source.model_extra == {"extra_tag": "synthetic"}


def test_defaults(tmp_path):
    c = config.load(make_tracker(tmp_path))
    assert c.stale_after_minutes == 15
    assert c.write_pause_seconds == 1.0
    assert c.statuses == config.DEFAULT_STATUSES
    assert c.hours_per_point == 8.0
    assert c.time_source is None


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"lanes": ["api", "api"]}, "lanes repeats api"),
        ({"statuses": ["Todo", "Done", "Todo"]}, "statuses repeats Todo"),
        ({"lanes": []}, "lanes"),
        ({"repos": {}}, "repos"),
        ({"points_per_week": 0}, "points_per_week"),
        ({"write_pause_seconds": -1}, "write_pause_seconds"),
        ({"repos": {"x": {"path": ".", "gh": "no-slash"}}}, "gh"),
        ({"repos": {"x": {"path": "/abs/app", "gh": "o/r"}}}, "must be relative"),
        ({"repos": {"x": {"path": ".", "gh": "-org/r"}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "org_x/r"}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "o/r/extra"}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "o/.."}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "ö/r"}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "o/r\n"}}}, "not owner/name"),
        ({"repos": {"x": {"path": ".", "gh": "o/r", "branch": "main"}}}, "branch"),
        ({"lanse": ["api"]}, "lanse"),
    ],
)
def test_rejects_bad_config(change, message):
    data = {
        "points_per_week": 5,
        "project_start": "2026-10-13",
        "repos": {"web-app": {"path": ".", "gh": "example-org/web-app"}},
        "lanes": ["api"],
    } | change
    with pytest.raises(ValueError, match=message):
        Config.model_validate(data)


@pytest.mark.parametrize(
    "text",
    ["", "lanes: [api\n", "points_per_week: 5\n"],
    ids=["empty", "malformed", "incomplete"],
)
def test_unusable_config_file_is_a_tracker_error(tmp_path, text):
    root = make_tracker(tmp_path, text)
    with pytest.raises(TrackerError, match="config.yml") as e:
        config.load(root)
    assert e.value.exit_code == 2


# Paths the rest of the tool reads


@pytest.mark.parametrize("gh", ["example-org/web-app", "a1/repo.name_2", "o/.github"])
def test_accepts_github_names(gh):
    assert config.Repo(path="../sibling", gh=gh).gh == gh


def test_repo_path_is_relative_to_the_tracker_root(tmp_path):
    tracker = config.discover(make_tracker(tmp_path / "web-app", EXAMPLE), env={})
    assert tracker.repo_path("web-app") == (tmp_path / "web-app").resolve()
    assert tracker.repo_path("billing-api") == (tmp_path / "billing-api").resolve()


def test_milestones_are_discovered_by_glob(tmp_path):
    tracker = config.discover(make_tracker(tmp_path), env={})
    milestones = tracker.tracker_dir / "milestones"
    milestones.mkdir()
    for name in ("phase-2.yml", "phase-1.yml", "notes.md"):
        (milestones / name).write_text("", encoding="utf-8")
    assert [p.name for p in tracker.milestone_files()] == ["phase-1.yml", "phase-2.yml"]


def test_no_milestones_directory_means_no_milestones(tmp_path):
    assert config.discover(make_tracker(tmp_path), env={}).milestone_files() == []

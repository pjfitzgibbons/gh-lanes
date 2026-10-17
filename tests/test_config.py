"""config.py: the config.yml model and `.tracker/` discovery."""

from datetime import date
from pathlib import Path

import pytest

from ghplan import config
from ghplan.config import Config, NeedsConvertingError, NotFoundError, TrackerError
from ghplan.store import dumps_yaml

# The design 0001 *Config* example, plus the `time_source` design 0002 adds, in the canonical form.
EXAMPLE = """\
prefix: wa
points_per_week: 5.0
project_start: 2026-10-13
hours_per_point: 8.0
time_source:
  kind: timewarrior
  extra_tag: synthetic
repos:
  - ../billing-api
lanes:
  - api
  - frontend
  - docs
  - infra
"""

MINIMAL = """\
prefix: wa
points_per_week: 5
project_start: 2026-10-13
lanes: [api]
"""


def make_tracker(root: Path, text: str = MINIMAL, name: str = "config.yml") -> Path:
    (root / ".tracker").mkdir(parents=True)
    (root / ".tracker" / name).write_text(text, encoding="utf-8")
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


def test_a_json_tracker_needs_converting(tmp_path):
    """An unconverted tracker fails loudly at discovery instead of looking absent."""
    make_tracker(tmp_path / "outer")
    json_only = make_tracker(tmp_path / "outer" / "inner", '{"points_per_week": 5}\n', "config.json")
    with pytest.raises(NeedsConvertingError) as e:
        config.find_root(json_only, env={})
    assert e.value.exit_code == 2
    assert str(json_only.resolve() / ".tracker" / "config.json") in str(e.value)
    assert "plan convert" in str(e.value)


def test_a_converted_tracker_ignores_a_leftover_json_config(tmp_path):
    make_tracker(tmp_path)
    (tmp_path / ".tracker" / "config.json").write_text('{"points_per_week": 5}\n', encoding="utf-8")
    assert config.find_root(tmp_path, env={}) == tmp_path.resolve()


def test_defaults_to_the_working_directory_and_environment(tmp_path, monkeypatch):
    make_tracker(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PLAN_ROOT", raising=False)
    assert config.discover().root == tmp_path.resolve()


# The config model


def test_loads_the_design_example(tmp_path):
    tracker = config.discover(make_tracker(tmp_path, EXAMPLE), env={})
    c = tracker.config
    assert c.prefix == "wa"
    assert c.points_per_week == 5.0
    assert c.project_start == date(2026, 10, 13)
    assert c.repos == ["../billing-api"]
    assert c.lanes == ["api", "frontend", "docs", "infra"]
    assert c.time_source.kind == "timewarrior"
    assert c.time_source.model_extra == {"extra_tag": "synthetic"}


def test_the_example_is_canonical(tmp_path):
    assert dumps_yaml(config.load(make_tracker(tmp_path, EXAMPLE))) == EXAMPLE


def test_defaults(tmp_path):
    c = config.load(make_tracker(tmp_path))
    assert c.hours_per_point == 8.0
    assert c.time_source is None
    assert c.repos == []  # a repo planned on its own


def test_no_repos_is_left_out_when_written(tmp_path):
    assert "repos" not in dumps_yaml(config.load(make_tracker(tmp_path)))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"lanes": ["api", "api"]}, "lanes repeats api"),
        ({"repos": ["../b", "../b"]}, "repos repeats ../b"),
        ({"statuses": ["Todo", "Done"]}, "statuses"),
        ({"lanes": []}, "lanes"),
        ({"points_per_week": 0}, "points_per_week"),
        ({"points_per_week": "5"}, "points_per_week"),
        ({"points_per_week": float("inf")}, "points_per_week"),
        ({"hours_per_point": float("nan")}, "hours_per_point"),
        ({"project_start": "2026-10-13"}, "project_start"),
        ({"prefix": "WA"}, "lowercase letters"),
        ({"prefix": "w-a"}, "lowercase letters"),
        ({"prefix": ""}, "lowercase letters"),
        ({"prefix": "wä"}, "lowercase letters"),
        ({"repos": ["/abs/app"]}, "must be relative"),
        ({"repos": {"billing-api": {"path": "../billing-api", "gh": "o/r"}}}, "repos"),
        ({"stale_after_minutes": 15}, "stale_after_minutes"),
        ({"write_pause_seconds": 1.0}, "write_pause_seconds"),
        ({"lanse": ["api"]}, "lanse"),
    ],
)
def test_rejects_bad_config(change, message):
    data = {"prefix": "wa", "points_per_week": 5, "project_start": date(2026, 10, 13),
            "lanes": ["api"]} | change
    with pytest.raises(ValueError, match=message):
        Config.model_validate(data)


@pytest.mark.parametrize("missing", ["prefix", "points_per_week", "project_start", "lanes"])
def test_required_keys(missing):
    data = {"prefix": "wa", "points_per_week": 5, "project_start": date(2026, 10, 13),
            "lanes": ["api"]}
    del data[missing]
    with pytest.raises(ValueError, match=missing):
        Config.model_validate(data)


@pytest.mark.parametrize(
    "content",
    [b"", b"lanes: [api\n", b"points_per_week: 5\n", b"- api\n", b"\xff",
     MINIMAL.replace("points_per_week: 5", "points_per_week: five").encode()],
    ids=["empty", "malformed", "incomplete", "not-a-mapping", "not-utf-8", "wrong-type"],
)
def test_unusable_config_file_is_a_tracker_error(tmp_path, content):
    root = make_tracker(tmp_path)
    (root / ".tracker" / "config.yml").write_bytes(content)
    with pytest.raises(TrackerError, match="config.yml") as e:
        config.load(root)
    assert e.value.exit_code == 2


# Paths the rest of the tool reads


def test_repo_paths_are_relative_to_the_tracker_root(tmp_path):
    tracker = config.discover(make_tracker(tmp_path / "web-app", EXAMPLE), env={})
    assert tracker.repo_paths() == [(tmp_path / "billing-api").resolve()]


def test_milestones_are_discovered_by_glob(tmp_path):
    tracker = config.discover(make_tracker(tmp_path), env={})
    milestones = tracker.tracker_dir / "milestones"
    milestones.mkdir()
    for name in ("phase-2.md", "phase-1.md", "old.json", "notes.txt"):
        (milestones / name).write_text("", encoding="utf-8")
    assert [p.name for p in tracker.milestone_files()] == ["phase-1.md", "phase-2.md"]


def test_no_milestones_directory_means_no_milestones(tmp_path):
    assert config.discover(make_tracker(tmp_path), env={}).milestone_files() == []


def test_loading_a_root_with_no_config_is_a_tracker_error(tmp_path):
    with pytest.raises(TrackerError, match="config.yml") as e:
        config.load(tmp_path)
    assert e.value.exit_code == 2

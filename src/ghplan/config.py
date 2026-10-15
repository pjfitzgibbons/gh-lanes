"""`.tracker/config.yml`: the model, and finding `.tracker/` from wherever the CLI runs.

Discovery walks up from the working directory like git does; `PLAN_ROOT` names the directory that
holds `.tracker/` and skips the walk. See design 0001 *Discovery* and *Config*.
"""

import os
from datetime import date
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ghplan.ids import PREFIX
from ghplan.store import FileFormatError, load_yaml

TRACKER_DIR = ".tracker"
CONFIG_FILE = "config.yml"
JSON_CONFIG_FILE = "config.json"  # the layout before ADRs 0007 and 0008
ROOT_ENV = "PLAN_ROOT"


class TrackerError(Exception):
    """`.tracker/` was not found or its config is unusable. The CLI exits 2 on this."""

    exit_code = 2


class NotFoundError(TrackerError):
    def __init__(self, searched: list[Path]):
        self.searched = searched
        paths = "\n".join(f"  {p}" for p in searched)
        super().__init__(f"no {TRACKER_DIR}/{CONFIG_FILE} found; searched:\n{paths}")


class NeedsConvertingError(TrackerError):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(
            f"{path} is a JSON tracker; tracker files are YAML and Markdown now (ADRs 0007, 0008). "
            f"Convert {path.parent} with `plan convert` before running plan"
        )


class TimeSourceConfig(BaseModel):
    # Keys other than `kind` belong to the adapter `kind` names (design 0002 *Config*).
    model_config = ConfigDict(extra="allow", frozen=True)

    kind: str


class Config(BaseModel):
    # A misspelt key fails loudly instead of silently taking its default.
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, allow_inf_nan=False)

    # Field order is the file's key order.
    prefix: str
    points_per_week: float = Field(gt=0)
    project_start: date
    hours_per_point: float = Field(default=8.0, gt=0)
    time_source: TimeSourceConfig | None = None
    repos: list[str] = []  # member repos, by path relative to the root; absent when planned alone
    lanes: list[str] = Field(min_length=1)

    @field_validator("prefix")
    @classmethod
    def _id_prefix(cls, v: str) -> str:
        if not PREFIX.fullmatch(v):
            raise ValueError(f"prefix {v!r} must be lowercase letters a to z")
        return v

    @field_validator("repos")
    @classmethod
    def _relative(cls, v: list[str]) -> list[str]:
        # An absolute path would replace the root when joined, and differ per machine.
        for path in v:
            if Path(path).is_absolute():
                raise ValueError(f"repos path {path!r} must be relative to the tracker root")
        return v

    @model_validator(mode="after")
    def _no_duplicates(self) -> Self:
        for key in ("repos", "lanes"):
            values = getattr(self, key)
            if dupes := sorted({v for v in values if values.count(v) > 1}):
                raise ValueError(f"{key} repeats {', '.join(dupes)}")
        return self


class Tracker(BaseModel):
    """A discovered `.tracker/`: where it is, and its parsed config."""

    model_config = ConfigDict(frozen=True)

    root: Path  # the directory holding .tracker/
    config: Config

    @property
    def tracker_dir(self) -> Path:
        return self.root / TRACKER_DIR

    def repo_paths(self) -> list[Path]:
        return [(self.root / path).resolve() for path in self.config.repos]

    def milestone_files(self) -> list[Path]:
        return sorted((self.tracker_dir / "milestones").glob("*.md"))


def find_root(cwd: Path | None = None, env: dict[str, str] | None = None) -> Path:
    """Return the directory holding `.tracker/config.yml`, or raise NotFoundError.

    A `.tracker/` holding only `config.json` raises NeedsConvertingError, so an unconverted
    tracker fails loudly instead of the walk passing it by.
    """
    env = os.environ if env is None else env
    if override := env.get(ROOT_ENV):
        candidates = [Path(override).resolve()]
    else:
        start = (cwd or Path.cwd()).resolve()
        candidates = [start, *start.parents]
    searched = []
    for directory in candidates:
        config = directory / TRACKER_DIR / CONFIG_FILE
        searched.append(config)
        if config.is_file():
            return directory
        if (json_config := config.with_name(JSON_CONFIG_FILE)).is_file():
            raise NeedsConvertingError(json_config)
    raise NotFoundError(searched)


def load(root: Path) -> Config:
    path = root / TRACKER_DIR / CONFIG_FILE
    try:
        return load_yaml(path, Config)
    except FileFormatError as e:
        raise TrackerError(str(e)) from e
    except OSError as e:
        raise TrackerError(f"{path}: {e}") from e


def discover(cwd: Path | None = None, env: dict[str, str] | None = None) -> Tracker:
    root = find_root(cwd, env)
    return Tracker(root=root, config=load(root))

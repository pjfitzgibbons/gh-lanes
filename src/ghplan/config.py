"""`.tracker/config.yml`: the model, and finding `.tracker/` from wherever the CLI runs.

Discovery walks up from the working directory like git does; `PLAN_ROOT` names the directory that
holds `.tracker/` and skips the walk. See design 0001 *Discovery* and *Config*.
"""

import os
import re
from datetime import date
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from ruamel.yaml import YAML, YAMLError

TRACKER_DIR = ".tracker"
CONFIG_FILE = "config.yml"
ROOT_ENV = "PLAN_ROOT"
DEFAULT_STATUSES = ["Icebox", "Todo", "In Progress", "Blocked", "Done"]
# GitHub's owner rule: ASCII letters, digits and single inner hyphens. Repo names: ASCII letters,
# digits, `.`, `-` and `_`, with `.` and `..` reserved.
GH_REPO = re.compile(r"(?a)[A-Za-z0-9](?:-?[A-Za-z0-9])*/[A-Za-z0-9._-]+")


class TrackerError(Exception):
    """`.tracker/` was not found or its config is unusable. The CLI exits 2 on this."""

    exit_code = 2


class NotFoundError(TrackerError):
    def __init__(self, searched: list[Path]):
        self.searched = searched
        paths = "\n".join(f"  {p}" for p in searched)
        super().__init__(f"no {TRACKER_DIR}/{CONFIG_FILE} found; searched:\n{paths}")


class Repo(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str  # relative to the directory holding .tracker/
    gh: str  # owner/name

    @field_validator("path")
    @classmethod
    def _relative(cls, v: str) -> str:
        # An absolute path would replace the root when joined, and differ per machine.
        if Path(v).is_absolute():
            raise ValueError(f"path {v!r} must be relative to the tracker root")
        return v

    @field_validator("gh")
    @classmethod
    def _owner_name(cls, v: str) -> str:
        if not GH_REPO.fullmatch(v) or v.split("/")[1] in (".", ".."):
            raise ValueError(f"gh {v!r} is not owner/name")
        return v


class TimeSourceConfig(BaseModel):
    # Keys other than `kind` belong to the adapter `kind` names (design 0002 *Config*).
    model_config = ConfigDict(extra="allow", frozen=True)

    kind: str


class Config(BaseModel):
    # A misspelt key fails loudly instead of silently taking its default.
    model_config = ConfigDict(extra="forbid", frozen=True)

    points_per_week: float = Field(gt=0)
    project_start: date
    stale_after_minutes: int = Field(default=15, ge=0)
    write_pause_seconds: float = Field(default=1.0, ge=0)
    repos: dict[str, Repo] = Field(min_length=1)
    lanes: list[str] = Field(min_length=1)
    statuses: list[str] = Field(default_factory=lambda: list(DEFAULT_STATUSES))
    hours_per_point: float = Field(default=8.0, gt=0)
    time_source: TimeSourceConfig | None = None

    @model_validator(mode="after")
    def _no_duplicates(self) -> Self:
        for name in ("lanes", "statuses"):
            values = getattr(self, name)
            dupes = sorted({v for v in values if values.count(v) > 1})
            if dupes:
                raise ValueError(f"{name} repeats {', '.join(dupes)}")
        return self


class Tracker(BaseModel):
    """A discovered `.tracker/`: where it is, and its parsed config."""

    model_config = ConfigDict(frozen=True)

    root: Path  # the directory holding .tracker/
    config: Config

    @property
    def tracker_dir(self) -> Path:
        return self.root / TRACKER_DIR

    def repo_path(self, name: str) -> Path:
        return (self.root / self.config.repos[name].path).resolve()

    def milestone_files(self) -> list[Path]:
        return sorted((self.tracker_dir / "milestones").glob("*.yml"))


def find_root(cwd: Path | None = None, env: dict[str, str] | None = None) -> Path:
    """Return the directory holding `.tracker/config.yml`, or raise NotFoundError."""
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
    raise NotFoundError(searched)


def load(root: Path) -> Config:
    path = root / TRACKER_DIR / CONFIG_FILE
    try:
        data = YAML(typ="safe", pure=True).load(path.read_text(encoding="utf-8"))
    except (OSError, YAMLError) as e:
        raise TrackerError(f"{path}: {e}") from e
    try:
        return Config.model_validate(data or {})
    except ValidationError as e:
        raise TrackerError(f"{path}: {e}") from e


def discover(cwd: Path | None = None, env: dict[str, str] | None = None) -> Tracker:
    root = find_root(cwd, env)
    return Tracker(root=root, config=load(root))

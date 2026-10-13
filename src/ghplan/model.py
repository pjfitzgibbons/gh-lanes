"""Schemas for the committed files: one item per issue, one milestone per file.

GitHub-owned facts (title, state, labels, parent, blocked-by) are absent on purpose: they are read
by pull and cached in the index, never copied here. See design 0001 *Data model*.

The files are JSON in one canonical form (design 0001 *File format*). Each model declares its fields
in the order the file's keys are written, so `dumps` takes the key order from the model.
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator, model_validator


class FileFormatError(ValueError):
    """A tracker file is not valid UTF-8 or not valid JSON. The message names the file."""


def read_json(path: Path) -> Any:
    """Parse a tracker file. A leading byte-order mark, which some editors add, is accepted."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise FileFormatError(f"{path}: not valid UTF-8: {e}") from e
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise FileFormatError(f"{path}: not valid JSON: {e}") from e


def dumps(model: BaseModel) -> str:
    """The canonical form: keys in field order, null fields left out, UTF-8 unescaped."""
    data = model.model_dump(mode="json", exclude_none=True)
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"

Estimate = Literal[1, 2, 3, 5]  # 8 and 13 mean "split this"; they are not representable
Priority = Literal["P0", "P1", "P2", "P3"]
Status = Literal["Icebox", "Todo", "In Progress", "Blocked", "Done"]


class _File(BaseModel):
    # A misspelt key in a hand-edited file fails instead of being silently dropped.
    model_config = ConfigDict(extra="forbid")


class Baseline(_File):
    start: date
    finish: date
    frozen_at: datetime
    reason: str

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.finish < self.start:
            raise ValueError(f"baseline finishes {self.finish} before it starts {self.start}")
        return self


class Item(_File):
    # Field order is the file's key order.
    issue: int | None = None  # human key; a cache that reconcile repairs. None only while draft
    node_id: str | None = None  # GitHub global id, the real key. None only while draft
    draft: bool = False
    repo: str  # short name in config.repos
    estimate: Estimate | None = None  # None = needs-triage, or a parent with children
    priority: Priority = "P2"
    status: Status = "Icebox"
    ordinal: int | None = None  # sparse rank, the tiebreak inside a priority band
    lane: str | None = None  # checked against config.lanes by validate
    milestone: str | None = None  # None <=> Icebox, checked by validate
    baseline: Baseline | None = None

    @model_validator(mode="after")
    def _draft_has_no_identity(self) -> Self:
        has_identity = (self.node_id is not None, self.issue is not None)
        if self.draft and any(has_identity):
            raise ValueError("a draft has no node_id or issue until push-drafts creates the issue")
        if not self.draft and not all(has_identity):
            raise ValueError("an item needs node_id and issue unless it is a draft")
        return self


class Milestone(_File):
    id: str  # equals the file stem
    title: str
    exit_criterion: str  # may be stricter than "all issues closed"
    order: int  # sparse (100, 200, ...); cross-milestone sequence comes from this

    @field_validator("id")
    @classmethod
    def _matches_stem(cls, v: str, info: ValidationInfo) -> str:
        # The loader passes the file stem as context: Milestone.model_validate(data, context={"stem": ...}).
        stem = (info.context or {}).get("stem")
        if stem is not None and v != stem:
            raise ValueError(f"id {v!r} must equal the file name {stem!r}")
        return v

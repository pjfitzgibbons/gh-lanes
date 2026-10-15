"""Schemas for the committed item and milestone files (design 0001 *Data model*).

The tracker owns every field, title and blocked-by included; no GitHub identity is kept. An item's
and a milestone's ID is its file stem, so no field repeats it, and the Markdown body is read beside
the model by `store.py`. Each model declares its fields in the order the file's keys are written, so
the writer takes the key order from the model.
"""

from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    PlainSerializer,
    SerializationInfo,
    model_validator,
)

from ghplan.ids import ID
from ghplan.store import DoubleQuoted


def _utc_to_the_second(v: datetime) -> datetime:
    # Without a zone the instant is unknown, so it is refused rather than assumed to be UTC.
    if v.tzinfo is None:
        raise ValueError(f"{v.isoformat()} has no time zone; write it in UTC, ending in Z")
    return v.astimezone(UTC).replace(microsecond=0)


def _not_bool(v: Any) -> Any:
    # True == 1, so strict mode alone would take `estimate: true` as an estimate of 1.
    if isinstance(v, bool):
        raise ValueError(f"{v} is not a number")
    return v


def _an_id(v: str) -> str:
    if not ID.fullmatch(v):
        raise ValueError(f"{v!r} is not an item ID, <prefix>-<word>")
    return v


def _blocker(v: str) -> str:
    id, _, _ = v.partition(" - ")
    if not ID.fullmatch(id):
        raise ValueError(f"{v!r} does not start with an item ID: write '<id> - <title>'")
    return v


def _quoted(v: str, info: SerializationInfo) -> str:
    # The YAML writer always double-quotes a blocked_by entry (design 0001 *File format*).
    return v if info.mode == "json" else DoubleQuoted(v)


# Read with any offset, held and written as UTC to the second: "2026-10-10T16:00:00Z".
UtcDatetime = Annotated[datetime, AfterValidator(_utc_to_the_second)]

Estimate = Annotated[Literal[1, 2, 3, 5], BeforeValidator(_not_bool)]  # 8 and 13 mean "split this"
Priority = Literal["P0", "P1", "P2", "P3"]
Status = Literal["Icebox", "Todo", "In Progress", "Blocked", "Done"]
Type = Literal["feat", "bug", "chore"]
ItemId = Annotated[str, AfterValidator(_an_id)]
# "<id> - <title>": the ID is authoritative, the title a reminder for whoever reads the file.
Blocker = Annotated[str, AfterValidator(_blocker), PlainSerializer(_quoted, return_type=str)]


class _File(BaseModel):
    # A misspelt key in a hand-edited file fails instead of being silently dropped, and a value of
    # the wrong type fails instead of being converted.
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Baseline(_File):
    start: date
    finish: date
    frozen_at: UtcDatetime
    reason: str

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.finish < self.start:
            raise ValueError(f"baseline finishes {self.finish} before it starts {self.start}")
        return self


class Item(_File):
    # Field order is the file's key order.
    title: str
    type: Type  # required; names the branch: feat/, fix/, chore/
    status: Status = "Icebox"
    estimate: Estimate | None = None  # None = needs-triage, or a parent with children
    priority: Priority = "P2"
    ordinal: int | None = None  # sparse rank, the tiebreak inside a priority band
    lane: str | None = None  # checked against config.lanes by validate
    milestone: str | None = None  # None <=> Icebox, checked by validate
    labels: list[str] = []
    parent: ItemId | None = None
    blocked_by: list[Blocker] = []
    started: UtcDatetime | None = None  # written once, by the start commit
    baseline: Baseline | None = None

    @property
    def blocker_ids(self) -> list[str]:
        return [entry.partition(" - ")[0] for entry in self.blocked_by]


class Milestone(_File):
    # The exit criterion is the body, which may be stricter than "every item Done".
    title: str
    order: int  # sparse (100, 200, ...); cross-milestone sequence comes from this

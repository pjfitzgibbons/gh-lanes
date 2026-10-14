"""store.py: reading tracker files as YAML 1.2, and writing the one canonical form."""

from datetime import date, datetime
from pathlib import Path

import pytest
import yaml as pyyaml  # PyYAML, a YAML 1.1 reader: the written file must read the same in it
from pydantic import BaseModel

from ghplan.model import FileFormatError
from ghplan.store import (
    dumps_markdown,
    dumps_yaml,
    read_markdown,
    read_yaml,
    split_front_matter,
    write_markdown,
    write_yaml,
)


# Stand-ins for the schemas, which are pl-kozot's. Field order is the file's key order, and is
# deliberately not alphabetical.
class Window(BaseModel):
    start: date
    finish: date
    frozen_at: datetime


class Entry(BaseModel):
    title: str
    type: str = "feat"
    estimate: int | None = None
    lane: str | None = None
    labels: list[str] = []
    blocked_by: list[str] = []
    baseline: Window | None = None


class Text(BaseModel):
    value: str


FRONT_MATTER = """\
title: "store.py: YAML and Markdown front matter"
type: feat
estimate: 3
lane: model
labels:
  - Café
  - "no"
baseline:
  start: 2026-10-13
  finish: 2026-10-15
  frozen_at: 2026-10-10T16:00:00Z
"""

BODY = """\
### Summary
Trailing spaces stay.
\tA tab stays.

```yaml
---
not: front matter
---
```
"""

ITEM_FILE = f"---\n{FRONT_MATTER}---\n{BODY}"


def write(tmp_path, content: str | bytes, name: str = "pl-ganot.md"):
    path = tmp_path / name
    if isinstance(content, str):
        content = content.encode()
    path.write_bytes(content)
    return path


def round_trip(path) -> str:
    data, body = read_markdown(path)
    return dumps_markdown(Entry.model_validate(data), body)


# Round trip


def test_a_canonical_item_file_round_trips_to_identical_bytes(tmp_path):
    assert round_trip(write(tmp_path, ITEM_FILE)) == ITEM_FILE


def test_a_canonical_yaml_file_round_trips_to_identical_bytes(tmp_path):
    path = write(tmp_path, FRONT_MATTER, "config.yml")
    assert dumps_yaml(Entry.model_validate(read_yaml(path))) == FRONT_MATTER


def test_a_hand_edited_layout_loads_and_is_written_back_canonical(tmp_path):
    hand = (
        "---\n"
        "lane:   model\n"
        "title: 'store.py: YAML and Markdown front matter'\n"
        "estimate: 3\n"
        "type: feat\n"
        "labels: [Café, 'no']\n"
        "baseline: {start: 2026-10-13, finish: 2026-10-15, frozen_at: 2026-10-10T18:00:00+02:00}\n"
        f"---\n{BODY}"
    )
    assert round_trip(write(tmp_path, hand)) == ITEM_FILE


def test_the_writers_write_the_canonical_form(tmp_path):
    data, body = read_markdown(write(tmp_path, ITEM_FILE))
    entry = Entry.model_validate(data)
    write_markdown(tmp_path / "out.md", entry, body)
    write_yaml(tmp_path / "out.yml", entry)
    assert (tmp_path / "out.md").read_bytes() == ITEM_FILE.encode()
    assert (tmp_path / "out.yml").read_bytes() == FRONT_MATTER.encode()


# The canonical form


def test_keys_follow_the_model_and_nulls_and_empty_lists_are_left_out():
    text = dumps_yaml(Entry(title="t", lane=None, labels=[]))
    assert text == "title: t\ntype: feat\n"


def test_non_ascii_is_written_as_itself_and_long_lines_are_not_folded():
    title = "Café " * 100
    assert dumps_yaml(Text(value=title.strip())) == f"value: {title.strip()}\n"


def test_a_datetime_is_written_in_utc_to_the_second():
    w = Window(start=date(2026, 10, 13), finish=date(2026, 10, 15),
               frozen_at=datetime.fromisoformat("2026-10-10T18:00:00.5+02:00"))
    assert "frozen_at: 2026-10-10T16:00:00Z\n" in dumps_yaml(w)


# Each would be typed as something other than a string by a YAML 1.1 or 1.2 reader, or can't be
# read plain at all.
AMBIGUOUS = [
    "no", "No", "NO", "yes", "Yes", "on", "On", "off", "OFF", "y", "Y", "n", "N",
    "true", "False", "null", "Null", "~", "",
    "0123", "123", "-1", "0o17", "0x1f", "0b11", "1_000", "1:20",
    "1.10", "1e3", ".inf", "-.Inf", ".nan",
    "2026-10-13", "2026-10-10T16:00:00Z", "2026-10-10 16:00:00",
    "<<", "=",
    "store.py: front matter", "#hash", " leading", "trailing ", "- dash", "a #b", "a\nb",
]  # fmt: skip


@pytest.mark.parametrize("word", AMBIGUOUS)
def test_an_ambiguous_string_is_quoted_and_round_trips_as_a_string(tmp_path, word):
    text = dumps_yaml(Text(value=word))
    assert text.startswith('value: "'), text
    assert read_yaml(write(tmp_path, text, "focus.yml")) == {"value": word}
    assert pyyaml.safe_load(text) == {"value": word}


@pytest.mark.parametrize("word", ["model", "Café", "pl-kozot", "P1", "In Progress", "it's", "v1.10a"])
def test_an_unambiguous_string_is_written_plain(word):
    assert dumps_yaml(Text(value=word)) == f"value: {word}\n"


# The body


def test_the_body_comes_back_unchanged():
    front, body = split_front_matter(ITEM_FILE, Path("pl-ganot.md"))
    assert (front, body) == (FRONT_MATTER, BODY)


def test_a_body_without_a_final_newline_gains_exactly_one(tmp_path):
    path = write(tmp_path, ITEM_FILE.rstrip("\n"))
    assert round_trip(path) == ITEM_FILE


def test_crlf_line_endings_in_the_body_are_kept(tmp_path):
    body = "Windows line\r\nends here\r\n"
    path = write(tmp_path, f"---\n{FRONT_MATTER}---\n{body}")
    assert read_markdown(path)[1] == body


def test_an_empty_body_stays_empty(tmp_path):
    path = write(tmp_path, f"---\n{FRONT_MATTER}---\n")
    assert round_trip(path) == f"---\n{FRONT_MATTER}---\n"


def test_a_closing_delimiter_at_the_end_of_the_file_is_accepted(tmp_path):
    path = write(tmp_path, f"---\n{FRONT_MATTER}---")
    assert read_markdown(path)[1] == ""


# Encoding


def test_a_leading_byte_order_mark_is_accepted_and_dropped_on_write(tmp_path):
    path = write(tmp_path, b"\xef\xbb\xbf" + ITEM_FILE.encode())
    assert round_trip(path) == ITEM_FILE


# Failures, each naming the file


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"title: no delimiters\n", "no front matter"),
        (b"", "no front matter"),
        (b"\n---\ntitle: t\n---\n", "no front matter"),
        (b"---\ntitle: t\nnever closed\n", "never closed"),
        (b"---\ntitle: t\ntitle: u\n---\n", "not valid YAML"),
        (b"---\nlane: !!python/object/apply:os.system [echo]\n---\n", "not valid YAML"),
        (b"---\nlane: !custom x\n---\n", "not valid YAML"),
        (b"---\ntitle: [unclosed\n---\n", "not valid YAML"),
        (b"---\n- a list\n---\n", "not a mapping"),
        (b"---\n---\nbody\n", "not a mapping"),
        (b"---\ntitle: Caf\xe9\n---\n", "not valid UTF-8"),
    ],
    ids=["no-front-matter", "empty", "late-delimiter", "unclosed", "duplicate-key",
         "object-tag", "unknown-tag", "bad-yaml", "list", "empty-front-matter", "latin-1"],
)
def test_an_unreadable_markdown_file_is_reported_by_name(tmp_path, content, message):
    path = write(tmp_path, content)
    with pytest.raises(FileFormatError, match=message) as e:
        read_markdown(path)
    assert str(path) in str(e.value)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"prefix: pl\nprefix: wa\n", "not valid YAML"),
        (b"prefix: !!python/name:os.system\n", "not valid YAML"),
        (b"", "not a mapping"),
        (b"just a string\n", "not a mapping"),
    ],
    ids=["duplicate-key", "object-tag", "empty", "scalar"],
)
def test_an_unreadable_yaml_file_is_reported_by_name(tmp_path, content, message):
    path = write(tmp_path, content, "config.yml")
    with pytest.raises(FileFormatError, match=message) as e:
        read_yaml(path)
    assert str(path) in str(e.value)


def test_yaml_is_read_as_1_2(tmp_path):
    path = write(tmp_path, "a: no\nb: on\nc: 0123\n", "focus.yml")
    assert read_yaml(path) == {"a": "no", "b": "on", "c": 123}

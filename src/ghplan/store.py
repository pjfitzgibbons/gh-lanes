"""Read and write the committed tracker files (design 0001 *File format*, ADR 0007).

Items and milestones are Markdown with YAML front matter; config, focus and ready are plain YAML.
A read loads YAML 1.2 with ruamel.yaml's safe loader and accepts any layout. A write produces the
one canonical form, so a tool write's diff shows only the values that changed. Comments are not
kept. Only the `YAML()` instance API is used: ruamel.yaml has broken its module-level functions
between minor versions.
"""

import io
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from ruamel.yaml import YAML
from ruamel.yaml.emitter import Emitter
from ruamel.yaml.error import YAMLError
from ruamel.yaml.nodes import ScalarNode
from ruamel.yaml.representer import SafeRepresenter
from ruamel.yaml.resolver import VersionedResolver

from ghplan.model import FileFormatError

DELIMITER = "---"
_STR = "tag:yaml.org,2002:str"

# YAML 1.1 types y and n as booleans too; PyYAML and ruamel.yaml leave them out, other readers don't.
_YAML_1_1_EXTRA_BOOLS = re.compile(r"[yYnN]")
_RESOLVER_1_1 = VersionedResolver(version=(1, 1))


def _read_text(path: Path) -> str:
    """Decode a tracker file. A leading byte-order mark, which some editors add, is dropped."""
    try:
        return path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise FileFormatError(f"{path}: not valid UTF-8: {e}") from e


def _load(text: str, path: Path, what: str) -> dict[str, Any]:
    try:
        data = YAML(typ="safe").load(text)
    except YAMLError as e:  # also a duplicate key, or a tag that would build an object
        raise FileFormatError(f"{path}: {what} is not valid YAML: {e}") from e
    if not isinstance(data, dict):
        raise FileFormatError(f"{path}: {what} is not a mapping of keys to values")
    return data


def split_front_matter(text: str, path: Path) -> tuple[str, str]:
    """Split a Markdown file into its front matter and its body, which is returned as it was."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != DELIMITER:
        raise FileFormatError(f"{path}: no front matter: the first line must be {DELIMITER}")
    for n, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == DELIMITER:
            return "".join(lines[1:n]), "".join(lines[n + 1 :])
    raise FileFormatError(f"{path}: the front matter is never closed by a {DELIMITER} line")


def read_yaml(path: Path) -> dict[str, Any]:
    """Load a plain YAML tracker file: config.yml, focus.yml, ready.yml."""
    return _load(_read_text(path), path, "the file")


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    """Load an item or milestone file: its front matter, and its Markdown body unchanged."""
    front, body = split_front_matter(_read_text(path), path)
    return _load(front, path, "the front matter"), body


def _ambiguous(value: str) -> bool:
    """Whether a YAML 1.1 reader would type this plain scalar as something other than a string.

    The 1.2 cases are caught by the emitter itself, which quotes a string its own 1.2 resolver
    would read as another type.
    """
    if _YAML_1_1_EXTRA_BOOLS.fullmatch(value):
        return True
    return _RESOLVER_1_1.resolve(ScalarNode, value, (True, False)) != _STR


class _Representer(SafeRepresenter):
    def represent_str(self, data: str) -> ScalarNode:
        return self.represent_scalar(_STR, data, style='"' if _ambiguous(data) else None)

    def represent_datetime(self, data: datetime) -> ScalarNode:
        # UTC to the second, "2026-10-10T16:00:00Z"; the model has already refused a naive one.
        text = data.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.represent_scalar("tag:yaml.org,2002:timestamp", text)


_Representer.add_representer(str, _Representer.represent_str)
_Representer.add_representer(datetime, _Representer.represent_datetime)


class _Emitter(Emitter):
    def choose_scalar_style(self) -> Any:
        # One quoting style: wherever the emitter would single-quote, double-quote instead.
        style = super().choose_scalar_style()
        return '"' if style == "'" else style


def _writer() -> YAML:
    yaml = YAML(typ="safe", pure=True)  # pure: the C emitter would bypass _Emitter
    yaml.Representer = _Representer
    yaml.Emitter = _Emitter
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.width = sys.maxsize  # never fold a line
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def _prune(value: Any) -> Any:
    # model_dump has already left out the nulls; an empty list goes too.
    if isinstance(value, dict):
        return {k: _prune(v) for k, v in value.items() if v != []}
    if isinstance(value, list):
        return [_prune(v) for v in value]
    return value


def dumps_yaml(model: BaseModel) -> str:
    """The canonical YAML for a model: keys in field order, nulls and empty lists left out."""
    data = _prune(model.model_dump(mode="python", exclude_none=True))
    yaml = _writer()
    yaml.representer.sort_base_mapping_type_on_output = False  # the model's field order
    out = io.StringIO()
    yaml.dump(data, out)
    return out.getvalue()


def dumps_markdown(model: BaseModel, body: str) -> str:
    """An item or milestone file: canonical front matter, then the body as it was read."""
    if body and not body.endswith("\n"):
        body += "\n"
    return f"{DELIMITER}\n{dumps_yaml(model)}{DELIMITER}\n{body}"


def write_yaml(path: Path, model: BaseModel) -> None:
    path.write_text(dumps_yaml(model), encoding="utf-8", newline="")


def write_markdown(path: Path, model: BaseModel, body: str) -> None:
    path.write_text(dumps_markdown(model, body), encoding="utf-8", newline="")

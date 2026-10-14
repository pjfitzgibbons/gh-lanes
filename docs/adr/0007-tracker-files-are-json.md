# ADR 0007: The committed tracker files are formatted JSON

<a id="status"></a>
## 1. Status

Proposed.

<a id="context"></a>
## 2. Context

The committed tracker files are the item files, the milestone files, the config and the focus
file ([ADR 0001](0001-git-is-the-database.md)). They are the evidence [`G1`](../requirements.md) asks
for: diffable, and readable on GitHub by someone with no account. `git log -p` on one of them is
its change history ([`G5`](../requirements.md)), and [`G2`](../requirements.md) asks for a
documented, stable format.

People edit them by hand as well as through the tool ([`G6`](../requirements.md)). `plan set` is the command-line alternative
to editing an item file
([design 0001, *set*](../design/0001-phase-1.md#set)), and the schema rejects an unknown key so
that a typo in a hand-edited file fails instead of being dropped
([design 0001, *Item*](../design/0001-phase-1.md#item)). Every write is validated first
([`B3`](../requirements.md)).

The files were YAML, chosen on the premise that item files carry hand-written comments that a
rewrite must keep. No requirement in [requirements](../requirements.md) asks for comments in
tracker files. Without that premise, the format is chosen on parsing, typing and tooling.

<a id="decision"></a>
## 3. Decision

The committed tracker files are JSON: `.tracker/items/<repo>/<n>.json`,
`.tracker/milestones/<id>.json`, `.tracker/config.json` and `.tracker/focus.json`.

The tool writes one canonical form, formatted for a person to read and edit: two-space indent, one
key per line, keys in a fixed order, null fields left out, UTF-8 with no escaping, and a trailing
newline. Every write produces exactly that form. The details are in
[design 0001, *File format*](../design/0001-phase-1.md#file-format).

The files carry no comments. The reason for a change is the commit message that made it, as
ADR 0001 already has it for `G5`.

<a id="alternatives"></a>
## 4. Alternatives considered

- YAML. It allows comments and needs fewer quotes and commas. Python's standard library has no
  YAML parser, and keeping comments through a rewrite needs ruamel.yaml's round-trip mode. YAML
  also types untagged scalars by pattern: `2026-10-13` loads as a date and `1.10` as the float
  1.1 ([YAML 1.2, §10.3 Core Schema](https://yaml.org/spec/1.2.2/#103-core-schema)). Under
  YAML 1.1, which PyYAML and many other tools still implement, `no` loads as false and `0123` as
  the octal 83 ([bool](https://yaml.org/type/bool.html), [int](https://yaml.org/type/int.html)),
  so a lane named `no` loads wrong and one file can load differently in two parsers. Keeping
  YAML without comment preservation drops the round-trip code but keeps the dependency and the
  typing. Comments were its one advantage, and no requirement needs them.
- JSON with comments (JSONC or JSON5). The standard library's `json` parses neither, so it needs a
  dependency, and the tool would again have to keep comments through a rewrite.
- TOML. Python reads it with the standard library's `tomllib`, which cannot write it
  ([tomllib](https://docs.python.org/3/library/tomllib.html)), so writes need a dependency.

<a id="consequences"></a>
## 5. Consequences

- The standard library's `json` reads and writes every tracker file, and the ruamel.yaml
  dependency goes away. Pydantic validates JSON input directly
  ([`model_validate_json`](https://docs.pydantic.dev/latest/concepts/json/)).
- Types are explicit. A string is quoted, so a lane named `no` stays a string. Dates and datetimes
  are ISO 8601 strings, and the model's field types parse them.
- Every write produces the canonical form, so a tool write's diff shows only the values that
  changed. A hand edit in another layout is valid; the next tool write puts that file back into
  the canonical form, and that one diff also shows the layout change.
- Hand-editing costs quotes and commas. Adding a key after the last one also changes the line
  above it, which gains a comma.
- An item file has no place for a note about why a value is what it is. That note goes in the
  commit message.
- `jq` reads the files. VS Code validates a JSON file against a JSON Schema
  ([JSON editing in VS Code](https://code.visualstudio.com/docs/languages/json#_json-schemas-and-settings)),
  and Pydantic can generate one from the models
  ([JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)).
- A tracker already written in YAML is converted to JSON once.

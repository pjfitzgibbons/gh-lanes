# ADR 0007: The committed tracker files are YAML, and items and milestones are Markdown

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

People edit them by hand as well as through the tool ([`G6`](../requirements.md)). `plan set` is
the command-line alternative to editing an item file
([design 0001, *set*](../design/0001-phase-1.md#set)), and the schema rejects an unknown key so
that a typo in a hand-edited file fails instead of being dropped
([design 0001, *Item*](../design/0001-phase-1.md#item)). Every write is validated first
([`B3`](../requirements.md)).

An item file is the whole record of an item, its description as well as its fields
([ADR 0008](0008-file-native-items.md)). The description is prose in the issue outline, and a
milestone's exit criterion is prose too. Prose with a block of fields above it is what Markdown
front matter is for, and YAML is the front matter that editors, static-site tools and other
file-based trackers read.

<a id="decision"></a>
## 3. Decision

Every committed tracker file is YAML.

- Items and milestones are Markdown files with YAML front matter: `.tracker/items/<id>.md` and
  `.tracker/milestones/<id>.md`. The front matter, between two `---` lines, holds the fields. The
  Markdown after it is the description.
- `.tracker/config.yml` and `.tracker/focus.yml` are plain YAML.

Files are read as YAML 1.2 with a safe loader, so a scalar's type follows the 1.2 core schema and
no tag can build an object. The schema then checks every field's type, and a value of the wrong
type fails with the file's name rather than being converted.

The tool writes one canonical form: block style, two-space indent, keys in the model's field
order, null fields left out, UTF-8 with no escaping, no line folding, and a trailing newline. A
string that a YAML 1.1 or 1.2 parser would read as another type is quoted, such as `no`, `yes`,
`null`, `0123` or `1.10`, so the file reads the same in any YAML tool. The Markdown body is written
back exactly as it was read, except that a body without a final newline gets one. The details are
in
[design 0001, *File format*](../design/0001-phase-1.md#file-format).

The tool does not keep comments in front matter or in the YAML files. A note about a value goes in
the Markdown body, and the reason for a change goes in the commit message that made it, as
ADR 0001 has it for `G5`.

<a id="alternatives"></a>
## 4. Alternatives considered

- JSON for every file, with the description as a string field. The standard library reads and
  writes it, and its types are explicit. A multi-line description becomes one escaped string,
  which is hard to read and edit and diffs as a single changed line.
- JSON front matter on Markdown, or JSON for config and focus beside Markdown items. JSON front
  matter is unusual, so editors and other tools do not read it. Mixing formats means two parsers
  and two canonical forms for one directory.
- TOML front matter (between `+++` lines). Every string is quoted and every date is explicit, so
  TOML has no typing surprises. Python reads it with the standard library's `tomllib`, which cannot
  write it ([tomllib](https://docs.python.org/3/library/tomllib.html)), so writes need a dependency
  anyway, and fewer tools read TOML front matter than YAML.
- YAML 1.1 (PyYAML). It types untagged scalars by pattern more widely than 1.2: `no` loads as false
  and `0123` as the octal 83 ([bool](https://yaml.org/type/bool.html),
  [int](https://yaml.org/type/int.html)). Under the 1.2 core schema `no` is a string and `0123` is
  123, though `2026-10-13` still loads as a date and `1.10` as the float 1.1
  ([YAML 1.2, §10.3 Core Schema](https://yaml.org/spec/1.2.2/#103-core-schema)).
- Keeping comments through a rewrite (ruamel.yaml's round-trip mode). No requirement asks for
  comments, and the Markdown body takes the notes a comment would hold.

<a id="consequences"></a>
## 5. Consequences

- The tool depends on ruamel.yaml, which reads and writes YAML 1.2
  ([ruamel.yaml](https://pypi.org/project/ruamel.yaml/)). Its safe loader refuses Python object
  tags and duplicate keys. Pydantic validates the loaded data as it does any Python object.
- ruamel.yaml has one maintainer, and its API has broken between minor versions: 0.18 made the
  module-level `load` and `dump` functions an error. The tool uses only the `YAML()` instance API
  and pins a minimum version.
- ruamel.yaml's writer follows YAML 1.2 and writes `no` and `yes` unquoted, which a YAML 1.1 reader
  takes as booleans. The tool adds its own quoting for those words, and sets the key order and line
  width its defaults would change.
- A mistyped value fails loudly. A lane written `no` reaches the schema as the string `"no"`, and
  one written `true` reaches it as a boolean and is rejected, naming the file.
- Every write produces the canonical form, so a tool write's diff shows only the values that
  changed. A hand edit in another layout is valid; the next tool write puts that file back into
  the canonical form, and that one diff also shows the layout change.
- A comment written by hand in front matter or a YAML file is lost on the next tool write. A
  comment in the Markdown body is kept.
- Hand-editing needs no quotes or commas except where a string would read as another type.
- GitHub's file view renders a Markdown file's YAML front matter as a table above the body, one
  row per key, so an item reads well in the browser. A list such as `blocked_by` becomes a nested
  table with its entries side by side in one row, and a mapping such as `baseline` a nested table
  with its keys as column headings. Verified 2026-10-14 against the rendered HTML from the contents
  API (`Accept: application/vnd.github.html`). The `/markdown` rendering endpoint shows front
  matter as plain text.
- VS Code validates YAML against a JSON Schema through the Red Hat YAML extension, mapped by a
  `yaml.schemas` glob ([vscode-yaml](https://github.com/redhat-developer/vscode-yaml)), and
  Pydantic can generate the schema from the models
  ([JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)).
- A tracker already written in JSON is converted once.

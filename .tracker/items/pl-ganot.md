---
title: "store.py: YAML and Markdown front matter, in one canonical form"
type: feat
status: Done
estimate: 3
priority: P1
ordinal: 400
lane: model
milestone: bootstrap
started: 2026-10-14T22:02:19Z
---
### Summary
Read and write tracker files as ADR 0007 decides: Markdown with YAML front matter for issues and milestones, plain YAML for `config.yml` and `focus.yml`, loaded as YAML 1.2 with ruamel.yaml's safe loader. It replaces `read_json` and `dumps` in `model.py` and supersedes #9.

### Scope
- Split a file into front matter and body; a file with no front matter, or an unclosed one, fails naming the file.
- Load with `YAML(typ="safe")`, which refuses object tags and duplicate keys.
- Write the canonical form: block style, two-space indent, keys in model field order, null fields and empty lists left out, UTF-8 unescaped, no line folding, a trailing newline.
- Quote any string a YAML 1.1 or 1.2 reader would type as something else (`no`, `yes`, `null`, `0123`, `1.10`, a date-like string).
- Write the Markdown body back byte for byte, except that a body without a final newline gets one.
- Pin a minimum ruamel.yaml version and use only the `YAML()` instance API.
- Out of scope: the schemas themselves (pl-kozot), always double-quoting `blocked_by` entries, which needs the field names (pl-kozot), and comments, which are not kept.

### Acceptance
- Reading then writing a canonical file gives identical bytes.
- Each word on the quoting list round-trips as a string, and the written file loads as the same string under PyYAML's 1.1 loader.
- A body with trailing spaces, tabs and a `---` line inside a code block comes back unchanged.
- A body with no final newline gains exactly one, and nothing else in it changes.

### Tests
Unit tests in `tests/test_store.py`: round trip, quoting table, body preservation, a body with no final newline, missing and unclosed front matter, object tags, duplicate keys.

### Lenses
- [x] L1 Security: the safe loader refuses tags that build objects
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [x] L6 Compatibility and migration: adds the YAML reader and writer beside the JSON ones; `read_json` and `dumps` go once pl-kozot moves config discovery to `config.yml` and pl-nahuj converts the fixtures
- [ ] L7 Usability and accessibility
- [x] L8 Testability: pure functions over text and paths, no network
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [ ] L12 Offline and concurrency

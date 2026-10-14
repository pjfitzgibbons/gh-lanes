---
title: "IDs: draw a word, keep the blocklist, resolve what is typed"
status: Todo
estimate: 2
priority: P1
ordinal: 600
lane: engine
milestone: bootstrap
---
### Summary
Generate issue IDs as ADR 0008 decides, `<prefix>-<word>` with a random CVCVC word, and resolve the short forms people type.

### Scope
- The alphabet: 16 consonants and 5 vowels, about 102,000 words per repo. Record which 16 in design 0001.
- A committed blocklist of words that read badly; a drawn word on it, or already used by a file in the repo, is drawn again.
- Resolve, in order: a full ID; a word without the prefix inside its own repo; a unique prefix of the word; a unique word from a title; the ID in the current branch name (`<type>/<id>-<slug>`).
- An ambiguous match lists the candidates with their titles and exits non-zero.
- Out of scope: shell completion, which comes with the CLI.

### Acceptance
- Ten thousand draws hold no blocklisted word and match CVCVC.
- Each resolution form finds its issue in a fixture tracker, and an ambiguous prefix lists both candidates.

### Tests
Unit tests over a seeded generator and a fixture tracker.

### Lenses
- [ ] L1 Security
- [ ] L2 Privacy and data
- [ ] L3 Reliability and failure
- [ ] L4 Performance and limits
- [ ] L5 Observability
- [ ] L6 Compatibility and migration
- [x] L7 Usability and accessibility: an ID is rarely typed in full
- [ ] L8 Testability
- [ ] L9 Operations and cost
- [ ] L10 Docs impact
- [ ] L11 Invariants
- [x] L12 Offline and concurrency: random words keep worktrees from colliding; a rare duplicate is a merge conflict that validate reports

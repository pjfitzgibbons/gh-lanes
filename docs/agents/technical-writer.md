# technical-writer — gh-plan

<a id="technical-writer-lenses"></a>

## 1. Lenses

Two lenses are added to the global L1–L10:

| Lens | Question |
|---|---|
| L11 Invariants | Which of the invariants in [architecture §10](../architecture.md#invariants) does this touch, and why does each still hold? |
| L12 Offline and concurrency | What happens without the network? What happens when two clones or agents edit the same item files? |

<a id="technical-writer-design-docs"></a>

## 2. Design docs

After the global sections 1–5, a design doc here adds:

6. Testing
7. Requirements coverage: which IDs in [requirements](../requirements.md) the design meets
8. Work breakdown: the items that build it

<a id="technical-writer-issues"></a>

## 3. Items

An item is a file, `.tracker/items/<id>.md`: YAML front matter, then a Markdown body ([design 0001, *Item*](../design/0001-phase-1.md#item)).

- **Title:** the `title` field, an imperative outcome. It carries no estimate.
- **Type:** `type` is `feat`, `bug` or `chore`, and names the branch: `feat/`, `fix/` or `chore/`.
- **Front matter:** `type`, `estimate`, `priority`, `ordinal`, `lane`, `milestone`, `labels`, `parent` and `blocked_by` are fields, in the order [design 0001, *File format*](../design/0001-phase-1.md#file-format) lists. The estimate is one of 1, 2, 3 or 5. 8 and 13 mean "split this" and are never used as an estimate.
- **Sections:** the global four, Task, Guardrails, Lenses and Done. Lenses lists L1 to L12. Done's pass/fail conditions include what the test suite proves, and each `[x]` lens has one that names it, as `L11: …`. There is no *Planning* section; the front matter holds what it held.
- **Lanes** are the ones in `.tracker/config.yml`: `cli`, `engine`, `github`, `infra`, `model`, `web`.
- **Dependencies** are `blocked_by` in the front matter, as `"<id> - <title>"` strings, never lines in the body.
- **Imported items** are rewritten to this outline when they're picked up, before any code, and never in bulk. An item still in the older outline (Summary, Scope, Acceptance, Tests, Lenses) is rewritten the same way.

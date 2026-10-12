# technical-writer — gh-lanes

<a id="technical-writer-lenses"></a>

## 1. Lenses

Two lenses are added to the global L1–L10:

| Lens | Question |
|---|---|
| L11 Invariants | Which of the invariants in [architecture §12](../architecture.md#invariants) does this touch, and why does each still hold? |
| L12 Offline and concurrency | What happens without the network? What happens when two clones or agents edit the same item files? |

<a id="technical-writer-design-docs"></a>

## 2. Design docs

After the global sections 1–5, a design doc here adds:

6. Testing
7. Requirements coverage: which IDs in [requirements](../requirements.md) the design meets
8. Work breakdown: the issues that build it

<a id="technical-writer-issues"></a>

## 3. Issues

- **Title:** `[N] <imperative outcome>`, where N is the estimate, one of 1, 2, 3 or 5. 8 and 13 mean "split this" and are never used as an estimate.
- **Sections:** after `### Acceptance`, a `### Tests` section says what the suite proves. After `### Lenses`, a `### Planning` section closes the body:

  ```markdown
  ### Planning
  - Backlog ID: 1.2
  - Estimate: 2
  - Lane: model
  - Milestone: phase-1
  ```

- **Lanes** in use: `cli`, `engine`, `github`, `infra`, `model`, `web`.
- **Dependencies** are GitHub's blocked-by relationships, never lines in the body.
- **Forms:** `.github/ISSUE_TEMPLATE/task.yml` and `bug.yml` produce this shape on github.com. Drafts written to `.tmp/` and created with `gh issue create --body-file` use the same sections.

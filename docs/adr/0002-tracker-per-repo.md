# ADR 0002: The tool has its own repo; `.tracker/` lives in the repo it plans

<a id="status"></a>
## 1. Status

Proposed.

<a id="context"></a>
## 2. Context

`gh-plan` is a general-purpose tool with no project-specific content. It has its own tests,
versioning and release cycle, and anyone can install it without the projects that use it.

Planning data belongs to the project it plans. Under [ADR 0001](0001-git-is-the-database.md) that
data is committed files, and it is the evidence [`G1`](../requirements.md) is about, so it should
sit in git beside the work it describes.

<a id="decision"></a>
## 3. Decision

The tool lives in its own repo, `gh-plan`.

Each planned project keeps its own `.tracker/` directory in its own repo. When one plan covers
several repos ([`A1`](../requirements.md)), its `.tracker/` lists them in `config.repos`. The tool
finds `.tracker/` by walking up from the working directory
([design 0001, *Discovery*](../design/0001-phase-1.md#discovery)).

<a id="alternatives"></a>
## 4. Alternatives considered

- Data in the tool's repo. One project's planning data would sit inside a general-purpose tool,
  every user's data would compete for the same place, and a change to the plan would look like a
  change to the tool.
- One central hub repo holding the data for every project. The data would be separated from the
  work it plans, each project would depend on a second repo for its own evidence, and one repo
  would be privileged over the others it tracks.

<a id="consequences"></a>
## 5. Consequences

- The tool's repo carries its own Claude Code settings and attribution hook, because that
  configuration does not inherit from directories outside the repo
  ([design 0001, *Naming*](../design/0001-phase-1.md#naming)).
- The tool's own repo is planned with its own `.tracker/`, so its backlog is the first thing it
  tracks.
- The tool can be released and installed independently of any project's data.
- A plan that spans repos has one home. The other repos it lists hold no planning data.

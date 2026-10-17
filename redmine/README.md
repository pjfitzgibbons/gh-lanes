# Redmine

The tracker of [ADR 0011](../docs/adr/0011-redmine-is-the-tracker.md): Redmine 7.0 in Docker on
localhost, on SQLite, with the [lane board](plugins/lane_board/README.md) loaded. Run every
command here from the root of the gh-plan checkout.

| File | Holds |
|---|---|
| `compose.yml` | The service: the pinned image, the port, the volumes and the mounts |
| `setup.rb` | The projects, fields, status, workflow, settings, repositories and versions |
| `plugins/lane_board/` | The lane board plugin, mounted read-only |

## Starting and stopping

```
docker compose -f redmine/compose.yml up -d     # start; first start creates the database
docker compose -f redmine/compose.yml stop      # stop, keeping the container
docker compose -f redmine/compose.yml down      # stop and remove the container; data stays
docker compose -f redmine/compose.yml logs -f   # follow the log
```

Redmine is at <http://127.0.0.1:3010>, bound to localhost only. `REDMINE_PORT` picks another
port. The first sign-in is `admin` / `admin`, and Redmine makes you change the password at once.
Nothing in the repo holds the new password or any API key.

Each tracked repo's `.git` is mounted read-only, from `$HOME/programming/gh-plan/.git` and
`$HOME/programming/tempotag/.git`. `GH_PLAN_GIT` and `TEMPOTAG_GIT` point them elsewhere. Mount a
checkout's `.git` directory, not a worktree: a worktree's `.git` is a file naming a path on the
Mac, which the container can't follow.

## Where the data lives

Two named volumes of the `gh-plan-redmine` compose project:

| Volume | Mounted at | Holds |
|---|---|---|
| `gh-plan-redmine_db` | `/usr/src/redmine/sqlite` | `redmine.db`, the whole database |
| `gh-plan-redmine_files` | `/usr/src/redmine/files` | Attachments |

`down` keeps them; `down -v` deletes them, and with them every issue. Backup and export are
pl-pakiz's.

## Running the setup

After the first start, and after any change to `setup.rb`:

```
docker compose -f redmine/compose.yml exec -u redmine redmine bin/rails runner /setup/setup.rb
```

It prints each thing it makes or changes, then a count, or `nothing to change` when the Redmine
already matches. Re-running it is always safe: it runs in one transaction, makes only what is
missing, and leaves alone what it doesn't own, such as a version's status or description once
made. It needs no API key, because it works on the database from inside the container.

What it sets up:

- A private parent project `plan`, with sub-projects `gh-plan` and `tempotag`, each with the
  lane board, Gantt and repository modules.
- The default trackers, statuses, roles and workflows, on an empty database.
- An `Icebox` status, open, with the transitions of New in each workflow, so it opens no route a
  role lacks. The lane board leaves it out.
- The issue custom fields `Points` (1, 2, 3, 5, 8, 13), `Lane` (cli, engine, github, infra, model,
  web), and the dates `Baseline start` and `Baseline finish`.
- The baselines read-only, by workflow, for every role. A `Baseline editor` role, with no members,
  keeps them editable by the administrator, who holds every role in workflow checks.
- **View lane board** for every role.
- The REST API, cross-project relations and cross-project commit references switched on.
- `refs` as the commit keyword that links an issue, and `fixes` as the one that closes it.
- Each repo registered as its project's Git repository, at `/repos/<project>.git`.
- One version per milestone in `plan`, shared with its tree.

## Upgrading

1. Read the Redmine changelog for every release between the two tags.
2. Change `image:` in `compose.yml` to the new tag. Pin an exact tag such as `7.0.3`, never `7.0`.
3. Back up the `db` volume.
4. `docker compose -f redmine/compose.yml up -d`. The image migrates the database on start.
5. Check that *Administration › Plugins* still lists the lane board, and its tab still loads.
6. Re-run the setup, which should print `nothing to change`.

Anything that recreates the container signs everyone out: an upgrade, `down` then `up`, or a
change to `compose.yml`. The session secret is generated inside the container, so a new
container makes a new one.

## Commits and closing

Redmine reads a repository's new commits only when someone opens its Repository tab, so a
`fixes #<n>` commit closes the issue at that fetch, not when it is committed. The issue's
`closed_on` is the fetch time; the commit's time is the changeset's `committed_on`.
Opening the tab fetches now. Fetching after each merge is pl-sijil's, in the icebox.

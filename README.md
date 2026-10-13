# gh-plan

A planning layer over GitHub Issues. A local CLI, `plan`, keeps estimates, lanes, priorities and
frozen baselines in JSON files committed to your repo. GitHub Issues keeps titles, state, labels and
dependencies. It is not an issue tracker.

The design is in [`docs/architecture.md`](docs/architecture.md) and
[`docs/design/`](docs/design/).

> **Status:** in development. The `plan` CLI and the time-tracker integration are not built yet
> ([#61](https://github.com/pjfitzgibbons/gh-plan/issues/61), [#62](https://github.com/pjfitzgibbons/gh-plan/issues/62)). The instructions below describe how they are
> designed to work.

## Time tracking

gh-plan can compare each item's estimate with the time you actually spent on it. It reads time
entries from an external time tracker, adds them up when the item's issue closes, and stores the
total in the item file. `plan report time` then puts estimates and actuals side by side.

gh-plan only reads from the time tracker. It never starts, stops or edits a timer.

The first supported tracker is [Timewarrior](https://timewarrior.net/).

### Install

1. Install Timewarrior:

   ```sh
   brew install timewarrior        # macOS; see timewarrior.net for other platforms
   ```

2. Make sure `gh` is installed and logged in (`gh auth status`). gh-plan reaches GitHub only
   through `gh`, and never asks for a token of its own.

3. Turn time tracking on by adding two keys to `.tracker/config.json`:

   ```json
   "hours_per_point": 8.0,
   "time_source": {
     "kind": "timewarrior"
   }
   ```

   `hours_per_point` of 8.0 makes one point one working day. Set 1.0 if a point is an hour. With no `time_source` key, time tracking is off and nothing else changes.

4. Install the git hooks, from the repo that holds `.tracker/`:

   ```sh
   plan hooks install
   ```

   This writes a `post-merge` hook into every repo in `config.repos`, which reports closed issues
   after you pull any of them, and a `pre-commit` hook in this repo, which runs `plan validate`.
   The hooks are small Python scripts that call `plan` by its full path, because git hooks often
   run without your shell's `PATH`. If you reinstall or move `plan`, run `plan hooks install`
   again. A configured repo that isn't cloned at its `path` is skipped; run the install again
   after you clone it.

   If a hook already exists and gh-plan didn't write it, the command leaves it alone and prints
   the lines for you to add yourself.

### Track time against an issue

A time entry counts toward an issue when it has the tag `<owner>/<repo>#<number>`:

```sh
timew start "example-org/web-app#23"
# ... work ...
timew stop
```

`plan show 23` prints the tag, so you can copy it instead of typing it. If more than one
configured repo has an issue #23, name the repo: `plan show web-app#23`. The same goes for every
command below that takes an issue number.

An entry can have other tags as well. An entry with two issue tags counts in full toward both
issues, so if you want to split time between issues, split the entry in Timewarrior.

Anything that writes this tag works, including a script that starts Timewarrior for you from the
branch you're on (`23-fix-login` → `example-org/web-app#23`).

### When an issue closes

1. Merge the PR with `Closes #23` in its description. GitHub closes the issue.
2. Pull `main`. The `post-merge` hook checks for closed issues and prints what is pending, for
   example:

   ```
   #23 closed → Done, 4.25 h from 7 entries
   ```

   The hook doesn't change any files.
3. On a branch, record the time:

   ```sh
   git switch -c tracker/close-23
   plan reconcile --closed --apply
   git commit -am "Close #23"
   ```

   This marks the item `Done` and saves the total in `.tracker/items/web-app/23.json`.
   Merge the branch as usual.

If you pull with `--rebase` (or have `pull.rebase` set), git skips the `post-merge` hook. Run
`plan reconcile --closed` yourself to see what is pending.

### Check an item's time

```sh
plan time 23             # saved total, the current total from Timewarrior, and the difference
plan time 23 --apply     # replace the saved total with the current one
```

`plan time N --apply` also works on an open issue, for a mid-way check you can commit. Time logged
after an issue closed is only counted once you run it.

### Report

```sh
plan report time
plan report time --milestone beta
plan report time --json
```

The report lists each item's estimate in points and hours, its actual hours and the difference. The
last line compares the configured `hours_per_point` with the value your actual data implies. If the
two stay far apart, change `hours_per_point` in the config. Old reports rescale, because estimated
hours are computed when the report runs and never stored.

Items with no saved total are listed, but left out of the totals.

### Troubleshooting

`plan validate` warns about:

| Warning | What to do |
|---|---|
| `#N is Done with no tracked time` | Timewarrior couldn't be read when the item closed. Run `plan time N --apply` |
| `#N is Done with 0 tracked entries for owner/repo#N` | No entry had that tag. Check the tag in Timewarrior with `timew summary :all owner/repo#N` |
| `#N had 1 timer running at snapshot` | A timer was still running, and running timers are not counted. Stop it, then run `plan time N --apply` |

A transferred issue has a new tag, so entries tagged with the old one aren't found yet.

# gh-plan

## Contents

- [Time tracking](#time-tracking)
  - [Install](#install)
  - [Track time against an item](#track-time-against-an-item)
  - [When an item is Done](#when-an-item-is-done)
  - [Check an item's time](#check-an-items-time)
  - [Report](#report)
  - [Troubleshooting](#troubleshooting)

A file-native tracker. A local CLI, `plan`, keeps each item's title, status, estimate, lane,
priority, milestone and dependencies in a Markdown file with YAML front matter, committed in the
repo the item belongs to. GitHub Issues isn't used. Pull requests are the one GitHub integration.

The design is in [`docs/architecture.md`](docs/architecture.md) and
[`docs/design/`](docs/design/).

> **Status:** in development. The `plan` CLI and the time-tracker integration are not built yet.
> The instructions below describe how they are designed to work.

## Time tracking

gh-plan can compare each item's estimate with the time you actually spent on it. It reads time
entries from an external time tracker, adds them up when the item is set Done, and stores the
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

3. Turn time tracking on by adding two keys to `.tracker/config.yml`:

   ```yaml
   hours_per_point: 8.0
   time_source:
     kind: timewarrior
   ```

   `hours_per_point` of 8.0 makes one point one working day. Set 1.0 if a point is an hour. With no `time_source` key, time tracking is off and nothing else changes.

4. Install the git hooks, from the repo that holds `.tracker/`:

   ```sh
   plan hooks install
   ```

   This writes three hooks into every repo of the plan: `post-checkout`, which starts an item when
   you create its branch; `post-merge`, which reports Done items with no saved time after you pull;
   and `pre-commit`, which runs `plan validate`.
   The hooks are small Python scripts that call `plan` by its full path, because git hooks often
   run without your shell's `PATH`. If you reinstall or move `plan`, run `plan hooks install`
   again. A member repo that isn't cloned at its path is skipped; run the install again after you
   clone it.

   If a hook already exists and gh-plan didn't write it, the command leaves it alone and prints
   the lines for you to add yourself.

### Track time against an item

A time entry counts toward an item when it has the item's ID as a tag:

```sh
timew start wa-tunep
# ... work ...
timew stop
```

The prefix (`wa`) belongs to one repo, so an ID tags one item wherever the timer runs.

An entry can have other tags as well. An entry with two item tags counts in full toward both
items, so if you want to split time between items, split the entry in Timewarrior.

Anything that writes this tag works, including a script that starts Timewarrior for you from the
branch you're on (`feat/wa-tunep-retry` → `wa-tunep`).

### When an item is Done

1. On the item's branch, before it merges, set it Done:

   ```sh
   plan set wa-tunep --status Done
   ```

   This writes `status: Done` and the total from Timewarrior into `.tracker/items/wa-tunep.md` in
   one write. Commit it with the work, and it reaches the default branch with the merge.
2. If the item was set Done without a total, by hand in an editor or while Timewarrior couldn't
   be read, the `post-merge` hook reports it when you pull the merge, for example:

   ```
   wa-tunep is Done with no snapshot · 4.25 h from 7 entries
   ```

   The hook doesn't change any files. On a branch, run `plan time wa-tunep --apply` and commit it.

If you pull with `--rebase` (or have `pull.rebase` set), git skips the `post-merge` hook. Run
`plan time --missing` yourself to see what is pending.

### Check an item's time

```sh
plan time wa-tunep            # saved total, the current total from Timewarrior, and the difference
plan time wa-tunep --apply    # replace the saved total with the current one
plan time --missing           # Done items with no saved total, and what each would get
```

`plan time <id> --apply` also works on an item that isn't Done yet, for a mid-way check you can
commit. Time logged after an item is Done is only counted once you run it.

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
| `wa-tunep is Done with no tracked time` | Timewarrior couldn't be read when the item was set Done. Run `plan time wa-tunep --apply` |
| `wa-tunep is Done with 0 tracked entries tagged wa-tunep` | No entry had that tag. Check the tag in Timewarrior with `timew summary :all wa-tunep` |
| `wa-tunep had 1 timer running at snapshot` | A timer was still running, and running timers are not counted. Stop it, then run `plan time wa-tunep --apply` |

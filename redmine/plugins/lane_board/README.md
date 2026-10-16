# Lane board

A Redmine 7.0 plugin that adds a **Lanes** tab to a project. The tab shows the issues of the
project and its sub-projects with lanes as rows and statuses as columns. Each lane's row heading
totals its open points, counting leaf issues only, so a parent never counts its sub-tasks twice.
An issue is marked **ready** when it is open and every issue that blocks it is closed.

The plugin only reads. It writes no issue, custom field or relation, and has no database
migration.

## Custom fields it needs

Both are issue custom fields, found by name. An administrator adds them under
*Administration › Custom fields › New custom field › Issues*.

| Name | Format | Needed | Without it |
|---|---|---|---|
| `Lane` | List, single value | Yes | The tab shows a message saying the field is missing |
| `Points` | List: 1, 2, 3, 5, 8, 13 | No | Every issue shows `? pts`, and each lane totals 0 |

An issue with no lane goes in the `(no lane)` row; one with no points shows `? pts` and adds
nothing to its lane's total. Make both fields available to the trackers and projects the board
should cover.

## Mounting it

Redmine loads plugins from `plugins/` under its root, `/usr/src/redmine` in the official image.
Mount this folder there, read-only, and restart Redmine:

```
docker run -d --name redmine -p 3000:3000 \
  -v "$PWD/redmine/plugins/lane_board:/usr/src/redmine/plugins/lane_board:ro" \
  redmine:7.0
```

Run it from the root of the gh-plan checkout. The plugin has no migration, so
`rake redmine:plugins:migrate` is not needed. *Administration › Plugins* lists it as "Lane board"
once it has loaded.

## Turning it on

1. In each project, *Settings › Modules*: tick **Lane board**. A sub-project needs it
   ticked too for its own tab; the parent's tab already shows the sub-project's issues.
2. In *Administration › Roles and permissions*: give each role that should see the tab
   **View lane board**.
3. In *Administration › Settings › Issue tracking*: tick **Allow cross-project issue relations**.
   It is off by default, and without it an issue can be blocked only by one in its own project,
   so the board's ready marks never see a blocker in a sibling project.

The tab is at `/projects/<identifier>/lanes`.

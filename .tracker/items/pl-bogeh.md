---
title: "index.py: SQLite build, v_work view, plan reindex"
type: feat
status: Icebox
estimate: 3
priority: P2
ordinal: 10700
lane: engine
milestone: phase-1
---
Rebuilt wholesale, never incrementally. DDL in design 0001 *Index*. The `dep` table is filled from the pulled blocked-by edges, keyed by `node_id`, not from item files.

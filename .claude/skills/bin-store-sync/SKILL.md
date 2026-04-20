---
name: bin-store-sync
description: Bin store Grist sync. Trigger when the user says "sync Grist", "refresh the cut list", "push the cut list", "pull inventory", "sync bin store tables", or "update Grist from the repo". Regenerates the cut list from the OpenSCAD model and then syncs every Grist table in its default direction — cut_list and shopping_list push local → Grist (preserving the `completed` checkbox across pushes); inventory pulls Grist → local. Use this before running bin-store-shopping or any time the OpenSCAD model has changed.
allowed-tools:
  [
    Bash(python3 scripts/extract_cut_list.py*),
    Bash(python3 scripts/sync_grist_tables.py*),
    Read(data/cut_list.json),
    Read(data/inventory.json),
  ]
---

# bin-store-sync

Thin orchestrator for the repo ↔ Grist data flow. Does not touch shopping or supplier lookup — that lives in `bin-store-shopping`.

## Preconditions

- **Working directory:** the repo root, `/Users/chuck/workspace/diy-projects`. `cd` there if needed.
- **Env vars:** `GRIST_API_KEY`, `GRIST_DOC_ID` (optional `GRIST_BASE_URL`). If unset, stop and tell the user which one is missing — do not attempt a partial sync.

## Direction rules (enforced by the sync script)

| Table           | Direction     | Notes                                                                |
| --------------- | ------------- | -------------------------------------------------------------------- |
| `cut_list`      | local → Grist | Pulls `completed` column first, merges, rewrites local, then pushes. |
| `shopping_list` | local → Grist | Pushed only.                                                         |
| `inventory`     | Grist → local | Pulled only.                                                         |

Running `sync_grist_tables.py` with no `--table` flag syncs all three.

## Actions

### Default — full refresh (most common)

```bash
python3 scripts/extract_cut_list.py
python3 scripts/sync_grist_tables.py
```

Regenerates the cut list from the OpenSCAD model, then syncs every registered table. Report:

- cut_list row count
- how many `completed: true` rows were preserved
- inventory row count pulled back
- confirmation that pushes succeeded

### Single table

If the user asks to sync just one table:

```bash
python3 scripts/sync_grist_tables.py --table <cut_list|shopping_list|inventory>
```

Skip the `extract_cut_list.py` step unless they asked for `cut_list` — that's the only table that depends on regenerating the OpenSCAD output first.

### Skip the OpenSCAD extraction

If the user wants to sync without regenerating (e.g. "just push what's in the repo to Grist"), omit `extract_cut_list.py` and only run the sync. Say so explicitly in the reply so they know the cut list was not regenerated.

## Error handling

- **`GristApiError`** — check env vars → network → Grist doc permissions. Do not retry destructively.
- **Extraction fails on a .scad parse error** — means `bin-store-model/parameters.scad` was edited in a way the extractor cannot evaluate. Report the traceback and stop; do not modify the extractor or the .scad file to make the error go away.
- **Nothing to push (empty local snapshot)** — report it; do not silently succeed.

## Cowork notes

When run via Cowork's proxy skill, keep the final reply to one short paragraph with the four numbers (cut_list rows, completed preserved, inventory rows, shopping_list rows if pushed).

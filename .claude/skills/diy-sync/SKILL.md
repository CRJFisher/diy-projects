---
name: diy-sync
description: DIY project Grist sync. Trigger when the user says "sync Grist", "refresh the cut list", "push the cut list", "pull inventory", "sync bin store tables", "sync courtyard", or "update Grist from the repo". Regenerates the cut list from the project's OpenSCAD model and syncs tables — cut_list and shopping_list push local → Grist (preserving completed/acquired); shared inventory pulls Grist → shared/inventory. Requires a project slug (bin-store, courtyard-nook). Use before diy-shopping or after model changes.
allowed-tools:
  [
    Bash(python3 scripts/extract_cut_list.py*),
    Bash(python3 scripts/sync_grist_tables.py*),
    Read(projects/*/data/cut_list.json),
    Read(shared/inventory/inventory.json),
  ]
---

# diy-sync

Thin orchestrator for repo ↔ Grist. Does not touch supplier lookup — that lives in `diy-shopping`.

## Preconditions

- **Working directory:** the diy-projects repo root (directory containing `projects/` and `shared/`). `cd` there if needed.
- **Project slug:** required. Infer from the user's wording (`bin store` → `bin-store`, `courtyard` → `courtyard-nook`). If ambiguous, ask.
- **Env vars:** `GRIST_API_KEY`, `GRIST_DOC_ID` (optional `GRIST_BASE_URL`). If unset, stop and tell the user which one is missing.

## Direction rules

| Table           | Direction     | Notes                                                      |
| --------------- | ------------- | ---------------------------------------------------------- |
| `cut_list`      | local → Grist | Project-scoped; PKs namespaced as `{project}__{cut_id}`    |
| `shopping_list` | local → Grist | Project-scoped                                             |
| `inventory`     | Grist → local | Shared workshop stock at `shared/inventory/inventory.json` |

## Actions

### Default — full refresh

```bash
python3 scripts/extract_cut_list.py --project <slug>
python3 scripts/sync_grist_tables.py --project <slug>
```

Report cut_list row count, how many `completed: true` rows were preserved, inventory row count, and push confirmation.

### Single table

```bash
python3 scripts/sync_grist_tables.py --project <slug> --table <cut_list|shopping_list|inventory>
```

Skip extract unless syncing `cut_list`.

### Skip OpenSCAD extraction

If the user wants to push without regenerating, omit `extract_cut_list.py` and say so explicitly.

## Error handling

- **`GristApiError`** — check env vars → network → doc permissions. Do not retry destructively.
- **Extraction fails** — report the traceback and stop; do not patch the extractor or `.scad` to silence it.
- **Empty local snapshot** — report it; do not silently succeed.

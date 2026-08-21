# DIY Projects

Multi-project workshop repo. Each build lives under `projects/<slug>/`; shared inventory, Grist helpers, and store adapters live under `shared/`.

## Projects

| Slug             | Path                                                 | Notes                                                      |
| ---------------- | ---------------------------------------------------- | ---------------------------------------------------------- |
| `bin-store`      | [projects/bin-store/](projects/bin-store/)           | Outdoor bin store — design constraints in its `CLAUDE.md`  |
| `courtyard-nook` | [projects/courtyard-nook/](projects/courtyard-nook/) | Courtyard nook roofing — site measured, build not designed |

## OpenSCAD

OpenSCAD is installed locally. Cheat sheet: [shared/openscad/OpenSCAD CheatSheet.htm](shared/openscad/OpenSCAD%20CheatSheet.htm).

**Tip:** After opening a `.scad` file, press **F5** to preview, then use **View > View All** (or the toolbar button) to zoom the camera to fit the entire model. Without this, the viewport may appear blank.

## Shared inventory and Grist

One Grist document holds:

- `inventory` — workshop-wide stock (snapshot: `shared/inventory/inventory.json`)
- `cut_list` / `shopping_list` — scoped by `project_id`; primary keys are `{project_id}__{local_id}` in Grist

When computing a shopping list for project P, incomplete cuts from other projects reserve stock first so two projects cannot both claim the same stick.

```bash
python3 scripts/extract_cut_list.py --project bin-store
python3 scripts/sync_grist_tables.py --project bin-store
python3 scripts/compute_shopping_list.py --project bin-store
```

Env: `GRIST_API_KEY`, `GRIST_DOC_ID` (optional `GRIST_BASE_URL`). See [docs/grist_inventory_workflow.md](docs/grist_inventory_workflow.md).

## Tooling

- `shared/grist/` — Python package (`grist`) for snapshots, sync, shortfall / reservation
- `tooling/adapter-builder/` — Stagehand + Playwright recorder for `build-store-adapter`
- `shared/store_adapters/<slug>/` — generated per-site search adapters

Skills: `diy-sync`, `diy-shopping`, `build-store-adapter`.

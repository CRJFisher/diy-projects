# Courtyard Nook

Roofing / enclosure for a courtyard nook.

## Site envelope (looking into the nook from the courtyard)

All notes were in cm; OpenSCAD uses mm (`×10`). Source of truth: `model/parameters.scad`.

## Layout

- `model/` — OpenSCAD parametric model (`parameters.scad`, `walls.scad`, `courtyard_nook.scad`)
- `extraction.py` — cut-list mapping from parameters (to be added when the build is designed)
- `data/` — `cut_list.json`, `shopping_list.json`, `substitution_candidates.json`

Shared workshop inventory: `../../shared/inventory/inventory.json`.

```bash
python3 scripts/extract_cut_list.py --project courtyard-nook
python3 scripts/sync_grist_tables.py --project courtyard-nook
python3 scripts/compute_shopping_list.py --project courtyard-nook
```

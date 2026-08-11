# Courtyard Nook

Roofing / enclosure for a courtyard nook. Design constraints and OpenSCAD model are TBD.

## Layout

- `model/` — OpenSCAD parametric model (to be added)
- `extraction.py` — cut-list mapping from parameters (to be added)
- `data/` — `cut_list.json`, `shopping_list.json`, `substitution_candidates.json`

Shared workshop inventory: `../../shared/inventory/inventory.json`.

```bash
python3 scripts/extract_cut_list.py --project courtyard-nook
python3 scripts/sync_grist_tables.py --project courtyard-nook
python3 scripts/compute_shopping_list.py --project courtyard-nook
```

---
name: diy-shopping
description: DIY project procurement workflow. Trigger when the user asks "what do I need to buy", "refresh the shopping list", "find products for the bin store", "bin store shopping", "courtyard shopping", "check materials to order", or "can I use my existing X instead of Y". Pulls shared inventory from Grist, reserves stock for other projects' incomplete cuts, computes outstanding cuts for the active project, proposes substitutions within ±10mm, then searches B&Q and pushes the shopping list. Requires a project slug (bin-store, courtyard-nook).
allowed-tools:
  [
    Bash(python3 scripts/sync_grist_tables.py*),
    Bash(python3 scripts/compute_shopping_list.py*),
    Bash(python3 scripts/extract_cut_list.py*),
    Read(projects/*/data/cut_list.json),
    Read(shared/inventory/inventory.json),
    Read(projects/*/data/shopping_list.json),
    Read(projects/*/data/substitution_candidates.json),
    Edit(projects/*/model/parameters.scad),
    Edit(projects/*/data/shopping_list.json),
  ]
---

# diy-shopping

Turns the gap between a project's `cut_list` and shared `inventory` into a B&Q shopping list, then syncs it to Grist.

## Preconditions

- **Working directory:** diy-projects repo root.
- **Project slug:** required (`bin-store`, `courtyard-nook`, …). Infer from user wording; ask if unclear.
- **Env vars:** `GRIST_API_KEY`, `GRIST_DOC_ID` (optional `GRIST_BASE_URL`).
- **Browser tool** for B&Q search (Cowork Chrome automation, or WebFetch + user confirm in CLI).

## Workflow

### Step 1 — Sync first

```bash
python3 scripts/sync_grist_tables.py --project <slug>
```

Pushes that project's cut/shopping lists; pulls shared inventory.

### Step 2 — Compute outstanding cuts

```bash
python3 scripts/compute_shopping_list.py --project <slug>
```

Reserves inventory for other projects' incomplete cuts, then writes:

- `projects/<slug>/data/shopping_list.json`
- `projects/<slug>/data/substitution_candidates.json`

If zero shopping rows, stop — nothing to buy.

### Step 2.5 — Substitution candidates (if any)

Read `projects/<slug>/data/substitution_candidates.json`. Empty → Step 3.

**Headless / Cowork proxy:** do not edit scad; list candidates for the user and continue to Step 3.

**bin-store forbidden swaps** (never propose): `post_face`, `post_side`, `rail_h`, `batten_h`, envelope dims (`total_width`, `total_depth`, `front_height`, `back_height`, `mid_rail_height`, `internal_depth`, `left_section_clear`, `right_section_width`), and physical object dims (`wheelie_*`, `caddy_w`, `recycle_*`). See `projects/bin-store/CLAUDE.md`.

**Safer-to-propose (bin-store):** `brace_t`, `brace_w`, `ply_t`, `hardboard_t`, `featheredge_w`, `featheredge_thick`, `door_frame_w`, `door_frame_t`.

For approved swaps only: edit `projects/<slug>/model/parameters.scad`, then:

```bash
python3 scripts/extract_cut_list.py --project <slug>
python3 scripts/sync_grist_tables.py --project <slug> --table cut_list
python3 scripts/compute_shopping_list.py --project <slug>
```

Do not loop substitution more than once per run.

### Step 3 — Search B&Q

For each row with `status == "needs_product"` in `projects/<slug>/data/shopping_list.json`, search diy.com, prefer in-stock → lowest £/m → nearest section. Stock length ≥ `min_stock_length_mm`.

### Step 4 — Update local shopping list

Set `supplier`, `stock_length_mm`, `individual_units`, `pack_size`, `purchase_units`, `url`, `notes`, `status` (`ready` / `ambiguous` / `unavailable`). Do not change derived cut fields.

### Step 5 — Push shopping_list

```bash
python3 scripts/sync_grist_tables.py --project <slug> --table shopping_list
```

## Error handling

- **`GristApiError`** — check env → network → permissions; no destructive retries.
- **No B&Q match** — `status: "unavailable"` with a short note.
- **Extract fails after scad edit** — do not sync; revert session edits; stop.
- **Mid-loop sync fails** — stop; user can rerun `diy-sync` later.

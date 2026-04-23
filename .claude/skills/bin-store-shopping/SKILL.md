---
name: bin-store-shopping
description: Bin store procurement workflow. Trigger when the user asks "what do I need to buy", "refresh the shopping list", "find products for the bin store", "bin store shopping", "check the bin store materials to order", or "can I use my existing X instead of Y". Pulls the latest inventory from Grist, computes outstanding cuts (cut list minus inventory with greedy fit), proposes inventory substitutions within ±10mm tolerance and — with user approval — edits `parameters.scad` and regenerates before shopping, then searches B&Q for each remaining row and pushes the shopping list back to Grist. Designed for Cowork (uses Chrome browser automation) but also works in Claude Code CLI with WebFetch for single pages.
allowed-tools:
  [
    Bash(python3 scripts/sync_grist_tables.py*),
    Bash(python3 scripts/compute_shopping_list.py*),
    Bash(python3 scripts/extract_cut_list.py*),
    Read(data/cut_list.json),
    Read(data/inventory.json),
    Read(data/shopping_list.json),
    Read(data/substitution_candidates.json),
    Edit(bin-store-model/parameters.scad),
    Edit(data/shopping_list.json),
  ]
---

# bin-store-shopping

Turns the current gap between `cut_list` and `inventory` into a B&Q shopping list with product links, then syncs it to Grist.

## Preconditions

- **Working directory:** the repo root, `/Users/chuck/workspace/diy-projects`. `cd` there if needed.
- **Env vars** for the sync step: `GRIST_API_KEY`, `GRIST_DOC_ID` (and optional `GRIST_BASE_URL`). If unset, stop and tell the user which one is missing.
- **Browser tool** is required to search B&Q. In Cowork this is the built-in Chrome automation; in Claude Code CLI, fall back to WebFetch against direct product URLs and ask the user to confirm matches.

## Workflow

### Step 1 — Sync first (pull latest inventory, push any pending cut list)

```bash
python3 scripts/sync_grist_tables.py
```

This runs every table in its default direction: `cut_list` + `shopping_list` pushed, `inventory` pulled. Running shopping against stale inventory produces wrong shortfalls, so do not skip this step.

### Step 2 — Compute the outstanding cuts

```bash
python3 scripts/compute_shopping_list.py
```

Reads `data/cut_list.json` (incomplete rows only) and `data/inventory.json`, runs a greedy per-cut fit with 3 mm kerf and 150 mm minimum usable offcut, and writes:

- `data/shopping_list.json` — one row per unmet cut, with a stable `shopping_id`, dimensions, `qty_needed`, and empty `supplier`/`notes`/`status: "needs_product"`.
- `data/substitution_candidates.json` — for each unmet cut, any inventory in the same `material_type` whose section dims are within ±10 mm on every dimension. Empty `substitutions` list means nothing close is in stock; tolerance is `--tolerance-mm` if you need to widen it.

Read the shopping list and report how many outstanding rows there are and the unique `section_key` values. If zero rows, stop — nothing to buy — and tell the user.

### Step 2.5 — Review substitution candidates (only if the file lists any)

Read `data/substitution_candidates.json`. If `substitutions` is empty, skip to Step 3.

**Headless mode (Cowork's proxy skill):** do NOT attempt this step. There is no user to answer go/no-go. Include the candidates verbatim in the final reply with a "user action required before rerun" note, and proceed to Step 3 with the shopping list as-is.

**Forbidden swaps — reject outright, never propose to the user:**

These parameters are load-bearing for the 1300mm width budget, the 1550mm internal height clearance, or shelf geometry documented in CLAUDE.md. Swapping any of them silently violates a constraint that is not rechecked anywhere:

- `post_face` (47mm) — appears in `full_rail_length`, `right_front_bot_rail`, `front_centre_post_x`, and the CLAUDE.md width equation `47 + 490 + 323 + 440 = 1300`.
- `post_side` (50mm) — front panel overlap and right-front cladding width.
- `rail_h` — drives `centre_post_height = front_height − 2·rail_h` AND `shelf_thickness = rail_h + batten_h`, which is assumed by the hard-coded `shelf_space = 448`.
- `batten_h` — same `shelf_thickness` trap. Only propose if the user has confirmed shelf height can shift.
- `total_width`, `total_depth`, `front_height`, `back_height`, `mid_rail_height`, `internal_depth`, `left_section_clear`, `right_section_width` — overall envelope.
- `wheelie_w`, `wheelie_d`, `wheelie_h`, `caddy_w`, `recycle_w`, `recycle_d`, `recycle_h` — physical objects; not a design choice.

If every candidate in the file maps to a forbidden parameter, tell the user the candidates exist but cannot be safely swapped without redesign, and proceed to Step 3.

**Safe-to-propose parameters:** `brace_t`, `brace_w`, `ply_t`, `hardboard_t`, `featheredge_w`, `featheredge_thick`, `door_frame_w`, `door_frame_t`. Even these warrant a one-line impact note — e.g. `door_frame_w` feeds `door_rail` length via `door_width − 2·door_frame_w`, and can drive it negative for large swaps.

**For each remaining (non-forbidden) candidate:**

1. Note the `design_section_key` vs. `inventory_section_key`, `max_dim_delta_mm`, `needed_cuts`, and `inventory_available`.
2. Add a one-line structural-impact note before presenting. If unsure, say so rather than guessing.
3. Present the swap to the user and ask go/no-go. Do not edit the scad silently.
4. If the user declines, leave `parameters.scad` untouched; the corresponding shopping-list row stays and flows into Step 3 as normal.
5. For each approved swap, `Edit` the matching parameter in [bin-store-model/parameters.scad](bin-store-model/parameters.scad) (e.g. `batten_h = 22` → `batten_h = 18`). Only change the one parameter that drives the swap — derived values propagate at extraction time.
6. After **all** approved edits are made (batch them, do not loop one-at-a-time), regenerate and re-sync only the tables that changed:

   ```bash
   python3 scripts/extract_cut_list.py
   python3 scripts/sync_grist_tables.py --table cut_list
   python3 scripts/compute_shopping_list.py
   ```

   Scoping the sync to `--table cut_list` avoids re-pushing unrelated tables mid-workflow. The `completed` checkbox is reset automatically for any row whose dimensions drifted — the workshop should not trust a "completed" flag after a section change.

7. Re-read the regenerated `data/substitution_candidates.json`. If it is still non-empty, **do not loop again** — proceed to Step 3 with whatever shopping-list rows remain. A second loop risks chasing the inventory ↔ design until something gets swapped that shouldn't. Tell the user there are further candidates they can action in a fresh run.

### Step 3 — Search B&Q for each row

For each row in `data/shopping_list.json` where `status == "needs_product"`:

1. Build a search query from `material_type` + `section_key` + the required length (e.g. `"CLS timber 50x47 2.4m"`, `"featheredge cladding 125mm"`, `"plywood exterior 18mm"`). Prefer slightly longer stock lengths — B&Q sells common sizes like 2.4 m, 3.0 m, 3.6 m.
2. Search B&Q (`https://www.diy.com`) using the browser tool. If multiple matches, prefer: in-stock → lowest price per metre → exact or nearest section size.
3. Capture the product URL.

### Step 4 — Update the local shopping list

For each row you found a product for, use `Edit` on `data/shopping_list.json` to set:

- `supplier`: `"B&Q"`
- `notes`: the product URL (and a short product name if it fits on one line)
- `status`: `"ready"` if a good match was found, `"ambiguous"` if the best candidate is uncertain and the user should review, `"unavailable"` if no suitable product exists.

Do not change any other fields — they were computed from the cut list and must stay in sync with the source of truth.

### Step 5 — Push shopping_list back to Grist

```bash
python3 scripts/sync_grist_tables.py --table shopping_list
```

Report the upserted/deleted counts and confirm the Grist `shopping_list` table is updated. Include a one-line summary: total rows, rows ready, rows ambiguous, rows unavailable.

## Error handling

- **`GristApiError`** — check env vars → network → doc permissions. Do not retry destructively.
- **B&Q search returns nothing plausible** — leave `status: "unavailable"`, `notes` with a short reason. Don't invent products.
- **Ambiguous matches** — prefer `status: "ambiguous"` over guessing; the user can disambiguate in Grist before ordering.
- **Shopping list has zero rows after compute** — existing inventory satisfies all incomplete cuts. Tell the user and stop; don't push an empty list blindly.
- **All substitution candidates rejected / every candidate is forbidden** — proceed to Step 3 as if Step 2.5 had not run; report the rejection count in the final reply.
- **`extract_cut_list.py` fails after a scad edit** — the repo is in a half-edited state. Do NOT run sync. Show the traceback, revert the `parameters.scad` edit(s) made in this session, and stop. The user fixes the scad issue manually before rerunning.
- **Mid-loop sync fails after a scad edit** — the local `cut_list.json` is fresh but Grist is stale. Stop; do not retry blindly. The user can rerun `bin-store-sync` once the cause (network, permissions) is cleared.
- **Substitution candidates re-appear after one regen loop** — do not loop again in this run. Report them and proceed to Step 3.

## Cowork notes

When run via Cowork's proxy skill, keep the final reply short: one paragraph with the outstanding-rows count, the ready/ambiguous/unavailable breakdown, any substitution candidates left for the user to action, and the path `data/shopping_list.json` for reference. Step 2.5 (scad edits) is always skipped in headless mode.

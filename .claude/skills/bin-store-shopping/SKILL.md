---
name: bin-store-shopping
description: Bin store procurement workflow. Trigger when the user asks "what do I need to buy", "refresh the shopping list", "find products for the bin store", "bin store shopping", or "check the bin store materials to order". Pulls the latest inventory from Grist, computes outstanding cuts (cut list minus inventory with greedy fit), searches B&Q for each outstanding section, writes product links into the local shopping_list snapshot, and pushes it to Grist. Designed for Cowork (uses Chrome browser automation) but also works in Claude Code CLI with WebFetch for single pages.
allowed-tools:
  [
    Bash(python3 scripts/sync_grist_tables.py*),
    Bash(python3 scripts/compute_shopping_list.py*),
    Read(data/cut_list.json),
    Read(data/inventory.json),
    Read(data/shopping_list.json),
    Edit,
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

Reads `data/cut_list.json` (incomplete rows only) and `data/inventory.json`, runs a greedy per-cut fit with 3 mm kerf and 150 mm minimum usable offcut, and writes `data/shopping_list.json`. Each row has a stable `shopping_id`, the dimensions needed, `qty_needed`, and empty `supplier`/`notes`/`status: "needs_product"`.

Read the file and report how many outstanding rows there are and the unique `section_key` values. If zero rows, stop — nothing to buy — and tell the user.

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

## Cowork notes

When run via Cowork's proxy skill, keep the final reply short: one paragraph with the outstanding-rows count, the ready/ambiguous/unavailable breakdown, and the path `data/shopping_list.json` for reference.

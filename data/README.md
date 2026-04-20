# Inventory Data Snapshots

This directory holds the repo-backed snapshots for the Grist inventory workflow.

## Source of truth

- `cut_list.json` is generated from the OpenSCAD/code layer. Do not edit it by hand.
- the `completed` field inside the Grist `cut_list` table is the one editable exception; it marks rows that have already been processed against inventory.
- `inventory.json` is the local snapshot of the Grist `inventory` table after pull/sync.
- `grist_schema.json` defines the intended Grist tables and columns for bootstrapping or validation.

The Grist `shopping_list` table is intentionally not managed by the scripts in this repo. A separate AI agent process is expected to use `cut_list` and `inventory` to determine what to buy and then populate shopping data.

The goal is to keep durable history in git while using Grist as the working UI.

## Typical flow

1. Update the OpenSCAD model.
2. Run `python3 scripts/extract_cut_list.py`.
3. Push `cut_list.json` to Grist.
4. Edit inventory in Grist.
5. Pull `inventory.json` back into the repo.

The generated `cut_list` table in Grist should be treated as read-only. Edit the OpenSCAD/code sources instead.

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from grist_inventory.common import (
    CUT_LIST_PATH,
    INVENTORY_PATH,
    SHOPPING_LIST_PATH,
    load_snapshot,
    write_snapshot,
)
from grist_inventory.requirements import build_shopping_rows, compute_shortfall


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compute outstanding cuts (cut_list minus inventory, greedy fit) and seed "
            "shopping_list.json with one row per outstanding cut. Fill in supplier/notes "
            "with product links, then push to Grist."
        )
    )
    parser.add_argument(
        "--cut-list",
        type=Path,
        default=CUT_LIST_PATH,
        help=f"Path to cut_list.json. Defaults to {CUT_LIST_PATH}.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=INVENTORY_PATH,
        help=f"Path to inventory.json. Defaults to {INVENTORY_PATH}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SHOPPING_LIST_PATH,
        help=f"Path to write shopping_list.json. Defaults to {SHOPPING_LIST_PATH}.",
    )
    args = parser.parse_args()

    cut_list_snapshot = load_snapshot(args.cut_list, "cut_list", "cut_id")
    inventory_snapshot = load_snapshot(args.inventory, "inventory", "inventory_id")

    shortfall = compute_shortfall(cut_list_snapshot["rows"], inventory_snapshot["rows"])
    rows = build_shopping_rows(shortfall)

    write_snapshot(args.output, "shopping_list", "shopping_id", rows)
    print(f"Wrote {len(rows)} outstanding shopping rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

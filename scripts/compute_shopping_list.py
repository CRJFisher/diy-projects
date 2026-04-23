#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from grist_inventory.common import (
    CUT_LIST_PATH,
    INVENTORY_PATH,
    SHOPPING_LIST_PATH,
    SUBSTITUTION_CANDIDATES_PATH,
    load_snapshot,
    write_json,
    write_snapshot,
)
from grist_inventory.requirements import (
    DEFAULT_SECTION_TOLERANCE_MM,
    build_shopping_rows,
    compute_shortfall,
    find_substitution_candidates,
)


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
    parser.add_argument(
        "--substitutions-output",
        type=Path,
        default=SUBSTITUTION_CANDIDATES_PATH,
        help=(
            "Path to write substitution_candidates.json. "
            f"Defaults to {SUBSTITUTION_CANDIDATES_PATH}."
        ),
    )
    parser.add_argument(
        "--tolerance-mm",
        type=float,
        default=DEFAULT_SECTION_TOLERANCE_MM,
        help=(
            "Per-dimension tolerance (mm) for substitution candidates. "
            f"Defaults to {DEFAULT_SECTION_TOLERANCE_MM}."
        ),
    )
    args = parser.parse_args()

    cut_list_snapshot = load_snapshot(args.cut_list, "cut_list", "cut_id")
    inventory_snapshot = load_snapshot(args.inventory, "inventory", "inventory_id")

    shortfall = compute_shortfall(cut_list_snapshot["rows"], inventory_snapshot["rows"])
    rows = build_shopping_rows(shortfall)

    write_snapshot(args.output, "shopping_list", "shopping_id", rows)
    print(f"Wrote {len(rows)} outstanding shopping rows to {args.output}")

    substitutions = find_substitution_candidates(
        shortfall, inventory_snapshot["rows"], tolerance_mm=args.tolerance_mm
    )
    write_json(
        args.substitutions_output,
        {"tolerance_mm": args.tolerance_mm, "substitutions": substitutions},
    )
    print(
        f"Wrote {len(substitutions)} substitution candidate(s) to "
        f"{args.substitutions_output} (tolerance ±{args.tolerance_mm:g} mm)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from grist.common import (
    INVENTORY_PATH,
    load_snapshot,
    read_json,
    write_json,
    write_snapshot,
)
from grist.project import load_project, other_projects
from grist.requirements import (
    DEFAULT_SECTION_TOLERANCE_MM,
    build_shopping_rows,
    compute_shortfall,
    find_substitution_candidates,
    reserve_inventory_for_other_projects,
)

HARDWARE_CATEGORY = "hardware"


def _load_existing_hardware_rows(path: Path) -> list[dict[str, Any]]:
    """Return any hand-authored hardware rows from an existing shopping_list snapshot.

    Hardware rows (category == "hardware") are not derived from the cut_list, so
    they must survive regeneration. Anything else is a computed row and is
    discarded on each run.
    """
    if not path.exists():
        return []
    doc = read_json(path, default={"rows": []})
    rows = doc.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if row.get("category") == HARDWARE_CATEGORY]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compute outstanding cuts for a project (cut_list minus shared inventory, "
            "after reserving stock for other projects' incomplete cuts) and seed "
            "shopping_list.json. Hand-authored hardware rows (category == 'hardware') "
            "are preserved across runs."
        )
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project slug under projects/ (e.g. bin-store).",
    )
    parser.add_argument(
        "--cut-list",
        type=Path,
        help="Override path to cut_list.json.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=INVENTORY_PATH,
        help=f"Path to shared inventory.json. Defaults to {INVENTORY_PATH}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Override path to write shopping_list.json.",
    )
    parser.add_argument(
        "--substitutions-output",
        type=Path,
        help="Override path to write substitution_candidates.json.",
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
    parser.add_argument(
        "--no-reserve",
        action="store_true",
        help="Skip reserving inventory for other projects' incomplete cuts.",
    )
    args = parser.parse_args()

    project = load_project(args.project)
    cut_list_path = args.cut_list or project.cut_list_path
    output_path = args.output or project.shopping_list_path
    substitutions_path = (
        args.substitutions_output or project.substitution_candidates_path
    )

    cut_list_snapshot = load_snapshot(cut_list_path, "cut_list", "cut_id")
    inventory_snapshot = load_snapshot(args.inventory, "inventory", "inventory_id")
    available_inventory = list(inventory_snapshot["rows"])

    if not args.no_reserve:
        other_cut_lists: list[list[dict[str, Any]]] = []
        for other in other_projects(project.slug):
            other_snapshot = load_snapshot(other.cut_list_path, "cut_list", "cut_id")
            other_cut_lists.append(other_snapshot["rows"])
        available_inventory = reserve_inventory_for_other_projects(
            available_inventory, other_cut_lists
        )

    shortfall = compute_shortfall(cut_list_snapshot["rows"], available_inventory)
    computed_rows = build_shopping_rows(shortfall)
    hardware_rows = _load_existing_hardware_rows(output_path)
    rows = computed_rows + hardware_rows

    write_snapshot(output_path, "shopping_list", "shopping_id", rows)
    print(
        f"Wrote {len(rows)} shopping rows to {output_path} "
        f"({len(computed_rows)} computed, {len(hardware_rows)} hardware)"
    )

    substitutions = find_substitution_candidates(
        shortfall, available_inventory, tolerance_mm=args.tolerance_mm
    )
    write_json(
        substitutions_path,
        {"tolerance_mm": args.tolerance_mm, "substitutions": substitutions},
    )
    print(
        f"Wrote {len(substitutions)} substitution candidate(s) to "
        f"{substitutions_path} (tolerance ±{args.tolerance_mm:g} mm)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

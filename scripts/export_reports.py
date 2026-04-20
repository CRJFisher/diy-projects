#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from grist_inventory.common import SNAPSHOT_PATHS, load_snapshot, number_text


def export_snapshot(snapshot_name: str, output_dir: Path) -> None:
    path = SNAPSHOT_PATHS[snapshot_name]
    primary_keys = {
        "cut_list": "cut_id",
        "inventory": "inventory_id",
        "material_rules": "rule_id",
    }
    snapshot = load_snapshot(path, snapshot_name, primary_keys[snapshot_name])
    rows = snapshot["rows"]
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{snapshot_name}.csv"
    md_path = output_dir / f"{snapshot_name}.md"

    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or ["empty"])
        writer.writeheader()
        if rows:
            for row in rows:
                writer.writerow(row)
        else:
            writer.writerow({"empty": ""})

    markdown_lines = [f"# {snapshot_name}", ""]
    if not rows:
        markdown_lines.append("_No rows._")
    else:
        markdown_lines.append("| " + " | ".join(fieldnames) + " |")
        markdown_lines.append("|" + "|".join(["---"] * len(fieldnames)) + "|")
        for row in rows:
            markdown_lines.append(
                "| "
                + " | ".join(number_text(row.get(field, "")) for field in fieldnames)
                + " |"
            )
    md_path.write_text("\n".join(markdown_lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export inventory workflow snapshots to CSV and Markdown."
    )
    parser.add_argument(
        "--snapshot",
        choices=sorted(SNAPSHOT_PATHS.keys()),
        help="Export a single snapshot. Defaults to exporting all workflow snapshots.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/exports",
        help="Directory for exported CSV and Markdown reports.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    snapshot_names = [args.snapshot] if args.snapshot else [
        "cut_list",
        "inventory",
    ]

    for snapshot_name in snapshot_names:
        export_snapshot(snapshot_name, output_dir)
        print(f"Exported {snapshot_name} to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

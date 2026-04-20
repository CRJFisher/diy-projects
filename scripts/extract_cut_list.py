#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from grist_inventory.common import (
    CUT_LIST_PATH,
    PARAMETERS_PATH,
    load_snapshot,
    preserve_fields_by_key,
    write_snapshot,
)
from grist_inventory.extraction import build_cut_list_rows, parse_parameters


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the OpenSCAD-derived cut_list snapshot."
    )
    parser.add_argument(
        "--output",
        default=str(CUT_LIST_PATH),
        help="Path to write the cut_list snapshot JSON.",
    )
    args = parser.parse_args()

    parameters = parse_parameters(PARAMETERS_PATH)
    rows = build_cut_list_rows(parameters)
    existing_snapshot = load_snapshot(
        path=Path(args.output),
        table_name="cut_list",
        primary_key="cut_id",
    )
    rows = preserve_fields_by_key(
        rows=rows,
        existing_rows=existing_snapshot["rows"],
        primary_key="cut_id",
        editable_fields=["completed"],
    )
    snapshot = write_snapshot(
        path=Path(args.output),
        table_name="cut_list",
        primary_key="cut_id",
        rows=rows,
    )

    print(
        f"Wrote {len(snapshot['rows'])} cut_list rows to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

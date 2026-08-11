#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType

from grist.common import load_snapshot, preserve_fields_by_key, write_snapshot
from grist.project import load_project


def _load_extraction_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        f"project_extraction_{path.parent.name}", path
    )
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load extraction module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the OpenSCAD-derived cut_list snapshot for a project."
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project slug under projects/ (e.g. bin-store).",
    )
    parser.add_argument(
        "--output",
        help="Optional override path for the cut_list snapshot JSON.",
    )
    args = parser.parse_args()

    project = load_project(args.project)
    output_path = Path(args.output) if args.output else project.cut_list_path
    extraction = _load_extraction_module(project.extraction_module)
    if not hasattr(extraction, "parse_parameters") or not hasattr(
        extraction, "build_cut_list_rows"
    ):
        raise SystemExit(
            f"{project.extraction_module} must define parse_parameters and build_cut_list_rows"
        )

    parameters = extraction.parse_parameters(project.parameters_path)
    rows = extraction.build_cut_list_rows(parameters)
    existing_snapshot = load_snapshot(
        path=output_path,
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
        path=output_path,
        table_name="cut_list",
        primary_key="cut_id",
        rows=rows,
    )

    print(f"Wrote {len(snapshot['rows'])} cut_list rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

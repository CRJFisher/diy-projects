from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
BIN_STORE_DIR = ROOT_DIR / "bin-store-model"
PARAMETERS_PATH = BIN_STORE_DIR / "parameters.scad"
SCHEMA_PATH = DATA_DIR / "grist_schema.json"
CUT_LIST_PATH = DATA_DIR / "cut_list.json"
INVENTORY_PATH = DATA_DIR / "inventory.json"
SHOPPING_LIST_PATH = DATA_DIR / "shopping_list.json"

SNAPSHOT_PATHS = {
    "cut_list": CUT_LIST_PATH,
    "inventory": INVENTORY_PATH,
    "shopping_list": SHOPPING_LIST_PATH,
}


def clean_number(value: Any) -> Any:
    if isinstance(value, float):
        rounded = round(value, 3)
        if rounded.is_integer():
            return int(rounded)
        return rounded
    return value


def number_text(value: Any) -> str:
    if value in (None, ""):
        return "-"
    cleaned = clean_number(value)
    if isinstance(cleaned, float):
        return f"{cleaned:.3f}".rstrip("0").rstrip(".")
    return str(cleaned)


def stable_json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json_dumps(data))


def sorted_rows(rows: list[dict[str, Any]], primary_key: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: str(row.get(primary_key, "")))


def load_snapshot(path: Path, table_name: str, primary_key: str) -> dict[str, Any]:
    snapshot = read_json(path, default=None)
    if snapshot is None:
        return {
            "table_name": table_name,
            "primary_key": primary_key,
            "rows": [],
        }
    return snapshot


def write_snapshot(
    path: Path,
    table_name: str,
    primary_key: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot = {
        "table_name": table_name,
        "primary_key": primary_key,
        "rows": sorted_rows(rows, primary_key),
    }
    write_json(path, snapshot)
    return snapshot


def row_dimensions(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (
        clean_number(row.get("length_mm")),
        clean_number(row.get("width_mm")),
        clean_number(row.get("thickness_mm")),
    )


def make_match_key(row: dict[str, Any]) -> str:
    length_mm, width_mm, thickness_mm = row_dimensions(row)
    return "|".join(
        [
            str(row.get("category", "")),
            str(row.get("material_type", "")),
            str(row.get("section_key", "")),
            number_text(length_mm),
            number_text(width_mm),
            number_text(thickness_mm),
            str(row.get("unit", "")),
        ]
    )


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    compacted: dict[str, Any] = {}
    for key, value in row.items():
        cleaned = clean_number(value)
        if cleaned in ("", None):
            continue
        compacted[key] = cleaned
    return compacted


def preserve_fields_by_key(
    rows: list[dict[str, Any]],
    existing_rows: list[dict[str, Any]],
    primary_key: str,
    editable_fields: list[str],
) -> list[dict[str, Any]]:
    existing_by_key = {
        row.get(primary_key): row
        for row in existing_rows
        if row.get(primary_key) not in (None, "")
    }
    merged_rows: list[dict[str, Any]] = []
    for row in rows:
        merged_row = dict(row)
        existing_row = existing_by_key.get(row.get(primary_key), {})
        for field in editable_fields:
            if field in existing_row:
                merged_row[field] = existing_row[field]
        merged_rows.append(merged_row)
    return merged_rows

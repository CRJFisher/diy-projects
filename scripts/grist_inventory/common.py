from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


_SECTION_AXB_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*$")


def canonical_section_key(section_key: Any) -> str:
    """Normalize ``AxB`` section keys so that ``50x22`` and ``22x50`` compare equal.

    Non-``AxB`` shapes (``18_sheet``, ``125w_15t``, empty) are returned stripped
    but otherwise unchanged so labelled suffixes retain their meaning.
    """
    if section_key in (None, ""):
        return ""
    text = str(section_key).strip()
    match = _SECTION_AXB_RE.match(text)
    if not match:
        return text
    a, b = float(match.group(1)), float(match.group(2))
    lo, hi = sorted([a, b])

    def _fmt(value: float) -> str:
        return str(int(value)) if value.is_integer() else str(value)

    return f"{_fmt(lo)}x{_fmt(hi)}"


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
BIN_STORE_DIR = ROOT_DIR / "bin-store-model"
PARAMETERS_PATH = BIN_STORE_DIR / "parameters.scad"
SCHEMA_PATH = DATA_DIR / "grist_schema.json"
CUT_LIST_PATH = DATA_DIR / "cut_list.json"
INVENTORY_PATH = DATA_DIR / "inventory.json"
SHOPPING_LIST_PATH = DATA_DIR / "shopping_list.json"
SUBSTITUTION_CANDIDATES_PATH = DATA_DIR / "substitution_candidates.json"

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
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(stable_json_dumps(data))
    os.replace(tmp_path, path)


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


def _values_differ(new_value: Any, existing_value: Any) -> bool:
    cleaned_new = clean_number(new_value)
    cleaned_existing = clean_number(existing_value)
    if isinstance(cleaned_new, float) and isinstance(cleaned_existing, float):
        return abs(cleaned_new - cleaned_existing) > 1e-6
    return cleaned_new != cleaned_existing


def preserve_fields_by_key(
    rows: list[dict[str, Any]],
    existing_rows: list[dict[str, Any]],
    primary_key: str,
    editable_fields: list[str],
    reset_on_change_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Carry ``editable_fields`` from ``existing_rows`` onto ``rows`` keyed by
    ``primary_key``. If ``reset_on_change_fields`` is provided, a differing value
    in any of those fields means the row has drifted since the user last edited
    it — the preservation is skipped so the editable fields revert to whatever
    the regenerated row specifies (e.g. ``completed: False``).
    """
    existing_by_key = {
        row.get(primary_key): row
        for row in existing_rows
        if row.get(primary_key) not in (None, "")
    }
    compare_fields = reset_on_change_fields or []
    merged_rows: list[dict[str, Any]] = []
    for row in rows:
        merged_row = dict(row)
        existing_row = existing_by_key.get(row.get(primary_key), {})
        row_drifted = any(
            _values_differ(merged_row.get(field), existing_row.get(field))
            for field in compare_fields
            if field in existing_row
        )
        if not row_drifted:
            for field in editable_fields:
                if field in existing_row:
                    merged_row[field] = existing_row[field]
        merged_rows.append(merged_row)
    return merged_rows

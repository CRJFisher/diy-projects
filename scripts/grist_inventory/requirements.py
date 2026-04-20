from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any


DEFAULT_KERF_MM = 3.0
DEFAULT_MIN_OFFCUT_MM = 150.0


@dataclass(frozen=True)
class SectionGroupKey:
    category: str
    material_type: str
    section_key: str


def _normalize_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_completed(row: dict[str, Any]) -> bool:
    value = row.get("completed")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _group_key(row: dict[str, Any]) -> SectionGroupKey:
    return SectionGroupKey(
        category=_normalize_string(row.get("category")),
        material_type=_normalize_string(row.get("material_type")),
        section_key=_normalize_string(row.get("section_key")),
    )


def _expand_rows(
    rows: list[dict[str, Any]], qty_field: str
) -> dict[SectionGroupKey, list[float]]:
    result: dict[SectionGroupKey, list[float]] = defaultdict(list)
    for row in rows:
        length_raw = row.get("length_mm")
        qty_raw = row.get(qty_field)
        if length_raw in (None, "") or qty_raw in (None, "", 0):
            continue
        try:
            length_f = float(length_raw)
            qty_i = int(qty_raw)
        except (TypeError, ValueError):
            continue
        if length_f <= 0 or qty_i <= 0:
            continue
        key = _group_key(row)
        for _ in range(qty_i):
            result[key].append(length_f)
    return result


def compute_shortfall(
    cut_list_rows: list[dict[str, Any]],
    inventory_rows: list[dict[str, Any]],
    kerf_mm: float = DEFAULT_KERF_MM,
    min_offcut_mm: float = DEFAULT_MIN_OFFCUT_MM,
) -> list[dict[str, Any]]:
    """Greedy per-cut fit: longest-first, best-fit into available sticks, reuse offcuts above min_offcut_mm.

    Returns a list of {category, material_type, section_key, length_mm, qty} rows
    describing cuts that could not be satisfied from inventory.
    """
    incomplete_cuts = [row for row in cut_list_rows if not _is_completed(row)]
    cuts_by_group = _expand_rows(incomplete_cuts, "qty_required")
    sticks_by_group = _expand_rows(inventory_rows, "qty_on_hand")

    shortfall_counts: dict[tuple[SectionGroupKey, float], int] = defaultdict(int)

    for group_key, cuts in cuts_by_group.items():
        sticks = sorted(sticks_by_group.get(group_key, []))
        cuts_sorted = sorted(cuts, reverse=True)
        for cut_length in cuts_sorted:
            needed = cut_length + kerf_mm
            chosen_index: int | None = None
            for index, stick_length in enumerate(sticks):
                if stick_length >= needed:
                    chosen_index = index
                    break
            if chosen_index is None:
                shortfall_counts[(group_key, cut_length)] += 1
                continue
            stick_length = sticks.pop(chosen_index)
            offcut = stick_length - cut_length - kerf_mm
            if offcut >= min_offcut_mm:
                sticks.append(offcut)
                sticks.sort()

    shortfall_rows: list[dict[str, Any]] = []
    for (group_key, length_mm), qty in shortfall_counts.items():
        shortfall_rows.append(
            {
                "category": group_key.category,
                "material_type": group_key.material_type,
                "section_key": group_key.section_key,
                "length_mm": length_mm,
                "qty": qty,
            }
        )
    shortfall_rows.sort(
        key=lambda row: (
            str(row["category"]),
            str(row["material_type"]),
            str(row["section_key"]),
            -float(row["length_mm"]),
        )
    )
    return shortfall_rows


def _make_shopping_id(section_key: str, length_mm: float, index: int) -> str:
    section = section_key.replace(" ", "_") or "unknown"
    length = int(round(length_mm))
    return f"{section}-{length}-{index:02d}"


def build_shopping_rows(shortfall: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a shortfall list into shopping_list table rows with stable shopping_ids.

    Leaves `supplier`, `status`, and `notes` as placeholders for the shopping agent
    to populate with the product link it finds on the supplier's site.
    """
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(shortfall):
        qty = int(item.get("qty") or 1)
        length_mm = float(item.get("length_mm") or 0)
        section_key = _normalize_string(item.get("section_key"))
        rows.append(
            {
                "shopping_id": _make_shopping_id(section_key, length_mm, index),
                "category": _normalize_string(item.get("category")),
                "material_type": _normalize_string(item.get("material_type")),
                "section_key": section_key,
                "length_mm": length_mm,
                "qty_required": qty,
                "qty_available": 0,
                "qty_needed": qty,
                "supplier": "",
                "status": "needs_product",
                "notes": "",
            }
        )
    return rows

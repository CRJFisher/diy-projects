from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from grist_inventory.common import canonical_section_key


DEFAULT_KERF_MM = 3.0
DEFAULT_MIN_OFFCUT_MM = 150.0
DEFAULT_SECTION_TOLERANCE_MM = 10.0

_SECTION_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


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
        section_key=canonical_section_key(row.get("section_key")),
    )


def _expand_rows(
    rows: list[dict[str, Any]],
    qty_field: str,
    display_keys: dict[SectionGroupKey, str] | None = None,
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
        if display_keys is not None:
            raw = _normalize_string(row.get("section_key"))
            if raw and key not in display_keys:
                display_keys[key] = raw
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
    describing cuts that could not be satisfied from inventory. Matching is done
    on canonicalised section keys (``50x22`` == ``22x50``) but the emitted
    ``section_key`` is preserved in the form the cut list used, so downstream
    display matches what the user sees in the cut-list table.
    """
    incomplete_cuts = [row for row in cut_list_rows if not _is_completed(row)]
    cut_display_keys: dict[SectionGroupKey, str] = {}
    cuts_by_group = _expand_rows(
        incomplete_cuts, "qty_required", display_keys=cut_display_keys
    )
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
                "section_key": cut_display_keys.get(group_key, group_key.section_key),
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


def _parse_section_dims(section_key: str) -> tuple[float, ...]:
    if not section_key:
        return ()
    numbers = _SECTION_NUMBER_RE.findall(section_key)
    return tuple(sorted(float(n) for n in numbers))


def _max_dim_delta(a: tuple[float, ...], b: tuple[float, ...]) -> float | None:
    if not a or not b or len(a) != len(b):
        return None
    return max(abs(x - y) for x, y in zip(a, b))


def find_substitution_candidates(
    shortfall: list[dict[str, Any]],
    inventory_rows: list[dict[str, Any]],
    tolerance_mm: float = DEFAULT_SECTION_TOLERANCE_MM,
) -> list[dict[str, Any]]:
    """For each unmet shortfall line, surface inventory rows with the same
    ``material_type`` whose section dimensions differ by at most
    ``tolerance_mm`` on every parsed dimension.

    Section keys are canonicalised (``50x22`` == ``22x50``) before comparison,
    so reversed keys do not masquerade as near-matches. Candidates whose parsed
    dimensions equal the design dims exactly are excluded — they should have
    been consumed by the exact-match pass in ``compute_shortfall``; if they
    still appear here it's a data/keying issue that the user should fix in
    Grist, not a substitution decision.

    Join key is ``material_type`` only; ``category`` is editorial and is taken
    from the shortfall row. Cross-category drift on the inventory side is
    surfaced rather than hidden.
    """
    needed_by_section: dict[tuple[str, str], dict[str, Any]] = {}
    for row in shortfall:
        material_type = _normalize_string(row.get("material_type"))
        display_key = _normalize_string(row.get("section_key"))
        canonical_key = canonical_section_key(display_key)
        length_mm = row.get("length_mm")
        qty = row.get("qty")
        if not material_type or not canonical_key:
            continue
        if length_mm in (None, "") or not qty:
            continue
        key = (material_type, canonical_key)
        entry = needed_by_section.setdefault(
            key,
            {
                "category": _normalize_string(row.get("category")),
                "display_section_key": display_key,
                "cuts": [],
            },
        )
        entry["cuts"].append({"length_mm": float(length_mm), "qty": int(qty)})

    inventory_by_material: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inventory_rows:
        qty_on_hand = row.get("qty_on_hand")
        if not qty_on_hand:
            continue
        try:
            qty_i = int(qty_on_hand)
        except (TypeError, ValueError):
            continue
        if qty_i <= 0:
            continue
        material_type = _normalize_string(row.get("material_type"))
        if not material_type:
            continue
        inventory_by_material[material_type].append(row)

    substitutions: list[dict[str, Any]] = []
    for (material_type, design_canonical), entry in needed_by_section.items():
        design_dims = _parse_section_dims(design_canonical)
        if not design_dims:
            continue
        by_inv_canonical: dict[str, dict[str, Any]] = {}
        for inv_row in inventory_by_material.get(material_type, []):
            inv_display_key = _normalize_string(inv_row.get("section_key"))
            inv_canonical = canonical_section_key(inv_display_key)
            if not inv_canonical or inv_canonical == design_canonical:
                continue
            inv_dims = _parse_section_dims(inv_canonical)
            if inv_dims == design_dims:
                # Same physical section, keyed differently in the raw data.
                # Fix the inventory row rather than proposing a scad edit.
                continue
            delta = _max_dim_delta(design_dims, inv_dims)
            if delta is None or delta > tolerance_mm or delta <= 0:
                continue
            bucket = by_inv_canonical.setdefault(
                inv_canonical,
                {"display_key": inv_display_key, "rows": []},
            )
            bucket["rows"].append(inv_row)

        for inv_canonical, bucket in by_inv_canonical.items():
            inv_dims = _parse_section_dims(inv_canonical)
            delta = _max_dim_delta(design_dims, inv_dims)
            inv_display_key = bucket["display_key"]
            substitutions.append(
                {
                    "substitution_id": (
                        f"{material_type}:{design_canonical}->{inv_canonical}"
                    ),
                    "category": entry["category"],
                    "material_type": material_type,
                    "design_section_key": entry["display_section_key"],
                    "inventory_section_key": inv_display_key,
                    "design_dims": list(design_dims),
                    "inventory_dims": list(inv_dims),
                    "max_dim_delta_mm": delta,
                    "needed_cuts": sorted(
                        entry["cuts"], key=lambda c: (-c["length_mm"], -c["qty"])
                    ),
                    "inventory_available": sorted(
                        [
                            {
                                "inventory_id": _normalize_string(r.get("inventory_id")),
                                "qty_on_hand": int(r.get("qty_on_hand") or 0),
                                "length_mm": float(r.get("length_mm") or 0),
                            }
                            for r in bucket["rows"]
                        ],
                        key=lambda r: (-r["length_mm"], r["inventory_id"]),
                    ),
                }
            )

    substitutions.sort(
        key=lambda s: (
            s["material_type"],
            s["design_section_key"],
            s["inventory_section_key"],
        )
    )
    return substitutions


def _make_shopping_id(material_type: str, canonical_key: str, length_mm: float) -> str:
    """Content-derived id built on the **canonical** section key so that
    reversing a key in the raw data (e.g. ``50x22`` vs ``22x50``) does not
    change the id. Positional index is deliberately omitted: adding or removing
    shortfall rows must not renumber every surviving row (which would
    invalidate product URLs already pushed to Grist).
    """
    material = material_type.replace(" ", "_") or "unknown_material"
    section = canonical_key.replace(" ", "_") or "unknown_section"
    length = int(round(length_mm))
    return f"{material}-{section}-{length}"


def build_shopping_rows(shortfall: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a shortfall list into shopping_list table rows with stable shopping_ids.

    The emitted ``section_key`` preserves the form used in the cut list (e.g.
    ``50x22``) so the Grist shopping table reads naturally; the ``shopping_id``
    is built from the canonical form so reversed keys don't split rows.

    Leaves ``supplier``, ``status``, and ``notes`` as placeholders for the
    shopping agent to populate with the product link it finds on the supplier's
    site.
    """
    rows: list[dict[str, Any]] = []
    for item in shortfall:
        qty = int(item.get("qty") or 1)
        length_mm = float(item.get("length_mm") or 0)
        material_type = _normalize_string(item.get("material_type"))
        display_section_key = _normalize_string(item.get("section_key"))
        canonical_key = canonical_section_key(display_section_key)
        rows.append(
            {
                "shopping_id": _make_shopping_id(material_type, canonical_key, length_mm),
                "category": _normalize_string(item.get("category")),
                "material_type": material_type,
                "section_key": display_section_key,
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

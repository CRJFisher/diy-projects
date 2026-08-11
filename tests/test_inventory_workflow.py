from __future__ import annotations

import unittest

from extraction import build_cut_list_rows, parse_parameters
from grist.common import preserve_fields_by_key
from grist.project import (
    denamespace_pk,
    list_project_slugs,
    load_project,
    namespace_pk,
    other_projects,
)
from grist.requirements import (
    compute_shortfall,
    remaining_inventory_after_cuts,
    reserve_inventory_for_other_projects,
)


class InventoryWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = load_project("bin-store")
        self.parameters = parse_parameters(self.project.parameters_path)

    def test_cut_list_contains_expected_core_rows(self) -> None:
        rows = build_cut_list_rows(self.parameters)
        cut_ids = {row["cut_id"] for row in rows}

        self.assertIn("frame_post_back", cut_ids)
        self.assertIn("roof_deck_panel", cut_ids)
        self.assertIn("shelf_batten", cut_ids)
        self.assertIn("door_featheredge", cut_ids)
        self.assertEqual(len(rows), 20)

    def test_cut_list_rows_keep_inventory_matching_fields(self) -> None:
        rows = build_cut_list_rows(self.parameters)
        frame_post_row = next(row for row in rows if row["cut_id"] == "frame_post_back")

        self.assertEqual(frame_post_row["category"], "timber")
        self.assertEqual(frame_post_row["material_type"], "softwood_pt")
        self.assertEqual(frame_post_row["section_key"], "47x50")
        self.assertEqual(frame_post_row["width_mm"], 47)
        self.assertEqual(frame_post_row["thickness_mm"], 50)
        self.assertFalse(frame_post_row["completed"])

    def test_completed_flag_is_preserved_from_existing_snapshot_rows(self) -> None:
        generated_rows = build_cut_list_rows(self.parameters)
        existing_rows = [
            {
                "cut_id": "frame_post_back",
                "completed": True,
            }
        ]

        merged_rows = preserve_fields_by_key(
            rows=generated_rows,
            existing_rows=existing_rows,
            primary_key="cut_id",
            editable_fields=["completed"],
        )
        frame_post_row = next(
            row for row in merged_rows if row["cut_id"] == "frame_post_back"
        )
        roof_row = next(row for row in merged_rows if row["cut_id"] == "roof_deck_panel")

        self.assertTrue(frame_post_row["completed"])
        self.assertFalse(roof_row["completed"])

    def test_project_loader_discovers_bin_store_and_courtyard(self) -> None:
        slugs = list_project_slugs()
        self.assertIn("bin-store", slugs)
        self.assertIn("courtyard-nook", slugs)
        others = {p.slug for p in other_projects("bin-store")}
        self.assertIn("courtyard-nook", others)

    def test_pk_namespacing(self) -> None:
        self.assertEqual(namespace_pk("bin-store", "frame_post_back"), "bin-store__frame_post_back")
        self.assertEqual(
            denamespace_pk("bin-store", "bin-store__frame_post_back"), "frame_post_back"
        )

    def test_other_project_cuts_reserve_inventory(self) -> None:
        inventory = [
            {
                "inventory_id": "stick-1",
                "category": "timber",
                "material_type": "softwood_pt",
                "section_key": "47x50",
                "length_mm": 2400,
                "qty_on_hand": 1,
                "unit": "each",
            }
        ]
        other_cuts = [
            {
                "cut_id": "other_post",
                "category": "timber",
                "material_type": "softwood_pt",
                "section_key": "47x50",
                "length_mm": 2300,
                "qty_required": 1,
                "completed": False,
            }
        ]
        active_cuts = [
            {
                "cut_id": "active_post",
                "category": "timber",
                "material_type": "softwood_pt",
                "section_key": "47x50",
                "length_mm": 1500,
                "qty_required": 1,
                "completed": False,
            }
        ]

        # Without reservation the stick covers the active cut.
        self.assertEqual(compute_shortfall(active_cuts, inventory), [])

        remaining = remaining_inventory_after_cuts(other_cuts, inventory)
        # 2400 - 2300 - 3 kerf = 97 < 150 min offcut → stick fully consumed.
        self.assertEqual(remaining, [])

        reserved = reserve_inventory_for_other_projects(inventory, [other_cuts])
        shortfall = compute_shortfall(active_cuts, reserved)
        self.assertEqual(len(shortfall), 1)
        self.assertEqual(shortfall[0]["length_mm"], 1500)
        self.assertEqual(shortfall[0]["qty"], 1)


if __name__ == "__main__":
    unittest.main()

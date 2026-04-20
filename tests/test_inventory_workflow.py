from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from grist_inventory.extraction import build_cut_list_rows, parse_parameters  # noqa: E402


class InventoryWorkflowTests(unittest.TestCase):
    def test_cut_list_contains_expected_core_rows(self) -> None:
        rows = build_cut_list_rows(parse_parameters())
        cut_ids = {row["cut_id"] for row in rows}

        self.assertIn("frame_post_back", cut_ids)
        self.assertIn("roof_deck_panel", cut_ids)
        self.assertIn("shelf_panel_inferred", cut_ids)
        self.assertIn("door_featheredge", cut_ids)
        self.assertEqual(len(rows), 20)

    def test_cut_list_rows_keep_inventory_matching_fields(self) -> None:
        rows = build_cut_list_rows(parse_parameters())
        frame_post_row = next(row for row in rows if row["cut_id"] == "frame_post_back")

        self.assertEqual(frame_post_row["category"], "timber")
        self.assertEqual(frame_post_row["material_type"], "softwood_pt")
        self.assertEqual(frame_post_row["section_key"], "47x50")
        self.assertEqual(frame_post_row["width_mm"], 47)
        self.assertEqual(frame_post_row["thickness_mm"], 50)
        self.assertFalse(frame_post_row["completed"])

    def test_completed_flag_is_preserved_from_existing_snapshot_rows(self) -> None:
        generated_rows = build_cut_list_rows(parse_parameters())
        existing_rows = [
            {
                "cut_id": "frame_post_back",
                "completed": True,
            }
        ]

        from grist_inventory.common import preserve_fields_by_key  # noqa: E402

        merged_rows = preserve_fields_by_key(
            rows=generated_rows,
            existing_rows=existing_rows,
            primary_key="cut_id",
            editable_fields=["completed"],
        )
        frame_post_row = next(row for row in merged_rows if row["cut_id"] == "frame_post_back")
        roof_row = next(row for row in merged_rows if row["cut_id"] == "roof_deck_panel")

        self.assertTrue(frame_post_row["completed"])
        self.assertFalse(roof_row["completed"])


if __name__ == "__main__":
    unittest.main()

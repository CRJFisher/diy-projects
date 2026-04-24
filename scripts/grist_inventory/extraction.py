from __future__ import annotations

import ast
import math
import re
from pathlib import Path
from typing import Any

from grist_inventory.common import PARAMETERS_PATH, compact_row


ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?);$")


def parse_parameters(path: Path = PARAMETERS_PATH) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue
        match = ASSIGNMENT_RE.match(line)
        if not match:
            continue
        name, expr = match.groups()
        try:
            values[name] = _eval_expression(expr.strip(), values)
        except Exception:
            continue
    return values


def _eval_expression(expr: str, values: dict[str, Any]) -> Any:
    expr = expr.replace("true", "True").replace("false", "False")
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body, values)


def _eval_node(node: ast.AST, values: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, values)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return operand
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, values)
        right = _eval_node(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left**right
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(element, values) for element in node.elts)
    if isinstance(node, ast.List):
        return [_eval_node(element, values) for element in node.elts]
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def build_cut_list_rows(parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    parameters = parameters or parse_parameters()
    rows: list[dict[str, Any]] = []

    def add_row(
        *,
        cut_id: str,
        category: str,
        material_type: str,
        section_key: str,
        qty_required: int,
        unit: str,
        source_kind: str,
        source_ref: str,
        phase: str,
        notes: str = "",
        completed: bool = False,
        length_mm: Any = None,
        width_mm: Any = None,
        thickness_mm: Any = None,
    ) -> None:
        rows.append(
            compact_row(
                {
                    "cut_id": cut_id,
                    "category": category,
                    "material_type": material_type,
                    "section_key": section_key,
                    "length_mm": length_mm,
                    "width_mm": width_mm,
                    "thickness_mm": thickness_mm,
                    "qty_required": qty_required,
                    "unit": unit,
                    "source_kind": source_kind,
                    "source_ref": source_ref,
                    "phase": phase,
                    "completed": completed,
                    "notes": notes,
                }
            )
        )

    post_section = f"{parameters['post_face']}x{parameters['post_side']}"
    brace_section = f"{parameters['brace_w']}x{parameters['brace_t']}"
    batten_section = f"{parameters['batten_w']}x{parameters['batten_h']}"
    door_section = f"{parameters['door_frame_w']}x{parameters['door_frame_t']}"
    post_width_mm = parameters["post_face"]
    post_thickness_mm = parameters["post_side"]
    brace_width_mm = parameters["brace_w"]
    brace_thickness_mm = parameters["brace_t"]
    batten_width_mm = parameters["batten_w"]
    batten_thickness_mm = parameters["batten_h"]
    door_width_mm = parameters["door_frame_w"]
    door_thickness_mm = parameters["door_frame_t"]

    add_row(
        cut_id="frame_post_back",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["back_height"],
        qty_required=3,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="frame.back_frame",
        phase="weekend_1",
        notes="Back left, back centre, and back right posts.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )
    add_row(
        cut_id="frame_post_front_corner",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["front_height"],
        qty_required=2,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="frame.front_frame",
        phase="weekend_1",
        notes="Front left and front right corner posts.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )
    add_row(
        cut_id="frame_post_front_centre",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["centre_post_height"],
        qty_required=1,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="frame.front_frame",
        phase="weekend_1",
        notes="Front centre post that stands on the right bottom rail.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )
    add_row(
        cut_id="frame_rail_full_width",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["full_rail_length"],
        qty_required=4,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="frame.back_frame,frame.front_frame",
        phase="weekend_1",
        notes="Back top, back bottom, back mid, and front top rails.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )
    add_row(
        cut_id="frame_rail_front_bottom_right",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["right_front_bot_rail"],
        qty_required=1,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="frame.front_frame",
        phase="weekend_1",
        notes="Right-side bottom rail at the front opening.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )

    sloped_depth_length = math.hypot(parameters["depth_rail_length"], parameters["roof_slope"])
    add_row(
        cut_id="frame_depth_rail_level",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=parameters["depth_rail_length"],
        qty_required=8,
        unit="piece",
        source_kind="module_derived",
        source_ref="frame.centre_divider,frame.side_rails",
        phase="weekend_1",
        notes="Level depth rails, including the left wall mid-rail and shelf support rails.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )
    add_row(
        cut_id="frame_depth_rail_sloped",
        category="timber",
        material_type="softwood_pt",
        section_key=post_section,
        length_mm=sloped_depth_length,
        qty_required=3,
        unit="piece",
        source_kind="module_derived",
        source_ref="frame.centre_divider,frame.side_rails",
        phase="weekend_1",
        notes="Top depth rails that follow the roof slope.",
        width_mm=post_width_mm,
        thickness_mm=post_thickness_mm,
    )

    back_brace_length = math.hypot(
        parameters["back_centre_post_x"] - parameters["post_face"],
        (parameters["back_height"] - parameters["rail_h"])
        - (parameters["mid_rail_height"] + parameters["rail_h"]),
    )
    left_brace_high_length = math.hypot(
        parameters["depth_rail_length"],
        (parameters["back_height"] - parameters["rail_h"])
        - (parameters["mid_rail_height"] + parameters["rail_h"]),
    )
    left_brace_low_length = math.hypot(
        parameters["depth_rail_length"],
        (parameters["front_height"] - parameters["rail_h"])
        - (parameters["mid_rail_height"] + parameters["rail_h"]),
    )
    add_row(
        cut_id="brace_back_panel",
        category="timber",
        material_type="brace_timber",
        section_key=brace_section,
        length_mm=back_brace_length,
        qty_required=2,
        unit="piece",
        source_kind="module_derived",
        source_ref="frame.back_panel_braces",
        phase="weekend_1",
        notes="Net brace length from the clipped back-panel brace geometry.",
        width_mm=brace_width_mm,
        thickness_mm=brace_thickness_mm,
    )
    add_row(
        cut_id="brace_left_panel_long",
        category="timber",
        material_type="brace_timber",
        section_key=brace_section,
        length_mm=left_brace_high_length,
        qty_required=1,
        unit="piece",
        source_kind="module_derived",
        source_ref="frame.side_panel_braces",
        phase="weekend_1",
        notes="Long left-side brace running from bottom-front to top-back.",
        width_mm=brace_width_mm,
        thickness_mm=brace_thickness_mm,
    )
    add_row(
        cut_id="brace_left_panel_short",
        category="timber",
        material_type="brace_timber",
        section_key=brace_section,
        length_mm=left_brace_low_length,
        qty_required=1,
        unit="piece",
        source_kind="module_derived",
        source_ref="frame.side_panel_braces",
        phase="weekend_1",
        notes="Short left-side brace running from top-front to bottom-back.",
        width_mm=brace_width_mm,
        thickness_mm=brace_thickness_mm,
    )

    add_row(
        cut_id="roof_batten",
        category="timber",
        material_type="batten_softwood",
        section_key=batten_section,
        length_mm=parameters["total_width"],
        qty_required=4,
        unit="piece",
        source_kind="module_derived",
        source_ref="roof.roof_battens",
        phase="weekend_2",
        notes="Roof battens spanning the full width.",
        width_mm=batten_width_mm,
        thickness_mm=batten_thickness_mm,
    )
    add_row(
        cut_id="roof_deck_panel",
        category="sheet_good",
        material_type="plywood_exterior",
        section_key=f"{parameters['ply_t']}_sheet",
        length_mm=parameters["total_width"] + 2 * parameters["roof_overhang"],
        width_mm=parameters["total_depth"] + 2 * parameters["roof_overhang"],
        thickness_mm=parameters["ply_t"],
        qty_required=1,
        unit="sheet",
        source_kind="module_derived",
        source_ref="roof.roof_deck_panel",
        phase="weekend_2",
        notes="Roof deck cut size with overhang on all sides.",
    )

    add_row(
        cut_id="shelf_batten",
        category="timber",
        material_type="batten_softwood",
        section_key=batten_section,
        length_mm=parameters["shelf_batten_length"],
        qty_required=parameters["num_shelf_battens"] * 3,
        unit="piece",
        source_kind="parameter_derived",
        source_ref="shelves.shelf",
        phase="weekend_4",
        notes="Five battens per shelf across three shelf levels.",
        width_mm=batten_width_mm,
        thickness_mm=batten_thickness_mm,
    )
    add_row(
        cut_id="shelf_panel_inferred",
        category="sheet_good",
        material_type="plywood_exterior",
        section_key=f"{parameters['ply_t']}_sheet",
        length_mm=parameters["shelf_batten_length"],
        width_mm=parameters["depth_rail_length"],
        thickness_mm=parameters["ply_t"],
        qty_required=3,
        unit="piece",
        source_kind="inferred_from_code",
        source_ref="shelves.shelves",
        phase="weekend_4",
        notes="Shelf panels are not modeled directly; this cut size is inferred from the batten span and depth-rail length.",
    )

    back_panel_piece_height = math.ceil(parameters["back_height"] / 2)
    add_row(
        cut_id="back_panel_plywood",
        category="sheet_good",
        material_type="plywood_exterior",
        section_key=f"{parameters['hardboard_t']}_sheet",
        length_mm=parameters["total_width"],
        width_mm=back_panel_piece_height,
        thickness_mm=parameters["hardboard_t"],
        qty_required=2,
        unit="piece",
        source_kind="module_derived",
        source_ref="cladding.back_wall_panel",
        phase="weekend_3",
        notes="Back wall panel split into two stacked pieces so a standard 2440x1220 plywood sheet can be used (a single 1647mm-tall piece would not fit).",
    )

    featheredge_cover = parameters["featheredge_cover"]
    left_wall_count = math.ceil(max(parameters["front_height"], parameters["back_height"]) / featheredge_cover) + 1
    right_panel_width = (
        parameters["total_width"]
        - parameters["post_face"]
        - parameters["front_centre_post_x"]
        + parameters["front_panel_post_overlap"]
    )
    right_panel_height = parameters["front_height"] - parameters["rail_h"]
    right_panel_count = math.ceil(right_panel_height / featheredge_cover) + 1
    door_width = parameters["front_centre_post_x"] - (
        parameters["post_face"] + parameters["door_gap"]
    )
    door_height = (
        parameters["front_height"]
        - parameters["rail_h"]
        - 2 * parameters["door_gap"]
    )
    door_panel_count = math.ceil(door_height / featheredge_cover) + 1

    add_row(
        cut_id="left_wall_featheredge",
        category="cladding",
        material_type="featheredge",
        section_key=f"{parameters['featheredge_w']}w_{parameters['featheredge_thick']}t",
        length_mm=parameters["total_depth"],
        thickness_mm=parameters["featheredge_thick"],
        qty_required=left_wall_count,
        unit="piece",
        source_kind="module_derived",
        source_ref="cladding.left_wall_cladding",
        phase="weekend_3",
        notes="Board count is derived from featheredge cover height across the sloped left wall.",
        width_mm=parameters["featheredge_w"],
    )
    add_row(
        cut_id="right_front_featheredge",
        category="cladding",
        material_type="featheredge",
        section_key=f"{parameters['featheredge_w']}w_{parameters['featheredge_thick']}t",
        length_mm=right_panel_width,
        thickness_mm=parameters["featheredge_thick"],
        qty_required=right_panel_count,
        unit="piece",
        source_kind="module_derived",
        source_ref="cladding.right_front_panel",
        phase="weekend_3",
        notes="Board count is based on the modeled right-front featheredge panel.",
        width_mm=parameters["featheredge_w"],
    )
    add_row(
        cut_id="door_stile",
        category="timber",
        material_type="softwood_door",
        section_key=door_section,
        length_mm=door_height,
        qty_required=2,
        unit="piece",
        source_kind="module_derived",
        source_ref="door.door_panel",
        phase="weekend_3",
        notes="Door frame stiles.",
        width_mm=door_width_mm,
        thickness_mm=door_thickness_mm,
    )
    add_row(
        cut_id="door_rail",
        category="timber",
        material_type="softwood_door",
        section_key=door_section,
        length_mm=max(0, door_width - 2 * parameters["door_frame_w"]),
        qty_required=2,
        unit="piece",
        source_kind="module_derived",
        source_ref="door.door_panel",
        phase="weekend_3",
        notes="Door frame rails between the two stiles.",
        width_mm=door_width_mm,
        thickness_mm=door_thickness_mm,
    )
    add_row(
        cut_id="door_featheredge",
        category="cladding",
        material_type="featheredge",
        section_key=f"{parameters['featheredge_w']}w_{parameters['featheredge_thick']}t",
        length_mm=door_width,
        thickness_mm=parameters["featheredge_thick"],
        qty_required=door_panel_count,
        unit="piece",
        source_kind="module_derived",
        source_ref="door.door_panel",
        phase="weekend_3",
        notes="Modeled from the full outer door panel dimensions.",
        width_mm=parameters["featheredge_w"],
    )

    return sorted(rows, key=lambda row: row["cut_id"])

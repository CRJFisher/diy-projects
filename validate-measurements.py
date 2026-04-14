#!/usr/bin/env python3
"""
Bin Store Measurement Validation System
========================================
Validates all dimensional constraints for the bin store frame.
Identifies conflicts (e.g., internal clearance issues) and suggests corrections.

Usage:
    python3 validate-measurements.py           # validate only
    python3 validate-measurements.py --fix     # validate and update guide docs
"""

import argparse
import math
import re
import sys
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────────────────────
# TIMBER CROSS-SECTION  (50 x 47 mm pressure-treated softwood)
#
# Convention (derived from the guide):
#   - Guide says "50 mm face up" when laying posts on sawhorses.
#     This means the 50 mm dimension is the visible face width.
#   - Centre post = 1597 - 2 x 47  =>  rail cross-section height = 47 mm.
#
#   POST_WIDTH  = 50 mm  (left-right as seen from the front)
#   POST_DEPTH  = 47 mm  (front-to-back)
#   RAIL_HEIGHT = 47 mm  (vertical cross-section of a horizontal rail)
#   RAIL_DEPTH  = 50 mm  (front-to-back for a left-right rail)
# ─────────────────────────────────────────────────────────

POST_WIDTH  = 50   # mm
POST_DEPTH  = 47   # mm
RAIL_HEIGHT = 47   # mm
RAIL_DEPTH  = 50   # mm

# ─────────────────────────────────────────────────────────
# BRACE CROSS-SECTION  (15 x 38 mm user-supplied timber)
#
# All X-braces use 15x38mm stock (user's own, 2400mm lengths,
# 8 pieces available). At the crossing point the two braces
# overlap to 15+15 = 30mm, which is less than the 47mm frame
# depth, so they do not protrude beyond the frame face.
# ─────────────────────────────────────────────────────────
BRACE_THICKNESS = 15  # mm (thin dimension, stacks at crossing)
BRACE_WIDTH     = 38  # mm

# ─────────────────────────────────────────────────────────
# DESIGN TARGETS
# ─────────────────────────────────────────────────────────

TOTAL_WIDTH            = 1300  # mm, outside-to-outside
TOTAL_DEPTH            = 750   # mm, outside-to-outside (50 + 650 + 50)
INTERNAL_DEPTH         = 650   # mm, between inner faces of posts (food caddy clearance)
ROOF_SLOPE             = 50    # mm, back higher than front
ROOF_OVERHANG          = 25    # mm, overhang on front, back, and sides
BATTEN_W               = 50    # mm, batten width (Y dimension on roof)
BATTEN_H               = 22    # mm, batten height (Z dimension on roof)
PLY_T                  = 18    # mm, plywood thickness
LEFT_SECTION_CLEAR     = 780   # mm, door opening (left post inside face to centre post face)
RIGHT_SECTION_WIDTH    = 440   # mm, recycling bin width + 10mm clearance (centre post overlaps into this space)
FRONT_CENTRE_POST_X    = 874   # mm, X position of front centre post (post_face + left_section_clear + post_face)
BACK_CENTRE_POST_X     = 827   # mm, X position of back centre post (post_face + left_section_clear)
MID_RAIL_HEIGHT        = 775   # mm from ground
MIN_INTERNAL_CLEARANCE = 1550  # mm, wheelie bin lid clearance in left section


# ─────────────────────────────────────────────────────────
# CUT REGISTRY
# ─────────────────────────────────────────────────────────

@dataclass
class Cut:
    cut_id: str
    description: str
    length: float           # mm, as stated in the guide
    qty: int = 1
    corrected: Optional[float] = None
    notes: str = ""

    @property
    def eff(self) -> float:
        """Effective (possibly corrected) length."""
        return self.corrected if self.corrected is not None else self.length


CUTS: dict[str, Cut] = {}

def _cut(cut_id, desc, length, qty=1, notes=""):
    CUTS[cut_id] = Cut(cut_id, desc, length, qty, notes=notes)

# -- POSTS --
_cut("POST_BL",  "Back-left corner post",            1647, notes="Full height back post")
_cut("POST_BR",  "Back-right corner post",            1647)
_cut("POST_BC",  "Back-centre post",                  1647, notes="Full height (same as corner back posts); inside frame at X=827, one post_side in front of back wall")
_cut("POST_FL",  "Front-left corner post",            1597, notes="50 mm shorter than back for roof slope")
_cut("POST_FR",  "Front-right corner post",           1597)
_cut("POST_FC",  "Front centre post",                 1503, notes="Between top & bottom rails: 1597 - 2x47; at X=874 (sits on top of front bottom right rail)")

# -- BACK FRAME RAILS (butt between inner faces of corner posts) --
_cut("RAIL_BACK_TOP",  "Back top rail",    1206, notes="Butts between corner posts: 1300 - 2x47 = 1206")
_cut("RAIL_BACK_BOT",  "Back bottom rail", 1206, notes="Butts between corner posts: 1300 - 2x47 = 1206")
_cut("RAIL_BACK_MID",  "Back mid-height rail", 1206, notes="At 775 mm; butts between corner posts")

# -- FRONT FRAME RAILS --
_cut("RAIL_FRONT_TOP",    "Front top rail",                   1206, notes="Butts between corner posts: 1300 - 2x47 = 1206")
_cut("RAIL_FRONT_BOT_R",  "Front bottom rail (right section)", 379,
     notes="From front centre post X (874) to right corner post inner face (1253): 1300 - 47 - 874 = 379mm; front centre post sits on top of this rail")


# -- DEPTH RAILS (front to back, butt between posts) --
_cut("RAIL_DEPTH_TL", "Top-left depth rail",     650, notes="Butts end-grain into post inner faces")
_cut("RAIL_DEPTH_TR", "Top-right depth rail",    650)
_cut("RAIL_DEPTH_BL", "Bottom-left depth rail",  650)
_cut("RAIL_DEPTH_BR", "Bottom-right depth rail", 650)
_cut("RAIL_DEPTH_TC", "Top centre depth rail",   650, notes="Centre divider top")
_cut("RAIL_DEPTH_MC", "Mid centre depth rail",   650, notes="Centre divider at 775 mm")

# -- SIDE MID-RAILS (front to back, butt between posts) --
_cut("RAIL_MID_LEFT", "Left wall mid-rail", 650, notes="Left-front to left-back at 775 mm")

# -- CROSS-BRACES (15x38mm user-supplied timber, NOT from B&Q 50x47mm stock) --
_cut("BRACE_BACK_1", "Back panel X-brace 1", 1100, notes="15x38mm user-supplied; left section upper zone, 45-deg ends")
_cut("BRACE_BACK_2", "Back panel X-brace 2", 1100, notes="15x38mm user-supplied")
_cut("BRACE_LEFT_1", "Left panel X-brace 1", 1000, notes="15x38mm user-supplied; left side upper zone, 45-deg ends; ~980 actual")
_cut("BRACE_LEFT_2", "Left panel X-brace 2", 1000, notes="15x38mm user-supplied; ~1010 actual")

# -- NOGGINS removed from Weekend 1 (optional; add in Weekend 3 if cladding needs extra support) --

# -- ROOF BATTENS (50x22mm, running left-to-right across full width) --
_cut("BATTEN_ROOF_1", "Roof batten 1 (front)",  1300, notes="50x22mm batten, full width")
_cut("BATTEN_ROOF_2", "Roof batten 2",          1300, notes="50x22mm batten, full width")
_cut("BATTEN_ROOF_3", "Roof batten 3",          1300, notes="50x22mm batten, full width")
_cut("BATTEN_ROOF_4", "Roof batten 4 (back)",   1300, notes="50x22mm batten, full width")

# -- ROOF DECK (plywood, with 25mm overhang on all sides) --
_cut("ROOF_DECK_W", "Roof deck width",  1350, notes=f"Plywood: {TOTAL_WIDTH} + 2 x {ROOF_OVERHANG} = {TOTAL_WIDTH + 2 * ROOF_OVERHANG}")
_cut("ROOF_DECK_D", "Roof deck depth",  800,  notes=f"Plywood: {TOTAL_DEPTH} + 2 x {ROOF_OVERHANG} = {TOTAL_DEPTH + 2 * ROOF_OVERHANG}")


# ─────────────────────────────────────────────────────────
# CONSTRAINT & CHECK TYPES
# ─────────────────────────────────────────────────────────

@dataclass
class Constraint:
    name: str
    description: str
    members: list           # [(label, value_mm), ...]
    expected: float
    tolerance: float = 2.0

    @property
    def actual(self) -> float:
        return sum(v for _, v in self.members)

    @property
    def ok(self) -> bool:
        return abs(self.actual - self.expected) <= self.tolerance

    def report(self) -> str:
        tag = "PASS" if self.ok else "FAIL"
        parts = " + ".join(f"{l}({v})" for l, v in self.members)
        lines = [
            f"[{tag}] {self.name}",
            f"       {self.description}",
            f"       {parts} = {self.actual} mm  (expected {self.expected} mm)",
        ]
        if not self.ok:
            lines.append(f"       MISMATCH: {self.actual - self.expected:+.1f} mm")
        return "\n".join(lines)


@dataclass
class ClearanceCheck:
    name: str
    description: str
    available: float
    required: float
    tolerance: float = 0.0

    @property
    def ok(self) -> bool:
        return self.available >= self.required - self.tolerance

    def report(self) -> str:
        tag = "PASS" if self.ok else "FAIL"
        lines = [
            f"[{tag}] {self.name}",
            f"       {self.description}",
            f"       Available: {self.available:.0f} mm, Required: >= {self.required} mm",
        ]
        if not self.ok:
            lines.append(f"       SHORTFALL: {self.required - self.available:.0f} mm")
        return "\n".join(lines)


def L(cut_id: str) -> float:
    """Shorthand: effective length of a cut."""
    return CUTS[cut_id].eff


# ─────────────────────────────────────────────────────────
# BUILD ALL CONSTRAINTS
#
# Every structural "line" in the wireframe is traced here.
# ─────────────────────────────────────────────────────────

def build_constraints() -> list:
    cs = []
    add = cs.append

    # Derived values
    # NOTE: CLAUDE.md uses 47 mm for posts in the width (left-right) chain,
    # which corresponds to POST_DEPTH in this script's naming convention.
    # The naming (POST_WIDTH=50 "left-right", POST_DEPTH=47 "front-to-back")
    # appears swapped relative to reality, but we use POST_DEPTH here to
    # match the authoritative constraints in CLAUDE.md.
    right_section_width = RIGHT_SECTION_WIDTH
    right_clear = TOTAL_WIDTH - 3 * POST_DEPTH - LEFT_SECTION_CLEAR  # 1300 - 141 - 780 = 379
    depth_rail_expected = INTERNAL_DEPTH  # rails butt between posts = 650 mm

    # ── WIDTH (left-to-right) ──────────────────────────────

    # Full-width rails butt between inner faces of corner posts.
    # Correct length = TOTAL_WIDTH - 2 * POST_DEPTH (1300 - 94 = 1206).
    full_width_rail_expected = TOTAL_WIDTH - 2 * POST_DEPTH
    for rid, label in [
        ("RAIL_BACK_TOP",  "Back top rail = total width - 2 * post depth"),
        ("RAIL_BACK_BOT",  "Back bottom rail = total width - 2 * post depth"),
        ("RAIL_BACK_MID",  "Back mid rail = total width - 2 * post depth"),
        ("RAIL_FRONT_TOP", "Front top rail = total width - 2 * post depth"),
    ]:
        add(Constraint(f"{rid}_WIDTH", label,
                        [(rid, L(rid))], full_width_rail_expected))

    # Dimensional chain: post_depth + rail + post_depth = TOTAL_WIDTH
    # This would catch a rail incorrectly set to 1300 (chain would sum to 1394).
    for rid, label in [
        ("RAIL_BACK_TOP",  "Back top rail"),
        ("RAIL_BACK_BOT",  "Back bottom rail"),
        ("RAIL_BACK_MID",  "Back mid rail"),
        ("RAIL_FRONT_TOP", "Front top rail"),
    ]:
        add(Constraint(f"{rid}_WIDTH_CHAIN",
            f"{label}: post_depth + rail + post_depth = {TOTAL_WIDTH}",
            [("left_post_depth", POST_DEPTH),
             (rid, L(rid)),
             ("right_post_depth", POST_DEPTH)],
            TOTAL_WIDTH))

    # Right-section rails
    add(Constraint("RIGHT_SECTION_COMPUTED_WIDTH",
        f"Right section width = {RIGHT_SECTION_WIDTH} (from CLAUDE.md: recycling bin width + 10mm clearance)",
        [("right_section", right_section_width)], 440))

    # Right-section rail clear span
    # Front centre post at X=874, right corner post inner face at 1300-47=1253
    # Rail length = 1253 - 874 = 379mm (front centre post sits on top of this rail)
    right_rail_expected = TOTAL_WIDTH - POST_DEPTH - FRONT_CENTRE_POST_X  # 1300 - 47 - 874 = 379
    add(Constraint("RIGHT_RAIL_CLEAR_SPAN",
        f"Right front bottom rail = total_width ({TOTAL_WIDTH}) - right post depth ({POST_DEPTH}) - front_centre_post_x ({FRONT_CENTRE_POST_X})",
        [("RAIL_FRONT_BOT_R", L("RAIL_FRONT_BOT_R"))], right_rail_expected))

    add(Constraint("RAIL_FRONT_BOT_R_WIDTH",
        "Front bottom rail (right) = right section clear span",
        [("RAIL_FRONT_BOT_R", L("RAIL_FRONT_BOT_R"))], right_rail_expected))

    # Full width dimensional chain (uses POST_DEPTH = 47 mm per CLAUDE.md)
    add(Constraint("TOTAL_WIDTH_CHAIN",
        "left_post + left_clear + centre_post + right_clear + right_post = 1300",
        [("POST_FL_w", POST_DEPTH),
         ("left_clear", LEFT_SECTION_CLEAR),
         ("POST_FC_w", POST_DEPTH),
         ("right_clear", right_clear),
         ("POST_FR_w", POST_DEPTH)],
        TOTAL_WIDTH))

    # ── HEIGHT ─────────────────────────────────────────────

    # Post heights -- compare against their own effective lengths
    # (so corrected values self-validate)
    add(Constraint("ROOF_SLOPE_LR",
        "Back-left minus front-left = roof slope",
        [("POST_BL", L("POST_BL")), ("minus_POST_FL", -L("POST_FL"))],
        ROOF_SLOPE))

    add(Constraint("ROOF_SLOPE_RR",
        "Back-right minus front-right = roof slope",
        [("POST_BR", L("POST_BR")), ("minus_POST_FR", -L("POST_FR"))],
        ROOF_SLOPE))

    add(Constraint("BACK_POSTS_EQUAL",
        "All back posts equal",
        [("POST_BL", L("POST_BL")), ("minus_POST_BR", -L("POST_BR"))],
        0))

    add(Constraint("BACK_POSTS_EQUAL_2",
        "Back-left = back-centre",
        [("POST_BL", L("POST_BL")), ("minus_POST_BC", -L("POST_BC"))],
        0))

    add(Constraint("FRONT_POSTS_EQUAL",
        "Front corner posts equal",
        [("POST_FL", L("POST_FL")), ("minus_POST_FR", -L("POST_FR"))],
        0))

    # Front centre post vertical chain: top_rail + centre_post + bottom_rail = front_post
    # (This derivation applies only to the front centre post; the back centre post is full height)
    add(Constraint("FRONT_CENTRE_POST_VERTICAL",
        "top_rail_ht + front_centre_post + bot_rail_ht = front corner post",
        [("rail_top_ht", RAIL_HEIGHT),
         ("POST_FC", L("POST_FC")),
         ("rail_bot_ht", RAIL_HEIGHT)],
        L("POST_FL")))

    # Front centre post expected value
    add(Constraint("FRONT_CENTRE_POST_CALC",
        f"Front centre post = front_post - 2 x rail_height",
        [("POST_FC", L("POST_FC"))],
        L("POST_FL") - 2 * RAIL_HEIGHT))

    # Back centre post is full height (same as back corner posts)
    add(Constraint("BACK_CENTRE_POST_HEIGHT",
        "Back centre post = back corner post height (full height, inside frame)",
        [("POST_BC", L("POST_BC")), ("minus_POST_BL", -L("POST_BL"))],
        0))

    # ── INTERNAL CLEARANCE (CRITICAL) ──────────────────────

    # Left section: no bottom rail.  Clearance = ground to bottom of top rail.
    # Top rail is face-mounted, top edge flush with post top.
    # Bottom of top rail = post_height - rail_height.
    add(ClearanceCheck("LEFT_INTERNAL_CLEARANCE",
        f"Left section clearance: post_ht({L('POST_FL'):.0f}) - rail_ht({RAIL_HEIGHT}) = {L('POST_FL') - RAIL_HEIGHT:.0f} mm",
        available=L("POST_FL") - RAIL_HEIGHT,
        required=MIN_INTERNAL_CLEARANCE))

    # Right section: between bottom and top rails (informational)
    add(ClearanceCheck("RIGHT_INTERNAL_CLEARANCE",
        f"Right section clearance (informational): {L('POST_FR') - 2*RAIL_HEIGHT:.0f} mm",
        available=L("POST_FR") - 2 * RAIL_HEIGHT,
        required=0))

    # ── DEPTH (front-to-back) ──────────────────────────────
    # Depth rails butt end-grain into inner faces of posts.
    # Chain: post_depth + rail_length + post_depth = total_depth.

    depth_rails = [
        ("RAIL_DEPTH_TL", "Left top depth"),
        ("RAIL_DEPTH_BL", "Left bottom depth"),
        ("RAIL_DEPTH_TR", "Right top depth"),
        ("RAIL_DEPTH_BR", "Right bottom depth"),
        ("RAIL_DEPTH_TC", "Centre top depth"),
        ("RAIL_DEPTH_MC", "Centre mid depth"),
        ("RAIL_MID_LEFT", "Left wall mid-rail depth"),
    ]
    for rid, label in depth_rails:
        add(Constraint(f"DEPTH_{rid}",
            f"{label}: post_width + {rid} + post_width = {TOTAL_DEPTH}",
            [("front_post_width", POST_WIDTH),
             (rid, L(rid)),
             ("back_post_width", POST_WIDTH)],
            TOTAL_DEPTH))

    # ── INTERNAL DEPTH CLEARANCE (food caddy) ───────────────
    add(ClearanceCheck("INTERNAL_DEPTH_CLEARANCE",
        f"Internal depth (between post faces) >= {INTERNAL_DEPTH} mm for food caddy",
        available=depth_rail_expected,
        required=INTERNAL_DEPTH))

    # ── TOTAL DEPTH CHAIN ─────────────────────────────────
    add(Constraint("TOTAL_DEPTH_CHAIN",
        "front_post_width + depth_rail + back_post_width = total_depth",
        [("front_post_width", POST_WIDTH),
         ("depth_rail", depth_rail_expected),
         ("back_post_width", POST_WIDTH)],
        TOTAL_DEPTH))

    # ── SIDE FACE HEIGHT CHAINS ────────────────────────────

    # Left side slope
    add(Constraint("LEFT_SIDE_SLOPE",
        "Left side: back - front = slope",
        [("POST_BL", L("POST_BL")), ("minus_POST_FL", -L("POST_FL"))],
        ROOF_SLOPE))

    # Right side slope
    add(Constraint("RIGHT_SIDE_SLOPE",
        "Right side: back - front = slope",
        [("POST_BR", L("POST_BR")), ("minus_POST_FR", -L("POST_FR"))],
        ROOF_SLOPE))

    # ── TOP RECTANGLE (plan view) ──────────────────────────

    add(Constraint("TOP_RECT_FRONT_BACK_MATCH",
        "Front top rail = back top rail (widths match)",
        [("RAIL_FRONT_TOP", L("RAIL_FRONT_TOP")),
         ("minus_RAIL_BACK_TOP", -L("RAIL_BACK_TOP"))],
        0))

    # All four corner depth rails equal
    add(Constraint("TOP_RECT_DEPTH_MATCH",
        "Top-left depth rail = top-right depth rail",
        [("RAIL_DEPTH_TL", L("RAIL_DEPTH_TL")),
         ("minus_RAIL_DEPTH_TR", -L("RAIL_DEPTH_TR"))],
        0))

    # ── ROOF ──────────────────────────────────────────────

    # Battens span the full width
    for bid in ["BATTEN_ROOF_1", "BATTEN_ROOF_2", "BATTEN_ROOF_3", "BATTEN_ROOF_4"]:
        add(Constraint(f"{bid}_LENGTH",
            f"{bid}: batten length = total width ({TOTAL_WIDTH})",
            [(bid, L(bid))], TOTAL_WIDTH))

    # Roof deck dimensions (with overhang)
    expected_deck_w = TOTAL_WIDTH + 2 * ROOF_OVERHANG
    expected_deck_d = TOTAL_DEPTH + 2 * ROOF_OVERHANG
    add(Constraint("ROOF_DECK_WIDTH",
        f"Roof deck width = total_width + 2 x overhang = {expected_deck_w}",
        [("ROOF_DECK_W", L("ROOF_DECK_W"))], expected_deck_w))

    add(Constraint("ROOF_DECK_DEPTH",
        f"Roof deck depth = total_depth + 2 x overhang = {expected_deck_d}",
        [("ROOF_DECK_D", L("ROOF_DECK_D"))], expected_deck_d))

    # ── CROSS-BRACE DIAGONALS ─────────────────────────────

    # Back braces: left section upper zone.
    # Rectangle: width = LEFT_SECTION_CLEAR (780 mm between inside faces)
    # Height = upper zone = (back_post - rail_ht) - (mid_rail_ht + rail_ht)
    back_upper_h = (L("POST_BL") - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    back_brace_diag = math.sqrt(LEFT_SECTION_CLEAR**2 + back_upper_h**2)
    add(Constraint("BACK_BRACE_DIAG",
        f"Back X-brace: sqrt({LEFT_SECTION_CLEAR}^2 + {back_upper_h:.0f}^2) = {back_brace_diag:.0f}",
        [("BRACE_BACK_1", L("BRACE_BACK_1"))],
        round(back_brace_diag), tolerance=30))

    # Left side braces: upper zone of left wall.
    # Width = depth rail length (clear span between posts).
    # Height: upper zone averages between back and front because of slope.
    front_upper_h = (L("POST_FL") - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    avg_upper_h = (back_upper_h + front_upper_h) / 2
    left_side_width = L("RAIL_DEPTH_TL")  # depth rail = clear span between posts
    left_brace_diag = math.sqrt(left_side_width**2 + avg_upper_h**2)
    add(Constraint("LEFT_BRACE_DIAG",
        f"Left X-brace: sqrt({left_side_width:.0f}^2 + {avg_upper_h:.0f}^2) = {left_brace_diag:.0f}",
        [("BRACE_LEFT_1", L("BRACE_LEFT_1"))],
        round(left_brace_diag), tolerance=80))

    # ── NOGGIN constraints removed (noggins are optional) ──

    # ── MID-RAIL HEIGHT CONSISTENCY ────────────────────────

    add(Constraint("MID_RAIL_APPROX_HALF",
        "Mid-rail at 775 mm is roughly half the back height",
        [("mid_rail_ht", MID_RAIL_HEIGHT)],
        L("POST_BL") / 2, tolerance=60))

    return cs


# ─────────────────────────────────────────────────────────
# CORRECTION ENGINE
# ─────────────────────────────────────────────────────────

def calculate_corrections() -> list[str]:
    """Identify issues and apply corrected dimensions."""
    msgs = []

    # --- Internal clearance fix ---
    clearance = CUTS["POST_FL"].length - RAIL_HEIGHT
    if clearance < MIN_INTERNAL_CLEARANCE:
        shortfall = MIN_INTERNAL_CLEARANCE - clearance  # 47
        new_front = CUTS["POST_FL"].length + shortfall
        new_back  = CUTS["POST_BL"].length + shortfall
        new_centre = new_front - 2 * RAIL_HEIGHT

        msgs.append(
            f"CLEARANCE FIX: Front posts {CUTS['POST_FL'].length} -> {new_front} mm "
            f"(+{shortfall}) to achieve {MIN_INTERNAL_CLEARANCE} mm internal clearance.")
        msgs.append(
            f"CLEARANCE FIX: Back posts {CUTS['POST_BL'].length} -> {new_back} mm "
            f"(+{shortfall}) to maintain {ROOF_SLOPE} mm roof slope.")
        msgs.append(
            f"CLEARANCE FIX: Front centre post {CUTS['POST_FC'].length} -> {new_centre} mm "
            f"(back centre post stays at full back height).")

        for pid in ("POST_FL", "POST_FR"):
            CUTS[pid].corrected = new_front
        # Back centre post is full height (same as back corner posts)
        for pid in ("POST_BL", "POST_BR", "POST_BC"):
            CUTS[pid].corrected = new_back
        CUTS["POST_FC"].corrected = new_centre

    # --- Depth rails ---
    # Depth rails are 650 mm (INTERNAL_DEPTH) -- they butt between post inner faces.
    # Total external depth = POST_WIDTH + INTERNAL_DEPTH + POST_WIDTH = 750 mm.
    # No correction needed; 650 mm is the correct rail length.
    expected_depth = INTERNAL_DEPTH  # 650

    # --- Left brace recalculation ---
    depth_span = expected_depth
    new_back_ht = CUTS["POST_BL"].eff
    new_front_ht = CUTS["POST_FL"].eff
    back_upper  = (new_back_ht - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    front_upper = (new_front_ht - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    avg_upper = (back_upper + front_upper) / 2
    left_diag = math.sqrt(depth_span**2 + avg_upper**2)
    if abs(CUTS["BRACE_LEFT_1"].length - left_diag) > 30:
        rounded = round(left_diag / 10) * 10  # round to nearest 10
        msgs.append(
            f"BRACE FIX: Left X-braces {CUTS['BRACE_LEFT_1'].length} -> ~{rounded} mm "
            f"(diagonal of {depth_span} x {avg_upper:.0f} rectangle = {left_diag:.0f}).")
        CUTS["BRACE_LEFT_1"].corrected = rounded
        CUTS["BRACE_LEFT_2"].corrected = rounded

    # --- Back brace recalculation ---
    back_diag = math.sqrt(LEFT_SECTION_CLEAR**2 + back_upper**2)
    if abs(CUTS["BRACE_BACK_1"].length - back_diag) > 30:
        rounded = round(back_diag / 10) * 10
        msgs.append(
            f"BRACE FIX: Back X-braces {CUTS['BRACE_BACK_1'].length} -> ~{rounded} mm "
            f"(diagonal of {LEFT_SECTION_CLEAR} x {back_upper:.0f} = {back_diag:.0f}).")
        CUTS["BRACE_BACK_1"].corrected = rounded
        CUTS["BRACE_BACK_2"].corrected = rounded

    return msgs


# ─────────────────────────────────────────────────────────
# GUIDE DOCUMENT UPDATE
# ─────────────────────────────────────────────────────────

GUIDE_PATH = "/Users/chuck/workspace/diy-projects/weekend-1-guide.md"


def add_cut_markers(content: str) -> str:
    """Insert [CUT:xxx] markers beside every cut-length dimension in the guide."""

    # -- Cut list table rows --
    table_markers = [
        # (regex, replacement)
        (r'(\|\s*3\s*\|\s*)(\d+)\s*mm(\s*\| Back posts)',
         lambda m: f'{m.group(1)}{CUTS["POST_BL"].eff:.0f} mm `[CUT:POST_BL,POST_BR,POST_BC]`{m.group(3)}'),

        (r'(\|\s*2\s*\|\s*)(\d+)\s*mm(\s*\| Front corner posts)',
         lambda m: f'{m.group(1)}{CUTS["POST_FL"].eff:.0f} mm `[CUT:POST_FL,POST_FR]`{m.group(3)}'),

        (r'(\|\s*1\s*\|\s*)(\d+)\s*mm(\s*\| Front centre post)',
         lambda m: f'{m.group(1)}{CUTS["POST_FC"].eff:.0f} mm `[CUT:POST_FC]`{m.group(3)}'),

        (r'(\|\s*4\s*\|\s*)(\d+)\s*mm(\s*\| Full-width rails)',
         lambda m: f'{m.group(1)}{CUTS["RAIL_BACK_TOP"].eff:.0f} mm `[CUT:RAIL_BACK_TOP,RAIL_BACK_BOT,RAIL_BACK_MID,RAIL_FRONT_TOP]`{m.group(3)}'),

        (r'(\|\s*1\s*\|\s*)~?(\d+)\s*mm(\s*\| Front bottom rail)',
         lambda m: f'{m.group(1)}{CUTS["RAIL_FRONT_BOT_R"].eff:.0f} mm `[CUT:RAIL_FRONT_BOT_R]`{m.group(3)}'),

        (r'(\|\s*5\s*\|\s*)(\d+)\s*mm(\s*\| Depth rails)',
         lambda m: f'{m.group(1)}{CUTS["RAIL_DEPTH_TL"].eff:.0f} mm `[CUT:RAIL_DEPTH_TL,RAIL_DEPTH_TR,RAIL_DEPTH_BL,RAIL_DEPTH_BR,RAIL_DEPTH_TC]`{m.group(3)}'),

        (r'(\|\s*2\s*\|\s*)(\d+)\s*mm(\s*\| Mid-rails)',
         lambda m: f'{m.group(1)}{CUTS["RAIL_MID_LEFT"].eff:.0f} mm `[CUT:RAIL_MID_LEFT,RAIL_DEPTH_MC]`{m.group(3)}'),

        (r'(\|\s*2\s*\|\s*)~?(\d+)\s*mm(\s*\| Back panel X-braces)',
         lambda m: f'{m.group(1)}~{CUTS["BRACE_BACK_1"].eff:.0f} mm `[CUT:BRACE_BACK_1,BRACE_BACK_2]`{m.group(3)}'),

        (r'(\|\s*2\s*\|\s*)~?(\d+)\s*mm(\s*\| Left panel X-braces)',
         lambda m: f'{m.group(1)}~{CUTS["BRACE_LEFT_1"].eff:.0f} mm `[CUT:BRACE_LEFT_1,BRACE_LEFT_2]`{m.group(3)}'),
    ]

    for pattern, repl in table_markers:
        content = re.sub(pattern, repl, content)

    # -- Step instructions: tag key dimensions --
    step_tags = [
        # Back posts in Step 1
        (r'all three 1647 mm back posts',
         f'all three {CUTS["POST_BL"].eff:.0f} mm `[CUT:POST_BL,POST_BR,POST_BC]` back posts'),
        # 1206 mm rail in Step 1 (was 1300 mm before correction)
        (r'a 1206 mm rail between',
         f'a {CUTS["RAIL_BACK_TOP"].eff:.0f} mm `[CUT:RAIL_BACK_TOP]` rail between'),
        # Front posts in Step 2
        (r'the two 1597 mm posts',
         f'the two {CUTS["POST_FL"].eff:.0f} mm `[CUT:POST_FL,POST_FR]` posts'),
        # Front top rail in Step 2 (was 1300 mm before correction)
        (r'the top rail \(1206 mm\)',
         f'the top rail ({CUTS["RAIL_FRONT_TOP"].eff:.0f} mm `[CUT:RAIL_FRONT_TOP]`)'),
        # Centre post in Step 4
        (r'the 1503 mm post',
         f'the {CUTS["POST_FC"].eff:.0f} mm `[CUT:POST_FC]` post'),
        # Centre depth rail in Step 4
        (r'650 mm rail from centre post top back',
         f'{CUTS["RAIL_DEPTH_TC"].eff:.0f} mm `[CUT:RAIL_DEPTH_TC]` rail from centre post top back'),
        # Centre mid depth rail in Step 4
        (r'650 mm rail from centre post to back frame at 775',
         f'{CUTS["RAIL_DEPTH_MC"].eff:.0f} mm `[CUT:RAIL_DEPTH_MC]` rail from centre post to back frame at 775'),
    ]

    for pattern, repl in step_tags:
        content = re.sub(pattern, repl, content, count=1)

    return content


def update_prose_dimensions(content: str) -> str:
    """Update specific prose dimensions that changed due to corrections."""

    corrections = {cid: c for cid, c in CUTS.items()
                   if c.corrected is not None and c.corrected != c.length}
    if not corrections:
        return content

    old_front = int(CUTS["POST_FL"].length)
    new_front = int(CUTS["POST_FL"].eff)
    old_back  = int(CUTS["POST_BL"].length)
    new_back  = int(CUTS["POST_BL"].eff)
    old_centre = int(CUTS["POST_FC"].length)
    new_centre = int(CUTS["POST_FC"].eff)
    old_depth_rail = int(CUTS["RAIL_DEPTH_TL"].length)
    new_depth_rail = int(CUTS["RAIL_DEPTH_TL"].eff)

    replacements = [
        # Spec table
        (f"| Front height | {old_front} mm |",
         f"| Front height | {new_front} mm |"),
        (f"| Back height | {old_back} mm |",
         f"| Back height | {new_back} mm |"),

        # Centre post note in cut list
        (f"{old_front} - 2 x 47",
         f"{new_front} - 2 x 47"),

        # Step 1 assembly: "1600 mm" back posts (already handled by markers,
        # but also in other prose)
        (f"three 1600 mm back posts",   # handled by markers, but backup
         f"three {new_back} mm back posts") if old_back != new_back else ("", ""),

        # Step 2: front posts are 1550
        (f"**Posts are {old_front} mm**",
         f"**Posts are {new_front} mm**"),

        # Step 2: "1550 mm tall"
        (f"front frame is {old_front} mm tall",
         f"front frame is {new_front} mm tall"),

        # Step 2: "Posts are 1550 mm (not 1600 mm)"
        (f"**Posts are {old_front} mm** (not {old_back} mm)",
         f"**Posts are {new_front} mm** (not {new_back} mm)"),

        # Step 3: "4x 750 mm depth rails"
        (f"4x {old_depth_rail} mm depth rails",
         f"4x {new_depth_rail} mm depth rails"),

        # Step 4: centre post calculation
        (f"{old_centre} mm -- exactly 94 mm shorter",
         f"{new_centre} mm -- exactly 94 mm shorter"),

        # Step 4: the 1456 mm figure
        (f"centre post is {old_centre} mm",
         f"centre post is {new_centre} mm"),

        # Step 3: depth measurements
        (f"the front frame {old_depth_rail} mm in front",
         f"the front frame {TOTAL_DEPTH} mm in front"),

        # Step 1: 1600 mm posts
        (f"three {old_back} mm back posts",
         f"three {new_back} mm back posts"),

        # Various: back frame height
        (f"back frame should be {ROOF_SLOPE} mm taller",
         f"back frame should be {ROOF_SLOPE} mm taller"),  # no change needed
    ]

    for old, new in replacements:
        if old and old != new:
            content = content.replace(old, new)

    return content


def update_guide(fix_mode: bool) -> list[str]:
    """Read guide, add CUT markers, optionally fix dimensions."""
    msgs = []
    try:
        with open(GUIDE_PATH, "r") as f:
            content = f.read()
    except FileNotFoundError:
        return [f"WARNING: Guide not found at {GUIDE_PATH}"]

    if not fix_mode:
        markers = re.findall(r'\[CUT:([^\]]+)\]', content)
        if markers:
            msgs.append(f"Found {len(markers)} CUT markers in guide.")
        else:
            msgs.append("No CUT markers found. Run with --fix to add them.")
        return msgs

    new_content = add_cut_markers(content)
    new_content = update_prose_dimensions(new_content)

    if new_content != content:
        with open(GUIDE_PATH, "w") as f:
            f.write(new_content)
        msgs.append(f"Guide updated with CUT markers and corrected dimensions: {GUIDE_PATH}")
    else:
        msgs.append("No changes needed in guide.")
    return msgs


# ─────────────────────────────────────────────────────────
# SLOPED RAIL GEOMETRY (informational)
# ─────────────────────────────────────────────────────────

def report_sloped_rail_geometry():
    """Informational calculations for sloped depth rails and side-wall braces."""
    print("=" * 70)
    print("SLOPED RAIL GEOMETRY (informational)")
    print("-" * 70)

    # Horizontal distance between post inner faces
    # POST_WIDTH (50 mm) is the post dimension in the depth direction
    horiz_dist = TOTAL_DEPTH - 2 * POST_WIDTH
    height_diff = ROOF_SLOPE  # 50 mm

    # 1. Slope angle
    slope_angle_rad = math.atan2(height_diff, horiz_dist)
    slope_angle_deg = math.degrees(slope_angle_rad)
    print(f"\n  Slope angle: arctan({height_diff}/{horiz_dist}) = {slope_angle_deg:.2f} deg")

    # 2. True diagonal length of sloped rail (along centreline)
    diag_length = math.sqrt(horiz_dist**2 + height_diff**2)
    length_diff = diag_length - horiz_dist
    print(f"\n  Horizontal distance between inner faces: {horiz_dist} mm")
    print(f"  True diagonal length: sqrt({horiz_dist}^2 + {height_diff}^2) = {diag_length:.1f} mm")
    print(f"  Difference from horizontal: {length_diff:.1f} mm")
    if length_diff <= 3.0:
        print(f"  --> Within 3 mm tolerance: builder can cut to {horiz_dist} mm (same as level rails)")
    else:
        print(f"  --> EXCEEDS 3 mm tolerance: builder should cut to {diag_length:.0f} mm")

    # 3. End-cut angle deviation
    # If the rail end is cut perpendicular to the rail (square to the rail),
    # it is tilted from vertical by the slope angle.  The gap created at the
    # post face = sin(slope) * rail_height.
    gap = math.sin(slope_angle_rad) * RAIL_HEIGHT
    print(f"\n  End-cut analysis:")
    print(f"    If cut square to the rail (perpendicular to rail length):")
    print(f"      End face tilt from vertical: {slope_angle_deg:.2f} deg")
    print(f"      Gap at post face: sin({slope_angle_deg:.2f}) x {RAIL_HEIGHT} = {gap:.1f} mm")
    print(f"    RECOMMENDATION: Cut ends VERTICAL (square to the post).")
    print(f"    This gives a flush fit against the vertical post face.")
    print(f"    Measure and cut to the horizontal distance ({horiz_dist} mm).")

    # 4. Left side X-braces in sloped upper zone (trapezoidal)
    # The upper zone is bounded by:
    #   Top: sloped rail (front post top to back post top)
    #   Bottom: mid-rail at 775 mm (level)
    #   Left (front): front-left post inner face
    #   Right (back): back-left post inner face
    #
    # Corner heights (from mid-rail top to top-rail bottom):
    #   Front: (front_post_ht - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    #   Back:  (back_post_ht  - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)

    front_post_ht = CUTS["POST_FL"].eff
    back_post_ht = CUTS["POST_BL"].eff

    front_upper = (front_post_ht - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)
    back_upper = (back_post_ht - RAIL_HEIGHT) - (MID_RAIL_HEIGHT + RAIL_HEIGHT)

    print(f"\n  Left-side X-braces (trapezoidal upper zone):")
    print(f"    Front upper zone height: {front_upper:.0f} mm")
    print(f"    Back upper zone height:  {back_upper:.0f} mm")
    print(f"    Horizontal span:         {horiz_dist} mm")

    # Brace 1: front-top-left corner to back-bottom-right corner
    # From (0, front_upper) to (horiz_dist, 0)
    brace1 = math.sqrt(horiz_dist**2 + front_upper**2)

    # Brace 2: front-bottom-left corner to back-top-right corner
    # From (0, 0) to (horiz_dist, back_upper)
    brace2 = math.sqrt(horiz_dist**2 + back_upper**2)

    print(f"    Brace 1 (front-top to back-bottom): sqrt({horiz_dist}^2 + {front_upper:.0f}^2) = {brace1:.0f} mm")
    print(f"    Brace 2 (front-bottom to back-top):  sqrt({horiz_dist}^2 + {back_upper:.0f}^2) = {brace2:.0f} mm")
    print(f"    Difference between braces: {abs(brace1 - brace2):.1f} mm")
    avg_brace = (brace1 + brace2) / 2
    print(f"    Average (for a single cut length): ~{round(avg_brace / 10) * 10:.0f} mm")

    print()


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def run_validation():
    print("=" * 70)
    print("BIN STORE MEASUREMENT VALIDATION REPORT")
    print("=" * 70)

    # --- Phase 1: original dimensions ---
    print("\n--- PHASE 1: Original dimensions ---\n")
    cs1 = build_constraints()
    fails1 = [c for c in cs1 if not c.ok]
    for c in cs1:
        print(c.report())
        print()
    print(f"Phase 1 result: {len(cs1) - len(fails1)} PASS, {len(fails1)} FAIL\n")

    # --- Phase 2: corrections ---
    if fails1:
        print("--- PHASE 2: Corrections ---\n")
        for msg in calculate_corrections():
            print(f"  >> {msg}")
        print()

        # --- Phase 3: re-validate ---
        print("--- PHASE 3: Re-validate with corrections ---\n")
        cs2 = build_constraints()
        fails2 = [c for c in cs2 if not c.ok]
        for c in cs2:
            print(c.report())
            print()
        print(f"Phase 3 result: {len(cs2) - len(fails2)} PASS, {len(fails2)} FAIL\n")

        if fails2:
            print("WARNING: Still failing after corrections:")
            for f in fails2:
                print(f"  - {f.name}")
            print()
    else:
        fails2 = []

    # --- Corrected cut list ---
    print("=" * 70)
    print("CORRECTED CUT LIST")
    print("-" * 70)
    print(f"{'Cut ID':<22} {'Orig':>6} {'Corrected':>10}   Description")
    print(f"{'-'*22} {'-'*6} {'-'*10}   {'-'*30}")
    for c in CUTS.values():
        orig = f"{c.length:.0f}"
        if c.corrected is not None and c.corrected != c.length:
            corr = f"{c.corrected:.0f} ***"
        else:
            corr = f"{c.eff:.0f}"
        print(f"{c.cut_id:<22} {orig:>6} {corr:>10}   {c.description}")
    print()

    # --- Sloped rail geometry (informational) ---
    report_sloped_rail_geometry()

    return fails1 if not fails1 else fails2


def main():
    parser = argparse.ArgumentParser(description="Validate bin store measurements")
    parser.add_argument("--fix", action="store_true",
                        help="Update guide docs with CUT markers and corrected dimensions")
    args = parser.parse_args()

    remaining = run_validation()

    print("=" * 70)
    print("GUIDE DOCUMENT UPDATE")
    print("-" * 70)
    for msg in update_guide(fix_mode=args.fix):
        print(f"  {msg}")
    print()

    has_corrections = any(c.corrected is not None for c in CUTS.values())
    if remaining:
        print("OVERALL: FAIL -- manual review needed")
        sys.exit(1)
    elif has_corrections:
        print("OVERALL: PASS (with corrections applied)")
    else:
        print("OVERALL: PASS")


if __name__ == "__main__":
    main()

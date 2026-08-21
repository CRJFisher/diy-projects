// ─────────────────────────────────────────────────────────
// Courtyard Nook — SITE CONSTRAINTS
// What is already there and cannot be changed. Measured on site.
// All dimensions in mm. Site notes were recorded in cm; values here are ×10.
//
// Nothing the shed is *made of* belongs in this file — that is
// `parameters.scad`, which includes this one.
// ─────────────────────────────────────────────────────────
//
// Viewpoint: standing in the courtyard looking into the nook.
// Plan: courtyard is a wide rectangle; the nook is on the far side,
// flush left — left edge of nook = left edge of courtyard.
//
// Walls:
//   Left        = brick (nook enclosure)
//   Back        = brick for the first 820mm from the left, then the
//                 neighbour's house wall takes over and rises above it
//   Right       = house wall (tall; bathroom extractor)
//
// Origin: front-left of the nook opening, ground level
//   X: left → right
//   Y: opening → into the nook (toward the back wall)
//   Z: up

// ─── Nook clear envelope (interior face to interior face) ───
// Right-side depth (house wall → main courtyard) is the clear depth.
// Left-side 1800 was to a courtyard wall-edge feature, not an angled back.
nook_width = 1720;
nook_depth = 2000;              // right side to main courtyard
left_to_wall_edge = 1800;       // site note: left side to courtyard wall edge

// ─── Wall heights ───
brick_wall_height = 1950;             // left + back brick in the nook
house_wall_height = 3000;             // right wall (house)
courtyard_left_wall_height = 4000;    // left wall where it meets the courtyard

// Schematic masonry thickness (not measured — visual only)
wall_t = 100;

// Courtyard wall stubs beyond the nook (1–2 m)
courtyard_stub_len = 1500;

// ─── Back wall: brick run, then the neighbour's house ───
// MEASURED: the back of the nook is not one flat wall. From the left
// corner the brick runs 820mm, then the neighbour's house wall
// interrupts it and continues to the right-hand (house) wall.
back_brick_run = 820;                             // left corner → neighbour's wall
neighbour_wall_run = nook_width - back_brick_run; // 900 — derived

// ─── Neighbour's gutter (one of the two roof height constraints) ───
// The gutter does NOT run across our back wall. It runs along the neighbour's
// eaves, away from us (+Y) into their property, and only its near END reaches
// back over our nook — by a few cm past the back wall plane. That end is the
// only part of it in our space, and it is the part we have to duck under.
//
// MEASURED: the underside sits 335mm above the top of the flat (brick) part
// of the back wall.
gutter_underside_above_brick = 335;                                    // measured
gutter_underside_z = brick_wall_height + gutter_underside_above_brick;  // 2285 — derived

// ASSUMED — "a few cm" was eyeballed on site, not measured. Remeasure before
// committing to a roof: how far the gutter END reaches into the nook (−Y).
gutter_projection = 50;

// Schematic gutter section and length (not measured — visual only).
gutter_dia = 112;
gutter_run = 1400;   // how far it carries on into their property (+Y)

// Sits just left of the step in the back wall, hanging off the west face of
// the neighbour's flank wall. X position inferred from the sketch, not measured.
gutter_centre_x = back_brick_run - gutter_dia / 2;   // 764 — derived

// ─── Neighbour's roof above the gutter (all schematic, none measured) ───
neighbour_eaves_z    = gutter_underside_z + gutter_dia;  // top of fascia — derived
neighbour_roof_pitch = 22;      // degrees, rising toward +X (right)
neighbour_roof_run   = 1400;    // how far the drawn roof slope extends in X
neighbour_roof_depth = 1200;    // how far it extends away from us in +Y
neighbour_roof_t     = 50;

// ─── Bathroom extractor on the right (house) wall ───
// "68 from left of extractor to edge with rest of the courtyard"
// → along the house wall, left edge of extractor is 680mm in from Y=0.
extractor_bottom_z = 2000;
extractor_w = 150;  // along the wall (Y)
extractor_h = 150;
extractor_d = 40;   // projects into the nook (−X from house face)
extractor_from_courtyard_edge = 680;

// ─── Site rendering ───
floor_ghost_t     = 2;
floor_ghost_alpha = 0.45;
curve_fn          = 48;     // $fn for the gutter

show_nook_walls      = true;
show_courtyard_stubs = true;
show_extractor       = true;
show_floor_ghost     = true;
show_neighbour_roof  = true;

brick_colour        = [0.72, 0.42, 0.32];
house_colour        = [0.82, 0.80, 0.76];
neighbour_colour    = [0.66, 0.60, 0.56];
neighbour_roof_col  = [0.40, 0.36, 0.34];
gutter_colour       = [0.25, 0.25, 0.27];
extractor_colour    = [0.35, 0.35, 0.38];
floor_colour        = [0.55, 0.62, 0.55];

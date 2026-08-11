// ─────────────────────────────────────────────────────────
// Courtyard Nook Parameters
// All dimensions in mm. Modules never contain magic numbers.
// Site notes were recorded in cm; values here are ×10.
// ─────────────────────────────────────────────────────────
//
// Viewpoint: standing in the courtyard looking into the nook.
// Plan: courtyard is a wide rectangle; the nook is on the far side,
// flush left — left edge of nook = left edge of courtyard.
//
// Walls:
//   Left + back = brick (nook enclosure)
//   Right       = house wall (tall; bathroom extractor)
//
// Origin: front-left of the nook opening, ground level
//   X: left → right
//   Y: opening → into the nook (toward the back wall)
//   Z: up

// Nook clear envelope (interior face to interior face)
// Right-side depth (house wall → main courtyard) is the clear depth.
// Left-side 1800 was to a courtyard wall-edge feature, not an angled back.
nook_width = 1720;
nook_depth = 2000;              // right side to main courtyard
left_to_wall_edge = 1800;       // site note: left side to courtyard wall edge

// Wall heights
brick_wall_height = 1950;             // left + back brick in the nook
house_wall_height = 3000;             // right wall (house)
courtyard_left_wall_height = 4000;    // left wall where it meets the courtyard

// Schematic masonry thickness (not measured — visual only)
wall_t = 100;

// Courtyard wall stubs beyond the nook (1–2 m)
courtyard_stub_len = 1500;

// Bathroom extractor on the right (house) wall
// "68 from left of extractor to edge with rest of the courtyard"
// → along the house wall, left edge of extractor is 680mm in from Y=0.
extractor_bottom_z = 2000;
extractor_w = 150;  // along the wall (Y)
extractor_h = 150;
extractor_d = 40;   // projects into the nook (−X from house face)
extractor_from_courtyard_edge = 680;

// Display toggles
show_nook_walls      = true;
show_courtyard_stubs = true;
show_extractor       = true;
show_floor_ghost     = true;

// Colours
brick_colour     = [0.72, 0.42, 0.32];
house_colour     = [0.82, 0.80, 0.76];
extractor_colour = [0.35, 0.35, 0.38];
floor_colour     = [0.55, 0.62, 0.55];

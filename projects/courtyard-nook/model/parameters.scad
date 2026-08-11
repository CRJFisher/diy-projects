// ─────────────────────────────────────────────────────────
// Courtyard Nook Parameters
// All dimensions in mm. Modules never contain magic numbers.
// Site notes were recorded in cm; values here are ×10.
// ─────────────────────────────────────────────────────────
//
// Viewpoint: standing in the courtyard looking into the nook.
// Plan context: courtyard is a wide rectangle; the nook sits on the
// far (back) side, flush left — left edge of nook = left edge of courtyard.
//
// Origin: front-left of the nook opening, ground level
//   X: left → right
//   Y: opening → into the nook (toward the back wall)
//   Z: up

// Nook clear envelope (interior face to interior face)
nook_width      = 1720;  // opening / clear width
nook_depth_left = 1800;  // left side, opening → back
nook_depth_right = 2000; // right side, opening → main courtyard edge

// Wall heights
wall_height = 1950;           // measured courtyard / nook wall height
building_wall_height = 2400;  // taller back (building) face so the extractor sits on it

// Schematic masonry thickness (not measured — visual only)
wall_t = 100;

// Courtyard wall stubs beyond the nook (1–2 m)
courtyard_stub_len = 1500;

// Bathroom extractor (on back wall, facing into the nook)
// "68 from left of extractor to edge with rest of the courtyard"
// → left edge of extractor is 680mm left of the nook's right (courtyard) edge.
extractor_bottom_z = 2000;
extractor_w = 150;
extractor_h = 150;
extractor_d = 40;  // projects into the nook
extractor_left_from_nook_right = 680;
extractor_x = nook_width - extractor_left_from_nook_right;  // left edge of vent

// Display toggles
show_nook_walls      = true;
show_courtyard_stubs = true;
show_extractor       = true;
show_floor_ghost     = true;

// Colours
wall_colour      = [0.78, 0.76, 0.72];
building_colour  = [0.70, 0.68, 0.64];
extractor_colour = [0.35, 0.35, 0.38];
floor_colour     = [0.55, 0.62, 0.55];

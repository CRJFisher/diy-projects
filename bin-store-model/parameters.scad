// ─────────────────────────────────────────────────────────
// Bin Store Parameters
// All dimensions in mm. Modules never contain magic numbers.
// ─────────────────────────────────────────────────────────

// Timber cross-sections (50x47mm pressure-treated softwood)
// When used as posts: 47mm left-right (X), 50mm front-back (Y)
// This matches the CLAUDE.md width breakdown: 47 + 490 + 323 + 440 = 1300
post_face = 47;   // post X dimension (left-right as seen from front)
post_side = 50;   // post Y dimension (front-back)
rail_h    = 47;   // rail height (vertical cross-section)
rail_d    = 50;   // rail depth (front-back for L-R rail, or L-R for F-B rail)
brace_t   = 15;   // brace thickness
brace_w   = 38;   // brace width

// Battens and plywood
batten_w = 50;
batten_h = 22;
ply_t = 18;

// Cladding and door geometry
featheredge_w = 125;
featheredge_thick = 15;
featheredge_thin = 5;
featheredge_overlap = 25;
featheredge_cover = featheredge_w - featheredge_overlap;
hardboard_t = 6;
door_frame_w = 70;
door_frame_t = 38;
door_gap = 5;
door_head_clearance = 5;
front_panel_post_overlap = post_side;

// Roof overhang
roof_overhang = 25;   // overhang on front, back, and sides

// Overall envelope
total_width  = 1300;
total_depth  = 750;
front_height = 1597;
back_height  = 1647;
roof_slope   = 50;   // back_height - front_height

// Section geometry
left_section_clear  = 780;   // door opening width
right_section_width = 440;   // recycling area width
mid_rail_height     = 775;   // mid-rail from ground
internal_depth      = 650;   // between inner faces of front/back posts

// Derived values
full_rail_length     = total_width - 2 * post_face;        // 1206
depth_rail_length    = internal_depth;                      // 650

// Centre post X positions
//   Back centre post: X = post_face + left_section_clear = 827
//   Front centre post: 47mm further right so it sits on the right bottom rail
back_centre_post_x  = post_face + left_section_clear;      // 827
front_centre_post_x = back_centre_post_x + post_face;      // 874

// Front centre post height (between top and bottom rails)
centre_post_height = front_height - 2 * rail_h;             // 1503

// Right front bottom rail: from front centre post to right corner post
right_front_bot_rail = total_width - post_face - front_centre_post_x;  // 379

// Shelf geometry (right section)
// Total usable height = front_height - rail_h = 1550mm (floor to bottom of top rail)
// Three shelves of 69mm each (47 rail + 22 batten), leaving 1343mm for three compartments
// 1343 / 3 = 447.67, rounded to 448, 448, 447 (bottom to top)
shelf_thickness      = rail_h + batten_h;                                     // 69
shelf_space          = 448;
bottom_shelf_rail_z  = 0;                                                     // floor
lower_shelf_rail_z   = shelf_thickness + shelf_space;                         // 517
upper_shelf_rail_z   = 2 * (shelf_thickness + shelf_space);                   // 1034
shelf_batten_length  = total_width - front_centre_post_x;                     // 426
num_shelf_battens    = 5;

// Bin dimensions (for ghost models)
wheelie_w = 490;  wheelie_d = 570;  wheelie_h = 1060;
caddy_w   = 323;  caddy_d   = 400;  caddy_h   = 400;
recycle_w = 430;  recycle_d = 570;  recycle_h = 300;

// Display toggles
show_frame    = true;
show_roof     = true;
show_cladding = true;
show_door     = true;
show_shelves  = true;
show_bins     = true;
show_edges    = true;

// Door angle (0 = closed, 90 = fully open)
door_angle = 0;

// Colours
timber_colour = [0.76, 0.60, 0.42];
ply_colour    = [0.85, 0.75, 0.60];
brace_colour  = [0.65, 0.50, 0.35];
edge_colour   = [0.15, 0.10, 0.05];
cladding_colour = [0.84, 0.70, 0.18];
cladding_colour_alt = [0.68, 0.55, 0.12];   // alternate-row shade so boards read as individual planks
hardboard_colour = [0.50, 0.46, 0.40];

// ─────────────────────────────────────────────────────────
// Courtyard Nook — SHED BUILD PARAMETERS
// Dimensions of the thing we are building. This file is the input to
// the cut-list script (`extraction.py` → `data/cut_list.json`), so every
// number a cut depends on must live here, not inside a module.
//
// Site measurements (walls, gutter, extractor) live in `site.scad`,
// which this file includes so the build can be derived from the site.
// All dimensions in mm.
// ─────────────────────────────────────────────────────────

include <site.scad>

// ─── What the site allows us to build into ───
// Absolute outer envelope, before any working clearance to the walls.
shed_max_width = nook_width;
shed_max_depth = nook_depth;

// ─── The two things the roof must pass under ───
// Each is a fixed obstruction at a known depth into the nook, so together
// they fix the highest roof plane we can build — and therefore its pitch.
//
//   near the opening : the bathroom extractor, bottom at 2000mm
//   at the back wall : the neighbour's gutter end, underside at 2285mm
//
// The gutter is the higher of the two and sits deeper in, so the roof rises
// toward the back and drains out toward the courtyard opening.
roof_extractor_clearance = 25;   // ASSUMED — raise it if the fan needs free air
roof_gutter_clearance    = 25;   // ASSUMED working clearance under the lip

// The extractor's binding point is its FAR edge (deepest into the nook),
// because the roof is rising as it passes beneath it.
roof_limit_y_at_extractor = extractor_from_courtyard_edge + extractor_w;   // 830
roof_limit_z_at_extractor = extractor_bottom_z - roof_extractor_clearance; // 1975

// The gutter's binding point is the back wall, where our roof stops and is
// therefore at its highest under the overhanging end.
roof_limit_y_at_gutter = nook_depth;                                    // 2000
roof_limit_z_at_gutter = gutter_underside_z - roof_gutter_clearance;    // 2260

// The limit plane runs through both points. This pitch is a ceiling, not a
// choice: build shallower and you lose headroom, steeper and you hit something.
roof_max_rise  = roof_limit_z_at_gutter - roof_limit_z_at_extractor;   // 285
roof_max_run   = roof_limit_y_at_gutter - roof_limit_y_at_extractor;   // 1170
roof_max_fall  = roof_max_rise / roof_max_run;                         // 0.2436
roof_max_pitch = atan(roof_max_fall);                                  // 13.7 deg

// Where that plane crosses the nook opening (Y=0) and the back wall.
roof_limit_z_at_front = roof_limit_z_at_extractor
                      - roof_limit_y_at_extractor * roof_max_fall;     // 1773

// Left of `back_brick_run` the back brick tops out at `brick_wall_height` and
// what sits above it has not been measured — do not assume that headroom is
// free until it is checked on site.

// ─── TODO — not yet designed, and nothing can be cut until they are ───
// Add here, then teach `extraction.py` to emit rows for each:
//   * frame:    post section, rail section, post positions, frame height
//   * roof:     pitch, fall direction, rafter section/spacing, deck material
//   * cladding: board type, coverage, batten section
//   * floor:    bearer section, deck material
//   * openings: door/access width, height, clearances

// ─── Shed rendering ───
ghost_alpha      = 0.30;
ghost_t          = 2;
show_roof_limit  = true;   // translucent plane at the highest buildable roof
clearance_colour = [0.95, 0.35, 0.25];

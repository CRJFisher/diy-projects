// ─────────────────────────────────────────────────────────
// Bin Store Shelves
// Batten slats sitting on top of the shelf depth rails
// in the right (recycling) section
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// ── Primitives ──────────────────────────────────────────

module shelf_batten(length) {
    // Single batten running along X, 50mm (Y) x 22mm (Z)
    color(timber_colour) cube([length, batten_w, batten_h]);
}

// ── Assemblies ──────────────────────────────────────────

module shelf(z_height) {
    // Battens run left-to-right (X) spanning between the centre
    // and right depth rails. Spaced evenly along Y (front to back).
    // z_height is the top of the supporting depth rail.
    spacing = (depth_rail_length - batten_w) / (num_shelf_battens - 1);

    for (i = [0 : num_shelf_battens - 1]) {
        y = post_side + i * spacing;
        translate([front_centre_post_x, y, z_height])
            shelf_batten(shelf_batten_length);
    }
}

module shelves() {
    // Bottom shelf: battens on top of the floor depth rails
    shelf(bottom_shelf_rail_z + rail_h);

    // Lower shelf: battens on top of the lower depth rails
    shelf(lower_shelf_rail_z + rail_h);

    // Upper shelf: battens on top of the upper depth rails
    shelf(upper_shelf_rail_z + rail_h);
}

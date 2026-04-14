// ─────────────────────────────────────────────────────────
// Bin Store Roof
// Battens (left-to-right) + plywood deck, following slope
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// ── Primitives ──────────────────────────────────────────

module roof_batten(length) {
    // Single batten running along X, 50mm (Y) x 22mm (Z)
    color(timber_colour) cube([length, batten_w, batten_h]);
}

module roof_deck_panel() {
    // 18mm plywood following the slope, with overhang on all sides
    deck_width = total_width + 2 * roof_overhang;
    deck_depth = total_depth + 2 * roof_overhang;
    // Front overhang drops slightly, back overhang rises slightly
    front_z = -(roof_overhang / total_depth) * roof_slope;
    back_z  = ((total_depth + roof_overhang) / total_depth) * roof_slope;

    color(ply_colour)
    translate([-roof_overhang, -roof_overhang, front_z])
    hull() {
        cube([deck_width, 0.01, ply_t]);
        translate([0, deck_depth, back_z - front_z])
            cube([deck_width, 0.01, ply_t]);
    }
}

// ── Assemblies ──────────────────────────────────────────

module roof_battens() {
    // 4 battens spaced across the depth, following the slope
    // Each batten's Z depends on its Y position
    num_battens = 4;
    spacing = (total_depth - batten_w) / (num_battens - 1);

    for (i = [0 : num_battens - 1]) {
        y = i * spacing;
        z = (y / total_depth) * roof_slope;
        translate([0, y, z])
            roof_batten(total_width);
    }
}

module roof_deck() {
    // Plywood sits on top of battens
    translate([0, 0, batten_h])
        roof_deck_panel();
}

// ── Complete Roof ───────────────────────────────────────

module roof() {
    // Position at top of frame (on top of top rails)
    translate([0, 0, front_height])
    {
        roof_battens();
        roof_deck();
    }
}

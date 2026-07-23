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

// ── Locating blocks ─────────────────────────────────────
// The roof is gravity-rested. Four blocks fixed under the deck drop into the
// frame's top internal corners: each bears against the side rail (locks X) and
// the front/back rail (locks Y). Opposing corners trap the roof both ways.

module roof_locating_block() {
    color(brace_colour) cube([roof_block_len, roof_block_width, roof_block_drop]);
}

module roof_locating_blocks() {
    inner_x_left  = rail_d;                                      // 50
    inner_x_right = total_width - rail_d - roof_block_len;       // 1180
    inner_y_front = rail_d;                                      // 50
    inner_y_back  = total_depth - post_side - roof_block_width;  // 650
    corners = [
        [inner_x_left,  inner_y_front],
        [inner_x_right, inner_y_front],
        [inner_x_left,  inner_y_back],
        [inner_x_right, inner_y_back],
    ];
    for (c = corners) {
        // Deck underside follows the slope, so the block top rises with Y
        z_top = batten_h + (c[1] / total_depth) * roof_slope;
        translate([c[0], c[1], z_top - roof_block_drop])
            roof_locating_block();
    }
}

// ── Complete Roof ───────────────────────────────────────

module roof() {
    // Position at top of frame (on top of top rails)
    translate([0, 0, front_height])
    {
        roof_battens();
        roof_deck();
        roof_locating_blocks();
    }
}

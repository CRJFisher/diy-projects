// ─────────────────────────────────────────────────────────
// Ghost Bins -- translucent models for fit-checking
// ─────────────────────────────────────────────────────────

include <parameters.scad>

module wheelie_bin() {
    color([0.2, 0.7, 0.2, 0.45])
    cube([wheelie_w, wheelie_d, wheelie_h]);
}

module food_caddy() {
    color([0.6, 0.4, 0.2, 0.45])
    cube([caddy_w, caddy_d, caddy_h]);
}

module recycling_box() {
    color([0.2, 0.3, 0.8, 0.45])
    cube([recycle_w, recycle_d, recycle_h]);
}

module bins() {
    // Wheelie bin: left section, centred in depth, on the floor
    translate([post_face, post_side + (internal_depth - wheelie_d) / 2, rail_h])
        wheelie_bin();

    // Food caddy: left section, next to wheelie bin
    translate([post_face + wheelie_w, post_side + (internal_depth - caddy_d) / 2, rail_h])
        food_caddy();

    // Recycling boxes: right section, 3 stacked
    // X starts after front centre post
    recycle_x = front_centre_post_x + post_face;
    recycle_y = post_side + (internal_depth - recycle_d) / 2;

    // Bottom box (on floor rail)
    translate([recycle_x, recycle_y, rail_h])
        recycling_box();

    // Middle box
    translate([recycle_x, recycle_y, rail_h + recycle_h + 20])
        recycling_box();

    // Top box
    translate([recycle_x, recycle_y, rail_h + 2 * (recycle_h + 20)])
        recycling_box();
}

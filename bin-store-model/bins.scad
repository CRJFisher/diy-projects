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
    translate([post_face, post_side + (internal_depth - wheelie_d) / 2, 0])
        wheelie_bin();

    // Food caddy: left section, next to wheelie bin
    translate([post_face + wheelie_w, post_side + (internal_depth - caddy_d) / 2, 0])
        food_caddy();

    // Recycling boxes: right section, one per shelf compartment
    // X starts after front centre post
    recycle_x = front_centre_post_x;
    recycle_y = post_side + (internal_depth - recycle_d) / 2;

    // Bottom box (on bottom shelf battens)
    translate([recycle_x, recycle_y, bottom_shelf_rail_z + rail_h + batten_h])
        recycling_box();

    // Middle box (on lower shelf battens)
    translate([recycle_x, recycle_y, lower_shelf_rail_z + rail_h + batten_h])
        recycling_box();

    // Top box (on upper shelf battens)
    translate([recycle_x, recycle_y, upper_shelf_rail_z + rail_h + batten_h])
        recycling_box();
}

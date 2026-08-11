// ─────────────────────────────────────────────────────────
// Courtyard Nook — Walls & site envelope
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// Left brick wall (interior at X=0), thickness outward (−X)
module nook_left_wall() {
    color(brick_colour)
        translate([-wall_t, 0, 0])
            cube([wall_t, nook_depth, brick_wall_height]);
}

// Back brick wall (interior at Y=nook_depth), straight across; thickness outward (+Y)
module nook_back_wall() {
    color(brick_colour)
        translate([0, nook_depth, 0])
            cube([nook_width, wall_t, brick_wall_height]);
}

// Right house wall (interior at X=nook_width), thickness outward (+X)
module nook_right_wall() {
    color(house_colour)
        translate([nook_width, 0, 0])
            cube([wall_t, nook_depth, house_wall_height]);
}

// Floor ghost of the rectangular nook footprint
module nook_floor() {
    color(floor_colour, 0.45)
        cube([nook_width, nook_depth, 2]);
}

// Bathroom extractor on the house (right) wall, projecting into the nook
module bathroom_extractor() {
    color(extractor_colour)
        translate([
            nook_width - extractor_d,
            extractor_from_courtyard_edge,
            extractor_bottom_z
        ])
            cube([extractor_d, extractor_w, extractor_h]);
}

// Courtyard stubs beyond the nook opening
//
// 1) Left wall continues past the opening (−Y) — rises high (~4 m)
// 2) Far courtyard / house return continues past the nook (+X) along the
//    opening line (Y=0), schematic only
module courtyard_stubs() {
    // Tall left courtyard wall (same plane as nook left brick)
    color(brick_colour)
        translate([-wall_t, -courtyard_stub_len, 0])
            cube([wall_t, courtyard_stub_len, courtyard_left_wall_height]);

    // Stub along the courtyard far edge, right of the nook opening
    color(house_colour)
        translate([nook_width, -wall_t, 0])
            cube([courtyard_stub_len, wall_t, house_wall_height]);
}

module nook_walls() {
    nook_left_wall();
    nook_back_wall();
    nook_right_wall();
}

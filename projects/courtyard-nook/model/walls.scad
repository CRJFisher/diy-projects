// ─────────────────────────────────────────────────────────
// Courtyard Nook — Walls & site envelope
// Geometry of what is already there. Driven by `site.scad` only —
// nothing here may depend on the shed's own dimensions.
// ─────────────────────────────────────────────────────────

include <site.scad>

// Left brick wall (interior at X=0), thickness outward (−X)
module nook_left_wall() {
    color(brick_colour)
        translate([-wall_t, 0, 0])
            cube([wall_t, nook_depth, brick_wall_height]);
}

// Back brick wall (interior at Y=nook_depth), thickness outward (+Y).
// Runs only `back_brick_run` from the left corner — beyond that the
// neighbour's house wall takes over.
module nook_back_wall() {
    color(brick_colour)
        translate([0, nook_depth, 0])
            cube([back_brick_run, wall_t, brick_wall_height]);
}

// Neighbour's house wall — completes the back of the nook from
// `back_brick_run` across to the house wall, rising past the brick to the
// eaves. Assumed flush with the brick back face (Y=nook_depth); not measured.
module neighbour_house_wall() {
    color(neighbour_colour)
        translate([back_brick_run, nook_depth, 0])
            cube([neighbour_wall_run, wall_t, neighbour_eaves_z]);
}

// Neighbour's gutter — runs along their eaves away from us (+Y), so almost
// all of it is over their property. Only its near end reaches back over our
// nook, by `gutter_projection`, and that end is what our roof must clear.
module neighbour_gutter() {
    color(gutter_colour)
        translate([
            gutter_centre_x,
            nook_depth - gutter_projection,
            gutter_underside_z + gutter_dia / 2
        ])
            rotate([-90, 0, 0])
                cylinder(h = gutter_run, d = gutter_dia, $fn = curve_fn);
}

// Neighbour's roof above the gutter, sloping up to the right. Schematic
// context only — pitch, run and depth are all unmeasured.
module neighbour_roof() {
    color(neighbour_roof_col)
        translate([gutter_centre_x, nook_depth - gutter_projection, neighbour_eaves_z])
            rotate([0, -neighbour_roof_pitch, 0])
                cube([neighbour_roof_run, neighbour_roof_depth, neighbour_roof_t]);
}

// Right house wall (interior at X=nook_width), thickness outward (+X)
module nook_right_wall() {
    color(house_colour)
        translate([nook_width, 0, 0])
            cube([wall_t, nook_depth, house_wall_height]);
}

// Floor ghost of the rectangular nook footprint
module nook_floor() {
    color(floor_colour, floor_ghost_alpha)
        cube([nook_width, nook_depth, floor_ghost_t]);
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
    neighbour_house_wall();
    neighbour_gutter();
    nook_right_wall();
}

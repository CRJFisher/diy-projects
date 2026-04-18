// ─────────────────────────────────────────────────────────
// Bin Store Door
// Framed door with featheredge infill
// ─────────────────────────────────────────────────────────

include <parameters.scad>
use <cladding.scad>

module door_stile(height) {
    color(timber_colour)
        cube([door_frame_w, door_frame_t, height]);
}

module door_rail(length) {
    color(timber_colour)
        cube([length, door_frame_t, door_frame_w]);
}

module door_panel(width, height) {
    inner_width = max(0, width - 2 * door_frame_w);
    inner_height = max(0, height - 2 * door_frame_w);

    door_stile(height);

    translate([width - door_frame_w, 0, 0])
        door_stile(height);

    translate([door_frame_w, 0, 0])
        door_rail(inner_width);

    translate([door_frame_w, 0, height - door_frame_w])
        door_rail(inner_width);

    if (inner_width > 0 && inner_height > 0) {
        translate([0, -featheredge_thick, 0])
            front_featheredge_panel(width, height);
    }
}

module door(angle = door_angle) {
    door_width = front_centre_post_x - (post_face + door_gap);
    door_height = front_height - rail_h - 2 * door_gap - door_head_clearance;

    rotate([0, 0, -angle])
        door_panel(door_width, door_height);
}

module door_assembly() {
    translate([post_face + door_gap, post_side - door_frame_t, door_gap])
        door();
}

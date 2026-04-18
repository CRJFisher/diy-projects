// ─────────────────────────────────────────────────────────
// Bin Store Cladding
// Featheredge walls and hardboard front panel
// ─────────────────────────────────────────────────────────

include <parameters.scad>

module featheredge_board(length) {
    color(cladding_colour)
        rotate([-90, 0, 0])
            linear_extrude(height = length)
                polygon([
                    [0, 0],
                    [featheredge_thin, 0],
                    [featheredge_thick, featheredge_w],
                    [0, featheredge_w]
                ]);
}

module featheredge_course_outlines(length, board_count) {
    if (show_edges) {
        face_x = featheredge_thin
            + (featheredge_thick - featheredge_thin) * (featheredge_cover / featheredge_w)
            - 0.8;

        color(edge_colour)
            for (i = [1 : board_count - 1]) {
                translate([face_x, 0, i * featheredge_cover - 0.5])
                    cube([0.8, length, 1.0]);
            }
    }
}

module featheredge_wall(length, front_top, back_top) {
    max_top = max(front_top, back_top);
    board_count = ceil(max_top / featheredge_cover) + 1;

    intersection() {
        union() {
            for (i = [0 : board_count - 1]) {
                translate([0, 0, i * featheredge_cover])
                    featheredge_board(length);
            }

            featheredge_course_outlines(length, board_count);
        }

        hull() {
            cube([featheredge_thick, 0.01, front_top]);
            translate([0, length - 0.01, 0])
                cube([featheredge_thick, 0.01, back_top]);
        }
    }
}

module front_featheredge_panel(width, height) {
    rotate([0, 0, -90])
        featheredge_wall(width, height, height);
}

module hardboard_panel(width, height) {
    color(hardboard_colour)
        cube([width, hardboard_t, height]);
}

module back_wall_panel() {
    translate([0, total_depth, 0])
        hardboard_panel(total_width, back_height);
}

module left_wall_cladding() {
    mirror([1, 0, 0])
        featheredge_wall(total_depth, front_height, back_height);
}

module right_front_panel() {
    panel_width = total_width - post_face - front_centre_post_x + front_panel_post_overlap;
    panel_height = front_height - rail_h;

    translate([front_centre_post_x, 0, 0])
        front_featheredge_panel(panel_width, panel_height);
}

module cladding() {
    back_wall_panel();
    left_wall_cladding();
    right_front_panel();
}

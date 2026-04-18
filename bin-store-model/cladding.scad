// ─────────────────────────────────────────────────────────
// Bin Store Cladding
// Featheredge walls and hardboard front panel
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// Rectangular outline traced around a cuboid panel (e.g. hardboard back wall).
module panel_edges(dims) {
    if (show_edges) {
        x = dims[0]; y = dims[1]; z = dims[2];
        r = 0.8;
        color(edge_colour) {
            for (p = [[0,0,0], [0,y,0], [0,0,z], [0,y,z]])
                translate(p) rotate([0,90,0]) cylinder(h=x, r=r, $fn=6);
            for (p = [[0,0,0], [x,0,0], [0,0,z], [x,0,z]])
                translate(p) rotate([-90,0,0]) cylinder(h=y, r=r, $fn=6);
            for (p = [[0,0,0], [x,0,0], [0,y,0], [x,y,0]])
                translate(p) cylinder(h=z, r=r, $fn=6);
        }
    }
}

// Single featheredge board.
// Polygon cross-section (XY) is extruded along Z for `length`, then rotated
// -90° about X so the extrusion runs along +Y. Edges are drawn from the SAME
// polygon so the outline follows the board's actual geometry.
featheredge_poly = [
    [0, 0],                                   // V1 back-top
    [featheredge_thin, 0],                    // V2 front-thin (top)
    [featheredge_thick, featheredge_w],       // V3 front-thick (bottom)
    [0, featheredge_w]                        // V4 back-bottom
];

module featheredge_board(length, board_colour = cladding_colour) {
    rotate([-90, 0, 0]) {
        color(board_colour)
            linear_extrude(height = length)
                polygon(featheredge_poly);

        if (show_edges) {
            r = 0.8;
            color(edge_colour) {
                // Length-wise edges: one cylinder per polygon vertex, running along +Z
                // (which becomes +Y after the outer rotate).
                for (v = featheredge_poly)
                    translate([v[0], v[1], 0]) cylinder(h=length, r=r, $fn=12);

                // End-face edges: trapezoid outline at Z=0 and Z=length.
                for (z = [0, length])
                    for (i = [0 : len(featheredge_poly) - 1]) {
                        a = featheredge_poly[i];
                        b = featheredge_poly[(i + 1) % len(featheredge_poly)];
                        dx = b[0] - a[0];
                        dy = b[1] - a[1];
                        seg_len = sqrt(dx*dx + dy*dy);
                        seg_ang = atan2(dy, dx);
                        translate([a[0], a[1], z])
                            rotate([0, 0, seg_ang])
                            rotate([0, 90, 0])
                            cylinder(h=seg_len, r=r, $fn=12);
                    }
            }
        }
    }
}

// Stacked featheredge boards clipped to a trapezoidal panel envelope.
// Both the board geometry and its edge wireframe sit inside the SAME
// intersection, so edges are trimmed to the panel shape automatically.
module featheredge_wall(length, front_top, back_top) {
    max_top = max(front_top, back_top);
    board_count = ceil(max_top / featheredge_cover) + 1;

    intersection() {
        union() {
            for (i = [0 : board_count - 1]) {
                translate([0, 0, i * featheredge_cover])
                    featheredge_board(length,
                        (i % 2 == 0) ? cladding_colour : cladding_colour_alt);
            }
        }

        hull() {
            cube([featheredge_thick + 0.5, 0.01, front_top]);
            translate([0, length - 0.01, 0])
                cube([featheredge_thick + 0.5, 0.01, back_top]);
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
    translate([0, total_depth, 0]) {
        hardboard_panel(total_width, back_height);
        panel_edges([total_width, hardboard_t, back_height]);
    }
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

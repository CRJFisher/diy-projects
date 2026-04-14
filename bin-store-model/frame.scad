// ─────────────────────────────────────────────────────────
// Bin Store Frame
// Posts, rails, depth rails, and X-braces
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// ── Edge highlighting ──────────────────────────────────

module edges(dims) {
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

// ── Primitives ──────────────────────────────────────────

module post(height) {
    // 47mm (X) x 50mm (Y) x height (Z)
    color(timber_colour) cube([post_face, post_side, height]);
    edges([post_face, post_side, height]);
}

module rail(length) {
    // length (X) x 50mm (Y) x 47mm (Z)
    color(timber_colour) cube([length, rail_d, rail_h]);
    edges([length, rail_d, rail_h]);
}

module depth_rail(length) {
    // 50mm (X) x length (Y) x 47mm (Z)
    color(timber_colour) cube([rail_d, length, rail_h]);
    edges([rail_d, length, rail_h]);
}

module sloped_depth_rail(length) {
    // Depth rail that rises by roof_slope from front to back
    color(timber_colour)
    hull() {
        cube([rail_d, 0.01, rail_h]);
        translate([0, length - 0.01, roof_slope])
            cube([rail_d, 0.01, rail_h]);
    }
    // Edges for sloped rail (approximate with end-face edges)
    if (show_edges) {
        r = 0.8;
        color(edge_colour) {
            // Front face edges
            for (p = [[0,0,0], [rail_d,0,0], [0,0,rail_h], [rail_d,0,rail_h]])
                translate(p) cylinder(h=0.01, r=r, $fn=6);
            // Back face edges (raised)
            for (p = [[0,length,roof_slope], [rail_d,length,roof_slope],
                      [0,length,roof_slope+rail_h], [rail_d,length,roof_slope+rail_h]])
                translate(p) cylinder(h=0.01, r=r, $fn=6);
            // Long edges connecting front to back
            for (corner = [[0,0], [rail_d,0], [0,rail_h], [rail_d,rail_h]]) {
                dx = 0; dy = length; dz = roof_slope;
                el = sqrt(dy*dy + dz*dz);
                ax = atan2(dz, dy);
                translate([corner[0], 0, corner[1]])
                    rotate([-90+ax, 0, 0])
                    translate([0, 0, 0])
                    rotate([90,0,0])
                    rotate([-90,0,0])
                    cylinder(h=el, r=r, $fn=6);
            }
        }
    }
}

module x_brace(p1, p2) {
    dx = p2[0] - p1[0];
    dy = p2[1] - p1[1];
    dz = p2[2] - p1[2];
    length = sqrt(dx*dx + dy*dy + dz*dz);
    angle_z = atan2(dy, dx);
    angle_y = -atan2(dz, sqrt(dx*dx + dy*dy));

    color(brace_colour)
    translate(p1)
    rotate([0, angle_y, angle_z])
    cube([length, brace_t, brace_w]);
}

// ── Post positions ──────────────────────────────────────
//
// Top view (looking down):
//
//   Back:   BL ──────────────────── BR     Y = total_depth - post_side
//            |          BC          |      (BC is INSIDE frame, in front of back rails)
//            |           |          |
//   Front:  FL ──────── FC ─────── FR     Y = 0
//
//   FC is 47mm to the right of BC (sits on the right bottom rail)

// Back corner posts (Y = total_depth - post_side, flush with back)
module back_left_post()  { translate([0, total_depth - post_side, 0])                    post(back_height); }
module back_right_post() { translate([total_width - post_face, total_depth - post_side, 0]) post(back_height); }

// Back centre post: INSIDE the frame, against the inside face of the back rails.
// Full height (same as other back posts). To the LEFT of the centre depth rail.
module back_centre_post() {
    translate([back_centre_post_x, total_depth - post_side - post_side, 0])
        post(back_height);
}

// Front corner posts (Y = 0)
module front_left_post()  { translate([0, 0, 0])                              post(front_height); }
module front_right_post() { translate([total_width - post_face, 0, 0])        post(front_height); }

// Front centre post: sits ON the right bottom rail, 47mm right of back centre
module front_centre_post() {
    translate([front_centre_post_x, 0, rail_h])
        post(centre_post_height);
}

// ── Back Frame ──────────────────────────────────────────
// Back corner posts + centre post (inside) + 3 continuous horizontal rails + X-braces

module back_frame() {
    back_left_post();
    back_centre_post();
    back_right_post();

    // Rails span full width between inner faces of corner posts (continuous)
    rail_y = total_depth - post_side;

    // Top rail
    translate([post_face, rail_y, back_height - rail_h])
        rail(full_rail_length);

    // Bottom rail
    translate([post_face, rail_y, 0])
        rail(full_rail_length);

    // Mid rail
    translate([post_face, rail_y, mid_rail_height])
        rail(full_rail_length);

    // X-braces in back-left panel (left post to centre post X, above mid rail)
    brace_x_left  = post_face;
    brace_x_right = back_centre_post_x;
    brace_z_bot   = mid_rail_height + rail_h;
    brace_z_top   = back_height - rail_h;
    brace_y       = rail_y + rail_d/2 - brace_t/2;

    x_brace([brace_x_left, brace_y, brace_z_bot],
            [brace_x_right, brace_y, brace_z_top]);
    x_brace([brace_x_left, brace_y, brace_z_top],
            [brace_x_right, brace_y, brace_z_bot]);
}

// ── Front Frame ─────────────────────────────────────────
// 2 corner posts + centre post (on right bottom rail) + top rail + right bottom rail

module front_frame() {
    front_left_post();
    front_centre_post();
    front_right_post();

    // Top rail (full width between corner posts)
    translate([post_face, 0, front_height - rail_h])
        rail(full_rail_length);

    // Right bottom rail (under and to the right of front centre post)
    translate([front_centre_post_x, 0, 0])
        rail(right_front_bot_rail);
}

// ── Centre Divider ──────────────────────────────────────
// Top depth rail (sloped, full internal depth) + mid depth rail (horizontal)
// Both at X = front_centre_post_x, to the right of the back centre post

module centre_divider() {
    // Top depth rail -- sloped from front height to back height
    translate([front_centre_post_x, post_side, front_height - rail_h])
        sloped_depth_rail(depth_rail_length);

    // Bottom shelf depth rail (on floor)
    translate([front_centre_post_x, post_side, bottom_shelf_rail_z])
        depth_rail(depth_rail_length);

    // Lower shelf depth rail
    translate([front_centre_post_x, post_side, lower_shelf_rail_z])
        depth_rail(depth_rail_length);

    // Upper shelf depth rail
    translate([front_centre_post_x, post_side, upper_shelf_rail_z])
        depth_rail(depth_rail_length);
}

// ── Side/Depth Rails ────────────────────────────────────
// Corner depth rails (top ones sloped) + left wall mid-rail + left wall X-braces

module side_rails() {
    // Top-left depth rail (sloped)
    translate([0, post_side, front_height - rail_h])
        sloped_depth_rail(depth_rail_length);

    // Top-right depth rail (sloped)
    translate([total_width - rail_d, post_side, front_height - rail_h])
        sloped_depth_rail(depth_rail_length);

    // Bottom-left depth rail
    translate([0, post_side, 0])
        depth_rail(depth_rail_length);

    // Right bottom shelf depth rail (on floor)
    translate([total_width - rail_d, post_side, bottom_shelf_rail_z])
        depth_rail(depth_rail_length);

    // Right lower shelf depth rail
    translate([total_width - rail_d, post_side, lower_shelf_rail_z])
        depth_rail(depth_rail_length);

    // Right upper shelf depth rail
    translate([total_width - rail_d, post_side, upper_shelf_rail_z])
        depth_rail(depth_rail_length);

    // Left wall mid-rail at 775mm
    translate([0, post_side, mid_rail_height])
        depth_rail(depth_rail_length);

    // X-braces in left side panel (above mid rail)
    brace_y_front = post_side;
    brace_y_back  = post_side + depth_rail_length;
    brace_z_bot   = mid_rail_height + rail_h;
    brace_z_top   = front_height - rail_h;
    brace_x       = post_face/2 - brace_t/2;

    x_brace([brace_x, brace_y_front, brace_z_bot],
            [brace_x, brace_y_back, brace_z_top]);
    x_brace([brace_x, brace_y_front, brace_z_top],
            [brace_x, brace_y_back, brace_z_bot]);
}

// ── Complete Frame ──────────────────────────────────────

module frame() {
    back_frame();
    front_frame();
    centre_divider();
    side_rails();
}

// ─────────────────────────────────────────────────────────
// Courtyard Nook — Walls & site envelope
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// Interior back-wall Y at a given X (angled: deeper on the right)
function back_y(x) =
    nook_depth_left + (nook_depth_right - nook_depth_left) * (x / nook_width);

// Left wall of the nook (interior at X=0), thickness outward (−X)
module nook_left_wall() {
    color(wall_colour)
        translate([-wall_t, 0, 0])
            cube([wall_t, nook_depth_left, wall_height]);
}

// Right wall of the nook (interior at X=nook_width), thickness outward (+X)
module nook_right_wall() {
    color(wall_colour)
        translate([nook_width, 0, 0])
            cube([wall_t, nook_depth_right, wall_height]);
}

// Back (building) wall — follows the angled back line; thickness outward (+Y)
module nook_back_wall() {
    x0 = 0;
    x1 = nook_width;
    y0 = back_y(x0);
    y1 = back_y(x1);
    ye0 = y0 + wall_t;
    ye1 = y1 + wall_t;
    h = building_wall_height;

    // Face winding: outward-facing normals (CCW when viewed from outside)
    color(building_colour)
        polyhedron(
            points = [
                [x0, y0, 0], [x1, y1, 0], [x1, ye1, 0], [x0, ye0, 0],  // 0–3 bottom
                [x0, y0, h], [x1, y1, h], [x1, ye1, h], [x0, ye0, h]   // 4–7 top
            ],
            faces = [
                [0, 3, 2, 1],  // bottom
                [4, 5, 6, 7],  // top
                [0, 1, 5, 4],  // interior (toward nook, −Y-ish)
                [1, 2, 6, 5],  // right end
                [2, 3, 7, 6],  // exterior (+Y)
                [3, 0, 4, 7]   // left end
            ]
        );
}

// Floor ghost of the nook footprint (trapezoid in plan)
module nook_floor() {
    x0 = 0;
    x1 = nook_width;
    yb0 = back_y(x0);
    yb1 = back_y(x1);
    t = 2;

    color(floor_colour, 0.45)
        polyhedron(
            points = [
                [x0, 0, 0], [x1, 0, 0], [x1, yb1, 0], [x0, yb0, 0],
                [x0, 0, t], [x1, 0, t], [x1, yb1, t], [x0, yb0, t]
            ],
            faces = [
                [0, 3, 2, 1],
                [4, 5, 6, 7],
                [0, 1, 5, 4],
                [1, 2, 6, 5],
                [2, 3, 7, 6],
                [3, 0, 4, 7]
            ]
        );
}

// Bathroom extractor on the back wall, projecting into the nook
module bathroom_extractor() {
    y_face = back_y(extractor_x + extractor_w / 2);

    color(extractor_colour)
        translate([extractor_x, y_face - extractor_d, extractor_bottom_z])
            cube([extractor_w, extractor_d, extractor_h]);
}

// Courtyard stubs: walls the nook sits against, drawn ~1.5 m beyond the opening
//
// 1) Left courtyard wall continues past the opening in −Y (same line as nook left)
// 2) Far courtyard wall continues past the nook in +X (from the right front corner)
module courtyard_stubs() {
    color(wall_colour)
        translate([-wall_t, -courtyard_stub_len, 0])
            cube([wall_t, courtyard_stub_len, wall_height]);

    color(wall_colour)
        translate([nook_width, -wall_t, 0])
            cube([courtyard_stub_len, wall_t, wall_height]);
}

module nook_walls() {
    nook_left_wall();
    nook_right_wall();
    nook_back_wall();
}

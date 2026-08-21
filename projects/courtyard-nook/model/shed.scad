// ─────────────────────────────────────────────────────────
// Courtyard Nook — Shed geometry
// The thing we are building. Driven by `parameters.scad`.
// Nothing is designed yet; only the site-imposed roof limit is drawn.
// ─────────────────────────────────────────────────────────

include <parameters.scad>

// The steepest roof plane the site allows. It grazes two fixed obstructions
// at two different depths — the far bottom edge of the bathroom extractor
// near the opening, and the underside of the neighbour's gutter end at the
// back wall — which between them fix the pitch. Anything of ours that pokes
// up through this plane does not fit.
module roof_limit_plane() {
    color(clearance_colour, ghost_alpha)
        translate([0, 0, roof_limit_z_at_front])
            rotate([roof_max_pitch, 0, 0])
                cube([nook_width, nook_depth / cos(roof_max_pitch), ghost_t]);
}

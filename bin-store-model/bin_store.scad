// ─────────────────────────────────────────────────────────
// Bin Store -- Main Assembly
// Origin: outside-front-left-bottom corner
// X: width (left to right, 0 to 1300)
// Y: depth (front to back, 0 to 750)
// Z: height (bottom to top, 0 to 1647)
// ─────────────────────────────────────────────────────────

include <parameters.scad>
use <frame.scad>
use <roof.scad>
use <bins.scad>
use <shelves.scad>

if (show_frame)  frame();
if (show_roof)   roof();
if (show_shelves) shelves();
if (show_bins)   bins();

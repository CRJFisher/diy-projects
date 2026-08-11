// ─────────────────────────────────────────────────────────
// Courtyard Nook — Main Assembly
// Origin: front-left of nook opening (courtyard side), ground
// X: left → right
// Y: opening → into nook
// Z: up
// ─────────────────────────────────────────────────────────

include <parameters.scad>
use <walls.scad>

if (show_nook_walls)      nook_walls();
if (show_courtyard_stubs) courtyard_stubs();
if (show_extractor)       bathroom_extractor();
if (show_floor_ghost)     nook_floor();

# OpenSCAD Bin Store Model -- Work Plan

## Goal

Create a parametric 3D model of the bin store in OpenSCAD that:

- Validates fit of all bins (wheelie bin, food caddy, recycling boxes)
- Visualises the structure at each build stage
- Serves as a reference alongside the build guides

## Inventory Workflow

The OpenSCAD/code layer is also the source of truth for the generated project `cut_list`.

- `bin-store-model/parameters.scad` and the module structure under `bin-store-model/` feed the extraction layer
- the generated `cut_list` is mirrored into Grist as a generated operational table, with only the `completed` flag editable
- manual stock counts live in the Grist `inventory` table and are pulled back into repo snapshots
- shopping decisions and `shopping_list` population are handled by a separate AI agent workflow outside the scripts in this repo

See `docs/grist_inventory_workflow.md` for the operator workflow and the repo-backed snapshot files under `data/`.

## File Structure

All files in a `bin-store-model/` directory:

```
bin-store-model/
  bin_store.scad      # Main entry point -- assembles all components
  parameters.scad     # All dimensions, timber sizes, and display toggles
  frame.scad          # Posts, rails, X-bracing
  roof.scad           # Battens, plywood deck, felt
  cladding.scad       # Featheredge walls, hardboard panel
  door.scad           # Left section hinged door
  shelves.scad        # Right section shelves (battens + plywood)
  bins.scad           # Transparent ghost bins for fit-checking
```

## Coordinate Convention

- Origin: outside-front-left-bottom corner of the bin store
- X axis: width (left to right), 0 to 1300mm
- Y axis: depth (front to back), 0 to 750mm
- Z axis: height (bottom to top), 0 to 1647mm

## Parameters (`parameters.scad`)

All measurements centralised here. Modules never contain magic numbers.

### Timber cross-sections

- `post_face = 47; post_side = 50;` (face = X/left-right dimension, side = Y/front-back dimension)
- `rail_h = 47; rail_d = 50;`
- `brace_t = 15; brace_w = 38;`
- `batten_w = 50; batten_h = 22;`
- `ply_t = 18;`

### Overall envelope

- `total_width = 1300;`
- `total_depth = 750;`
- `front_height = 1597;`
- `back_height = 1647;`
- `roof_slope = 50;`

### Section geometry

- `left_section_clear = 780;` (door opening)
- `right_section_width = 440;` (recycling area, front centre post overlaps into this)
- `front_centre_post_x = 874;` (post_face + left_section_clear + post_face = 47 + 780 + 47; sits on top of front bottom right rail)
- `back_centre_post_x = 827;` (post_face + left_section_clear = 47 + 780; inside frame, one post_side in front of back wall)
- `mid_rail_height = 775;`
- `internal_depth = 650;`

### Derived values (computed in OpenSCAD)

- Full-width rail length: `total_width - 2 * post_face` = 1206mm
- Right front bottom rail: `total_width - post_face - front_centre_post_x` = 1300 - 47 - 874 = 379mm
- Front centre post height: `front_height - 2 * rail_h` = 1503mm (only applies to front centre post)
- Back centre post height: `back_height` = 1647mm (full height, same as back corner posts)
- Depth rails: `internal_depth` = 650mm

### Bin dimensions (for ghost models)

- Wheelie bin: 490 x 570 x 1060mm
- Food caddy: 323 x 400 x 400mm (confirm actual depth/height)
- Recycling box: 430 x 570 x 300mm

### Display toggles

- `show_frame`, `show_roof`, `show_cladding`, `show_door`, `show_shelves`, `show_bins` -- booleans to toggle subsystems
- `door_angle` -- 0 = closed, 90 = fully open (default: 15 for visual clarity)

## Module Breakdown

### Frame (`frame.scad`)

Primitives:

- `post(height)` -- single 50x47 vertical timber
- `rail(length)` -- horizontal timber along X axis
- `depth_rail(length)` -- horizontal timber along Y axis
- `x_brace(p1, p2)` -- diagonal brace between two 3D points, auto-computes length/angle

Assemblies:

- `back_frame()` -- 2 back corner posts (1647mm each), back centre post (1647mm, inside frame at X=827, one post_side in front of back wall), 3 continuous horizontal rails (top/mid/bottom at 1206mm), 2 X-braces in left upper zone
- `front_frame()` -- 2 corner posts (1597mm), top rail (1206mm), right bottom rail (379mm). No left bottom rail (wheelie bin access)
- `centre_divider()` -- front centre post (1503mm, at X=874, sits on top of front bottom right rail), top centre depth rail connecting from front top rail to back top rail (passes to the right of back centre post at X=874), mid depth rail
- `side_rails()` -- 4 corner depth rails (top-left, top-right, bottom-left, bottom-right), left wall mid-rail at 775mm
- `frame()` -- calls all of the above

### Roof (`roof.scad`)

- `roof_battens()` -- 4 battens (50x22mm) running left-to-right, spaced across the 750mm depth, following the slope
- `roof_deck()` -- 18mm plywood on top of battens, sized to match or slightly overhang
- `roof()` -- battens + deck (felt/shingles are visual-only, can add as thin layer)

### Cladding (`cladding.scad`)

- `featheredge_board(length)` -- single tapered board profile using `linear_extrude` on a trapezoidal polygon
- `featheredge_wall(width, height)` -- repeating boards with overlap, for back wall, left wall, and centre divider
- `hardboard_panel(width, height)` -- flat panel for right section front
- `cladding()` -- places all wall panels. Right side intentionally open.

### Door (`door.scad`)

- `door_panel(width, height)` -- featheredge boards within a timber frame (2 stiles + 2 rails)
- `door(angle)` -- positions panel with hinge edge at local x=0, applies `rotate([0, 0, angle])`
- `door_assembly()` -- translates door to hinge position at left post

### Shelves (`shelves.scad`)

- `shelf(z_height)` -- 2 battens (front-to-back) + plywood panel on top
- `shelves()` -- 3 shelves in right section, spaced for recycling box height + clearance

### Ghost Bins (`bins.scad`)

- `wheelie_bin()` -- translucent green, 490x570x1060mm
- `food_caddy()` -- translucent brown, 323x400x400mm
- `recycling_box()` -- translucent blue, 430x570x300mm
- `bins()` -- places all bins in their intended positions on shelves / floor

## Implementation Phases

### Phase 1: Frame + Ghost Bins

Build `parameters.scad`, `frame.scad`, `bins.scad`, and `bin_store.scad`.

This is the highest-value phase: it validates that all bins fit within the structure and matches the already-built Weekend 1 frame. Deliverables:

- All 6 posts in correct positions
- All rails (full-width, right bottom, depth, mid-height)
- X-braces in back-left and left panels
- Ghost bins positioned for fit-checking

### Phase 2: Roof

Build `roof.scad` -- battens, plywood deck. Matches Weekend 2 scope.

### Phase 3: Shelves

Build `shelves.scad`. Simplest phase -- battens and plywood rectangles. Matches Weekend 4 scope.

### Phase 4: Cladding + Door

Build `cladding.scad` and `door.scad`. The featheredge profile is the trickiest geometry (tapered cross-section). Matches Weekend 3 scope.

### Phase 5: Clash Detection

OpenSCAD has no built-in collision detection, but `intersection()` can be used to find overlapping volumes between components. If the intersection is non-empty, there's a clash.
This work will replace the `validate-measurements.py` script with a more robust clash detection system.

#### File: `clash_check.scad`

Toggles to check specific pairs:

- `check_bins_vs_frame` -- does each bin fit within the frame without overlapping timber?
- `check_bins_vs_bins` -- do any bins overlap each other?
- `check_posts_vs_rails` -- are there any unintended post/rail overlaps?

Each check renders only the `intersection()` of the two component groups in bright red. If the preview shows nothing, the pair is clear.

#### CLI automation

A helper script (`clash_check.sh`) can render each check to STL via the OpenSCAD CLI and report pass/fail based on whether the output is a degenerate (empty) mesh:

```
openscad -o /tmp/clash.stl -D 'check_bins_vs_frame=true' clash_check.scad
# Empty STL (header-only, ~684 bytes) = no clash = PASS
```

This allows clash checks to be run non-interactively as part of a validation workflow.

## Design Notes

- **Featheredge taper**: Model as `linear_extrude` of a trapezoidal 2D polygon (thick edge ~15mm, thin edge ~5mm). Each board overlaps the one below by ~25mm.
- **Door hinge rotation**: Place door with hinge edge at local origin, then `translate` to hinge position before `rotate`. This gives correct pivot behaviour.
- **Roof slope**: Back posts are 50mm taller than front. Slope angle = atan(50/650) = 4.4 degrees. Roof deck can use `hull()` of two rectangles at different Z heights, or a rotated flat panel.
- **No CSG where unnecessary**: The model is mostly placed cuboids. Avoid `difference()` / `union()` except for the featheredge taper. Keeps preview fast.
- **Colour coding**: Timber in wood-brown `[0.76, 0.60, 0.42]`, plywood lighter, cladding grey, bins in translucent colours with alpha ~0.2.

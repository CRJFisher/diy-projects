# Courtyard Nook

Roofing / enclosure for a courtyard nook.

## Site envelope (looking into the nook from the courtyard)

All notes were taken in cm; OpenSCAD uses mm (`×10`).
Source of truth: `model/site.scad`.

- **Left** — brick nook wall, 1950mm, continuing past the opening as a ~4m courtyard wall.
- **Back** — _not one flat wall_. Brick for the first **820mm** from the left corner
  at 1950mm, then the **neighbour's house wall** interrupts it and carries on to
  the right-hand wall, rising well above the brick.
- **Right** — our house wall (~3m), with the bathroom extractor 680mm in from the
  courtyard edge.

### The two constraints that fix the roof pitch

The roof has to duck under two fixed obstructions, and they sit at different
depths into the nook — so between them they determine the steepest roof plane
we can build, and therefore its pitch. `model/shed.scad` draws that plane as a
translucent red sheet.

| Obstruction                          | Depth into nook (Y) | Underside (Z) | Roof limit with 25mm clearance |
| ------------------------------------ | ------------------- | ------------- | ------------------------------ |
| Bathroom extractor, far edge         | 830mm               | 2000mm        | 1975mm                         |
| Neighbour's gutter, at the back wall | 2000mm              | 2285mm        | 2260mm                         |

Result: **13.7° falling toward the courtyard opening**, 1773mm at the opening
rising to 2260mm at the back wall. Build shallower and you give up headroom;
steeper and you hit something.

Two details that are easy to get wrong:

- The extractor's binding point is its **far** edge (830mm = 680 + its 150mm
  width), not its near edge, because the roof is still rising as it passes
  beneath it.
- The gutter's binding point is the **back wall** (2000mm), where our roof
  stops and is therefore at its highest under the overhanging end.

### About that gutter

It does **not** run across our back wall. It runs along the neighbour's eaves
_away from us_, into their property, and only its near **end** reaches back over
our nook — by a few cm past the back wall plane. That end is the only part of it
in our airspace, and it is what we duck under.

**Still to measure:** how far that end actually reaches in. "A few cm" was
eyeballed; `gutter_projection` is a placeholder 50mm. Its X position, the
neighbour's roof pitch/run, and the masonry thicknesses are schematic too.

Left of the 820mm mark the brick tops out at 1950mm and **what sits above it has
not been measured** — do not assume that headroom is free.

## Layout

Parameters are split by _who owns the number_:

- `model/site.scad` — **site constraints.** What is already there and cannot be
  changed: nook envelope, wall heights, the back-wall split, the gutter, the
  extractor. Measured on site.
- `model/parameters.scad` — **shed build dimensions.** What we are building.
  Includes `site.scad` so the build derives from the site. This is the input to
  the cut-list script, so every number a cut depends on must live here.
- `model/walls.scad` — site geometry (driven by `site.scad` only)
- `model/shed.scad` — shed geometry (driven by `parameters.scad`); currently
  just the roof limit plane
- `model/courtyard_nook.scad` — assembly
- `extraction.py` — parses `parameters.scad` and everything it includes, then
  maps parameters → cut rows
- `data/` — `cut_list.json`, `shopping_list.json`, `substitution_candidates.json`

Shared workshop inventory: `../../shared/inventory/inventory.json`.

## TODO — there is no cut list yet

`build_cut_list_rows` returns nothing because **the shed itself is not designed**.
`extraction.py` parses parameters correctly and the pipeline runs end to end, so
the only missing piece is the design. Before `diy-shopping` can do anything useful:

1. Design the build and put every dimension in `model/parameters.scad` — see the
   TODO block there: frame (post/rail sections and positions), roof (pitch, fall
   direction, rafter section and spacing, deck), cladding, floor, openings.
2. Draw it in `model/shed.scad`, checking nothing pokes up through the roof
   limit plane.
3. Emit a row per cut in `build_cut_list_rows` — copy the `add_row` shape from
   `projects/bin-store/extraction.py`.
4. Re-run the three commands below.

```bash
python3 scripts/extract_cut_list.py --project courtyard-nook
python3 scripts/sync_grist_tables.py --project courtyard-nook
python3 scripts/compute_shopping_list.py --project courtyard-nook
```

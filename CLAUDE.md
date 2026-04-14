# Bin Store

## Basic design (from face on)

- Left section contains wheelie bin and food caddy. This has a door opening outwards to the front.
- Right section contains recycling boxes on three shelves. This has a hard board on the front and is left open for access on the right side of the bin store.

## Key Constraints

These are the key constraints that need to be met in order to design a successful bin store. Everything else flows from these and the design.

- *Total* width must be 1300mm in order to fit in the space. This is possible based on the line (going left to right at the front face):
  - 47mm (left post width)
  - 490mm (wheelie bin width)
  - 323mm (food caddy width)
  - 440mm (recycling bin width plus 10mm clearance)
  - Total: 440 + 323 + 490 + 47 = 1300mm
  - Note: the front and back centre posts are at different X positions. The front centre post (at X=874mm) sits on top of the front bottom right rail and overlaps 47mm into the recycling bin space in the width dimension; this is intentional and acceptable as the depth clearance ensures the recycling boxes fit without obstruction. The back centre post (at X=827mm) is inside the frame, one post_side (50mm) in front of the back wall, and does not reduce the recycling section width.
- *Internal* height must allow for the wheelie bin lid to be open, requiring a clearance of 1550mm
  - 1060mm (wheelie bin height)
  - 490mm (clearance above the wheelie bin lid)
  - Total: 1060 + 490 = 1550mm
- Depth should be depth of wheelie bin and recycling boxes - 750mm. This consists of:
  - 50mm (post width)
  - 40mm (clearance)
  - 570mm (recycling box depth)
  - 40mm (clearance)
  - 50mm (post width)
  - Total: 50 + 40 + 570 + 40 + 50 = 750mm

## OpenSCAD

We're using OpenSCAD to design the bin store. It is installed locally.

There's a cheat sheet for OpenSCAD here: [OpenSCAD CheatSheet.htm](OpenSCAD CheatSheet.htm)

**Tip:** After opening a `.scad` file, press **F5** to preview, then use **View > View All** (or the toolbar button) to zoom the camera to fit the entire model. Without this, the viewport may appear blank.
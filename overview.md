# Bin Store -- Overview

## What It Is

A two-section outdoor bin store in pressure-treated softwood.

- **Left section** (~860mm wide): wheelie bin + food caddy, enclosed with a front-opening door
- **Right section** (~440mm wide): three recycling boxes on shelves, open on the right side, hardboard front panel

## Key Dimensions

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| Total width | 1300mm | 47mm post + 490mm wheelie bin + 323mm food caddy + 440mm recycling box |
| Total depth | 750mm | 50mm post + 40mm clearance + 570mm recycling box + 40mm clearance + 50mm post |
| Front height | 1597mm | Standard for internal clearance |
| Back height | 1647mm | Front + 50mm roof slope |
| Internal clearance | 1550mm min | 1060mm wheelie bin + 490mm lid clearance |

Full constraint derivations are in [CLAUDE.md](CLAUDE.md).

## Design Decisions

1. **No bottom rail at the door opening** -- so the wheelie bin rolls in without lifting over a lip
2. **50mm roof slope** (back to front) -- no angled cuts needed; square-cut depth rails seat cleanly at ~3.8 degrees
3. **X-braces from user-supplied 15x38mm timber** -- keeps B&Q stock for posts/rails; 15mm braces overlap to only 30mm at crossing (less than 47mm frame depth)
4. **No right wall mid-rail** -- shelves provide lateral bracing for the right section
5. **Front centre post is 1503mm** (not full height) -- sits between top and bottom rails, keeping the front face flush for cladding and door frame. The **back centre post is full height (1647mm)** and is positioned inside the frame, one post_side (50mm) in front of the back corner posts, rather than flush with the back wall. The back left-to-right rails run continuously across the full width without breaking at the back centre post.
6. **Roof construction** (bottom to top): battens (50x22mm, left-to-right) -> 18mm plywood -> felt -> shingles. Battens follow the slope naturally since front posts are shorter than back.

## Workflow

| Weekend | Scope | Status |
|---------|-------|--------|
| 1 | Frame -- 6 posts, all rails, X-bracing, centre divider | Done |
| 2 | Roof -- battens, plywood sheathing, felt, shingles | Upcoming |
| 3 | Cladding (featheredge) + door (frame, hinges, latch) | Planned |
| 4 | Shelves (plywood on battens) + paint | Planned |

## Materials (B&Q)

| Material | Stock length | Total needed |
|----------|-------------|-------------|
| 50x47mm softwood | 2.4m | 8 sticks (posts + door stiles, offcuts = depth rails) |
| 50x47mm softwood | 1.8m | 5 sticks (full-width rails + door rail) |
| 50x22mm battens | 1.8m | 7 sticks (4 roof + 3 shelf) |
| 18mm exterior plywood | 2440x1220mm | 1 sheet (roof + shelves) |
| Featheredge 1.8m (10-pack) | 1.8m | 3 packs (back + left + divider) |
| Featheredge 3m | 3m | 8 pieces (door panel + right front) |

**User-supplied:** 15x38x2400mm timber (2 of 8 sticks for X-braces).

## Repo Structure

- `overview.md` -- this file
- `CLAUDE.md` -- key constraints for AI-assisted design
- `validate-measurements.py` -- validates all dimensions against constraints
- `week-1/` -- Weekend 1 build guide, shopping list, and helper script
- `diagrams/` -- SVG/PNG diagrams referenced by the build guides

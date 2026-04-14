# Bin Store — Weekend 1: Build the Frame

This weekend you build the freestanding timber frame -- six posts, all rails, cross-bracing, and a centre divider. No cladding, roof, or door yet.

| Measurement | Value |
|---|---|
| Total width | 1300 mm |
| Total depth | 750 mm |
| Internal depth | 650 mm (food caddy clearance) |
| Front height | 1597 mm |
| Back height | 1647 mm |
| Roof slope (back-to-front) | 50 mm fall |
| Left section width | ~860 mm (enclosed, with door) |
| Right section width | ~440 mm (open, with shelves) |

---

## Cut List

All frame cuts use **50 x 47 mm pressure-treated softwood** (from B&Q). Posts from 2.4 m stock; rails from 1.8 m stock. X-braces use **15 x 38 mm timber** (user-supplied, 2400 mm lengths).

| Qty | Length | Description |
|-----|--------|-------------|
| 3 | 1647 mm `[CUT:POST_BL,POST_BR,POST_BC]` | Back posts (2 corners + 1 right-section back) |
| 2 | 1597 mm `[CUT:POST_FL,POST_FR]` | Front corner posts (left + right) |
| 1 | 1503 mm `[CUT:POST_FC]` | Front centre post (sits between top & bottom rails; 1597 - 2 x 47) |
| 4 | 1206 mm `[CUT:RAIL_BACK_TOP,RAIL_BACK_BOT,RAIL_BACK_MID,RAIL_FRONT_TOP]` | Full-width rails (2 top, 1 back bottom, 1 back mid-rail at 775 mm; 1300 minus 2 x 47 mm posts) |
| 1 | 393 mm `[CUT:RAIL_FRONT_BOT_R]` | Front bottom rail -- right section only (centre post outside face to right corner post inside face; 440 section minus 47 right post) |
| 5 | 650 mm `[CUT:RAIL_DEPTH_TL,RAIL_DEPTH_TR,RAIL_DEPTH_BL,RAIL_DEPTH_BR,RAIL_DEPTH_TC]` | Depth rails (4 corner connections + 1 centre divider top) |
| 2 | 650 mm `[CUT:RAIL_MID_LEFT,RAIL_DEPTH_MC]` | Mid-rails (left wall + centre divider, at 775 mm) |
| 2 | ~1100 mm `[CUT:BRACE_BACK_1,BRACE_BACK_2]` | Back panel X-braces -- **15x38mm user-supplied** (45° both ends) |
| 2 | ~1000 mm `[CUT:BRACE_LEFT_1,BRACE_LEFT_2]` | Left panel X-braces -- **15x38mm user-supplied** (45° both ends; ~980 + ~1010, avg ~1000) |

**Fixings:** ~40x 75 mm galv screws (joints), ~16x 65 mm (braces). Roughly 56 total.

> **Noggins (optional):** can be added in Weekend 3 if cladding needs extra mid-span support.

![Cut List Diagram](diagrams/cut-list.png)

---

## Step 1: Build the Back Frame

Build this frame flat on sawhorses (or a flat floor), then stand it up later. Refer to the **Cut List** above for all part sizes.

![Back Frame Face-On View](diagrams/back-frame.png)

### Assembly

1. Lay all three 1647 mm `[CUT:POST_BL,POST_BR,POST_BC]` back posts flat, 50 mm face up: left corner post, centre-back post (860 mm from left), right corner post (1300 mm from left). The left-to-centre gap is ~860 mm; centre-to-right is ~440 mm
2. Butt a 1206 mm `[CUT:RAIL_BACK_TOP]` rail between the outer post tops, flush with the top ends. The rail passes over the centre-back post and is face-screwed to it -- the centre post is full height (1647 mm) and sits behind the rails, so the rails rest on its face. Pre-drill two pilot holes per joint, drive 2x 75 mm screws per side (6 screws total for this rail)
3. Repeat at the bottom. Check 90 deg with a framing square before driving screws -- tap the rail sideways to correct any racking
4. Mark all three posts at 775 mm up from the bottom rail. Fix the mid-height rail at this mark, spanning all three posts, same method (2x pilot holes, 2x 75 mm screws per side)

> **Centre-back post joint method:** The centre-back post runs the full 1647 mm height. All three horizontal rails are continuous 1206 mm pieces that pass in front of (over) the centre post and are face-screwed through the rail into the post. This is stronger than cutting the rails into sections because continuous rails act as beams, and face-screwing into the post (rather than end-grain screwing) gives a solid joint.

> **Tip:** A flat surface matters more than a raised one -- the frame must lie flat so it does not twist during assembly.

### Cross-Bracing (Upper Zone Only)

X-braces go in the **left section only** (between the left corner post and centre-back post), in the upper zone between the top rail and mid-height rail. They are surface-mounted on the **inside face** (facing the bins) -- no notches needed. This keeps the outside face flush for cladding. The right section (~440 mm) is too narrow for X-braces and will get shelves for rigidity instead.

5. Hold timber diagonally across the left section's upper rectangle (left post to centre-back post, top rail to mid-rail), corner to corner. Mark where it meets the inner edges and cut 45 deg at each end so it sits flush into the corner. Fix with 2x 65 mm screws at each end (pre-drill)

> **Visualising the 45 deg cut:** mitre the brace end so it tucks into the corner like a picture frame, touching both post and rail.

6. Cut and fix the second brace from the opposite corners of the same left-section rectangle, crossing over the first. Drive 1x 65 mm screw through both braces at the crossing point, plus 2x 65 mm screws at each end

> **Brace overlap note:** The 15 mm thick braces stack to only 30 mm at the crossing point (15 + 15 = 30 mm). This is less than the 47 mm depth of a single frame member, so the braces do not protrude beyond the frame face -- no packing or notching needed.

### Check for Square

7. Measure diagonals of the full frame (corner to corner) -- they should match within 2-3 mm. Also check diagonals of each section individually (left section: left post to centre-back post; right section: centre-back post to right post). If any pair differs, push the longer diagonal's corners inward (a clamp helps), then add one more screw per corner to lock the corrected position

> **Tip:** If the back frame is out of square, every frame you attach to it will fight to compensate.

Lean the completed frame against a wall, brace side outward.

## Step 2: Build the Front Frame

The front frame is 1597 mm tall (50 mm shorter than the back to create roof slope). Unlike the back frame, the front has a **door opening** on the left (~860 mm wide) for the wheelie bin and food caddy, so it gets **no X-braces, no full-width mid-height rail, and no bottom rail across the door opening**. The centre divider post (Step 4) will define the right edge of the door opening. Refer to the **Cut List** for parts.

> **Why no left-section bottom rail?** A full-width bottom rail would block the wheelie bin from rolling in and out -- you would have to lift the bin over a 47 mm timber lip every time. Removing the bottom rail from the door opening is standard practice in shed and garage construction. The left-front corner post is still braced at its base by the left-side depth rail (Step 3), and the door (Weekend 3) adds further rigidity when closed.

### Key Differences from the Back Frame

- **Posts are 1597 mm** (not 1647 mm) -- this creates the roof slope
- **No X-braces** -- the left section is a door opening and the right section is too narrow for meaningful bracing
- **No full-width mid-height rail** -- the left wall and right-section front get mid-rails (Step 5) but the right side wall does not (shelves will provide lateral bracing)
- **Front bottom rail is right section only (393 mm)** -- no bottom rail across the door opening so the wheelie bin can roll in and out freely
- Top rail remains **1206 mm** (full width between posts)

### Assembly

Build it flat on sawhorses:

1. Lay the two 1597 mm `[CUT:POST_FL,POST_FR]` posts parallel, 1300 mm apart (outside edge to outside edge)
2. Attach the top rail (1206 mm `[CUT:RAIL_FRONT_TOP]`) with 2x 75 mm screws per end (pilot holes first). **Do not fit a full-width bottom rail** -- the front bottom rail is fitted later in Step 4 as a short piece in the right section only
3. Check for square -- clamp a temporary diagonal brace across the frame to hold it square until the bottom rail and centre post are fitted in Step 4

> **Note:** The left section (~860 mm) will become the door opening -- keep it clear of bracing, mid-rails, and bottom rails. The right section (~440 mm) gets its bottom rail when the centre post is installed (Step 4). The centre post (Step 4) completes the front face.

![Front Face -- Complete View](diagrams/front-frame.png)

> **Check before moving on:** Stand both frames side by side. The back frame should be 50 mm taller and wider dimensions should match. The front frame will look more open -- that is correct (the centre post and door opening come later).

## Step 3: Connect Front & Back with Depth Rails

This is where your 2D frames become a 3D box. **You need a helper.** Refer to the **Cut List** for parts (4x 650 mm depth rails). Each rail gets 2x 75 mm screws per end (16 screws total). Pre-drill all holes.

### Assembly

1. Stand the back frame upright, propped or clamped. Position the front frame 750 mm in front (outside-to-outside), facing it -- the 650 mm depth rails bridge the 650 mm gap between inner post faces
2. Attach the top-left depth rail from left-back post (1647 mm) to left-front post (1597 mm) -- this slope creates the roof pitch. Butt the rail end-grain into the inner face of each post with the rail's **top edge flush with the post top** at each end (1647 mm at the back, 1597 mm at the front). No angled cuts are needed on posts or rails -- the ~3.8 degree slope is slight enough that the square-cut rail end seats cleanly against the post face. 2x 75 mm screws per end
3. Attach the bottom-left depth rail at ground level, flush with both posts (level). 2x 75 mm screws per end
4. Repeat on the right side -- top rail (sloped) and bottom rail (level)
5. Check square: measure diagonals of each side face and the top rectangle -- they should be equal. Tap corners with a mallet to adjust before fully tightening

![Box Frame Isometric View](diagrams/box-frame-isometric.png)

![Side View Showing Roof Slope](diagrams/side-view-slope.png)

> **Squareness check:** If diagonals differ, loosen one depth rail's screws, tap into alignment, re-measure, then tighten.

---

## Step 4: Install the Centre Divider

The centre divider splits the bin store into **left** (~860 mm, enclosed with door) and **right** (~440 mm, open shelves). See Cut List for timber sizes.

1. **Fit the right-section front bottom rail.** Cut the 393 mm `[CUT:RAIL_FRONT_BOT_R]` bottom rail (440 mm section width minus 47 mm right post = 393 mm, centre post outside face to right post inside face). Butt it against the inner face of the right corner post with its bottom edge flush with the post base. Fix with 2x 75 mm screws into the right corner post (pilot holes first). Leave the left end loose for now -- the centre post will sit on it next.
2. **Mark the divider position.** Measure 860 mm from the left-front post along the front top rail and mark it. This is also where the left end of the right-section bottom rail should sit.
3. **Stand the centre post.** Place the 1503 mm `[CUT:POST_FC]` post vertically at your mark, standing on top of the right-section bottom rail, 50 mm face parallel to the front edge. The post sits between the top rail and the bottom rail -- its bottom end rests on the top face of the bottom rail and its top end butts against the underside of the top rail.
4. **Fix the base.** Toe-screw 2x 75 mm screws through the post base into the bottom rail, one from each side. Pre-drill.
5. **Fix the top.** Drive 2x 75 mm screws down through the top rail into the end grain of the centre post. Pre-drill with a 5 mm bit to prevent splitting. This joint is compression-loaded (the roof pushes down), so end-grain screwing is adequate here.
6. **Fit the top depth rail.** 650 mm `[CUT:RAIL_DEPTH_TC]` rail from centre post top back to the back top rail (slopes slightly: 1597 mm front to 1647 mm back). 2x 75 mm screws at each end.
7. **Fit the mid-height depth rail.** 650 mm `[CUT:RAIL_DEPTH_MC]` rail from centre post to back frame at 775 mm height. 2x 75 mm screws at each end.
8. **Remove the temporary diagonal brace** from the front frame (if fitted in Step 2).
9. **Check plumb.** Spirit level on both faces of the centre post -- adjust until vertical before fully tightening.

> **Front centre post joint method:** Unlike the back frame (where the centre post is full height and rails pass over it), the front centre post is 1503 mm -- exactly 94 mm shorter than the corner posts (2 x 47 mm rail thickness). It sits between the top rail and the right-section bottom rail. This keeps the front face flush for cladding and the door frame.

> **No bottom rail at the door opening:** The left section (~860 mm) has no front bottom rail so the wheelie bin can roll straight in and out. The left-front corner post is braced at its base by the left-side bottom depth rail (fitted in Step 3), which is structurally sufficient.

### Plan View -- Frame After Step 4

![Plan View Top-Down After Step 4](diagrams/plan-view.png)

---

## Step 5: Add Remaining Mid-Height Rails

Mid-height rails at 775 mm stiffen the frame and provide cladding fixing points. Two are already in place from earlier steps (back wall and centre divider). One more to add now:

| Qty | Component | Length | Location |
|-----|-----------|--------|----------|
| 1 | Left wall mid-rail | 650 mm | Left-front to left-back post, 775 mm height |

Fix each rail with 2x 75 mm screws at each end. The right side wall does **not** get a mid-rail -- the shelves (Weekend 4) will act as lateral bracing instead. The right section of the front face (~440 mm wide) has no mid-rail either -- the cladding is nailed directly to the centre post and right corner post, which is sufficient for such a narrow span. Check all mid-rails are level with a spirit level before fully tightening.

### Front View -- Mid-Height Rails Highlighted

![Front View with Mid-Height Rails Highlighted](diagrams/mid-height-rails.png)

### Mid-height rail checklist

- [ ] **Back wall mid-rail** -- 1206 mm, across the full back, at 775 mm
- [ ] **Centre divider mid-rail** -- 650 mm, centre post to back frame, at 775 mm
- [ ] **Left wall mid-rail** -- 650 mm, left-front post to left-back post, at 775 mm

---

## Step 6: Final Quality Checks

Budget 20-30 minutes. Catching problems now saves painful disassembly later.

### 6.1 Squareness

Check diagonals of each face (back, front, left side, right side, and top). Both diagonals should match within 3 mm. If not, loosen corner screws half a turn, push the long-diagonal corner inward, re-measure, and re-tighten.

### 6.2 Plumb

Check all six posts with a spirit level in both directions (side-to-side and front-to-back). If a post is out, correct the base position first.

### 6.3 Level

Top rails should be level side-to-side (the front-to-back slope is intentional). Bottom rails should be level in all directions -- shim with offcuts on uneven ground.

### 6.4 Joint Tightness

Check every screw head is flush and wiggle-test each joint for play. If a joint moves, add one extra screw offset 25 mm from the original.

### 6.5 Cross-Brace Check

Push the top-front rail firmly sideways in both directions. The frame should feel rigid with no visible movement. If it racks, tighten brace screws.

### 6.6 Weather Protection

If rain is expected before Weekend 2, drape a tarp over the top (secured with clamps or rope) and lift the frame off the ground on packers if possible. End grain absorbs water fastest -- cap post tops with spare offcuts.

---

## Complete Frame -- What You've Built

![Complete Frame 3/4 View](diagrams/complete-frame.png)

---

## Weekend 1 Materials Summary

### Timber (B&Q)

See the Cut List above for all timber pieces and dimensions. Posts and rails are cut from 50x47mm stock (B&Q).

### Timber (user-supplied)

| Material | Qty | Length | Use |
|----------|-----|--------|-----|
| 15x38mm timber | 2 of 8 available | 2400 mm | X-braces (2x ~1100mm back + 2x ~1000mm left) |

The remaining 6 pieces of 15x38mm are spare.

### Fixings

| Fixing | Size | Qty |
|--------|------|-----|
| Galvanised screws | 75 mm | ~40 |
| Galvanised screws | 65 mm | ~16 |

### Tools

| Tool | Essential? |
|------|-----------|
| Cordless drill/driver (18V+) | Yes |
| Pilot drill bits (3 mm, 5 mm) | Yes |
| Tape measure (5 m) | Yes |
| Spirit level (600 mm+) | Yes |
| Framing square | Yes |
| Handsaw or mitre saw | Yes |
| Clamps (x2-4) | Yes |
| Sawhorses or workbench | Yes |
| Pencil | Yes |
| Safety glasses | Yes |
| Work gloves | Yes |

### NOT Needed This Weekend

- Cladding boards (featheredge) -- Weekend 3
- Roofing materials (felt, shingles) -- Weekend 2
- Plywood (roof deck, shelf panels) -- Weekend 2/4
- Hinges and door hardware -- Weekend 3
- Paint or wood stain -- Weekend 4
- Roof battens (50 x 22 mm) -- Weekend 2

# Bin Store Cutting Plan

Generated 2026-04-11. Based on validated dimensions from `validate-measurements.py`.

**Design change applied:** Right side wall does NOT get a mid-height rail (shelves act as rails).

---

## Summary of All 50x47mm Cuts (All 4 Weekends)

### Weekend 1 -- Frame (50x47mm from B&Q)

| Qty | Length (mm) | Description |
|-----|-------------|-------------|
| 3   | 1647        | Back posts (BL, BR, BC) |
| 2   | 1597        | Front corner posts (FL, FR) |
| 1   | 1503        | Front centre post (FC) |
| 4   | 1300        | Full-width rails (back top, back bottom, back mid, front top) |
| 7   | 750         | Depth rails (TL, TR, BL, BR, TC) + left wall mid-rail + centre divider mid-rail |
| 1   | 423         | Front bottom rail (right section; 470 section minus 47 centre post depth) |

### Weekend 1 -- X-Braces (15x38mm user-supplied, NOT from B&Q)

| Qty | Length (mm) | Description |
|-----|-------------|-------------|
| 2   | ~1100       | Back panel X-braces (45-deg ends) |
| 2   | ~1000       | Left panel X-braces (45-deg ends) |

> At the crossing point, 15+15 = 30mm total overlap -- less than a single 47mm frame member, so braces do not protrude beyond the frame depth.

### Weekend 3 -- Door Frame (50x47mm from B&Q)

| Qty | Length (mm) | Description |
|-----|-------------|-------------|
| 2   | 1500        | Door frame vertical stiles |
| 2   | 500         | Door frame horizontal rails |

### Weekend 1 Total 50x47mm: 18 pieces
### Weekend 1 Total 15x38mm (user-supplied): 4 pieces
### Weekend 3 Total 50x47mm: 4 pieces
### **Grand Total 50x47mm cuts: 22 pieces**
### **Grand Total 15x38mm cuts: 4 pieces**

---

## 50x22mm Cuts (Weekends 2 and 4)

| Weekend | Qty | Length (mm) | Description |
|---------|-----|-------------|-------------|
| 2       | 4   | 1300        | Roof battens (span full width) |
| 4       | 6   | 750         | Shelf battens (2 per level x 3 levels) |

---

## Cutting Plan: 50x47mm from 2.4m (2400mm) Sticks

Saw kerf assumed: 3mm per cut.

> **Design change:** X-braces are now cut from user-supplied 15x38mm timber, not from B&Q 50x47mm stock. This frees up 2 of the original 10 sticks.

| Stick # | Cut 1 | Cut 2 | Waste/Offcut | Notes |
|---------|-------|-------|--------------|-------|
| 1 | 1647mm (POST_BL) | 750mm (depth rail) | 0mm | 1647 + 3 + 750 = 2400. Perfect fit. |
| 2 | 1647mm (POST_BR) | 750mm (depth rail) | 0mm | Perfect fit. |
| 3 | 1647mm (POST_BC) | 750mm (depth rail) | 0mm | Perfect fit. |
| 4 | 1597mm (POST_FL) | 750mm (depth rail) | 50mm | 1597 + 3 + 750 = 2350. 50mm offcut. |
| 5 | 1597mm (POST_FR) | 750mm (depth rail) | 50mm | Same as above. |
| 6 | 1503mm (POST_FC) | 750mm (depth rail) | 144mm | 1503 + 3 + 750 = 2256. 144mm offcut. |
| 7 | 1500mm (door stile 1) | 750mm (depth rail) | 147mm | 1500 + 3 + 750 = 2253. 147mm offcut. |
| 8 | 1500mm (door stile 2) | 500mm (door rail 1) | 397mm | 1500 + 3 + 500 = 2003. 397mm offcut. |

**Sticks 1-8: Only 8 of the 10 available 2.4m sticks used.** This accounts for:
- 6 posts (3x 1647, 2x 1597, 1x 1503)
- 7x 750mm depth/mid rails (from sticks 1-7)
- 2x door stiles (1500mm)
- 1x door rail (500mm)

**2 spare 2.4m sticks remain** (sticks 9-10, previously used for braces + 1300mm rails).

**Remaining 50x47mm cuts that need 1.8m sticks:**
- 4x 1300mm rails (back top, back bottom, back mid, front top)
- 1x 500mm door rail
- 1x 423mm right-section bottom rail

---

## Cutting Plan: 50x47mm from 1.8m (1800mm) Sticks

> **Design change:** All 4x 1300mm rails now come from 1.8m sticks (previously 2 came from 2.4m sticks paired with braces). Back braces no longer use 50x47mm stock.

| Stick # | Cut 1 | Cut 2 | Cut 3 | Waste/Offcut | Notes |
|---------|-------|-------|-------|--------------|-------|
| 1 | 1300mm (rail) | 423mm (front bot R) | -- | 74mm | 1300 + 3 + 423 = 1726. 74mm offcut. |
| 2 | 1300mm (rail) | -- | -- | 497mm | 497mm offcut. |
| 3 | 1300mm (rail) | -- | -- | 497mm | 497mm offcut. |
| 4 | 1300mm (rail) | -- | -- | 497mm | 497mm offcut. |
| 5 | 500mm (door rail 2) | -- | -- | 1300mm | 1300mm offcut (spare). |

**Sticks 1-5: 5 of the 8 available 1.8m sticks used. 3 spare sticks remain.**

---

## Cutting Plan: 50x22mm from 1.8m (1800mm) Sticks

| Stick # | Cut 1 | Cut 2 | Waste/Offcut | Notes |
|---------|-------|-------|--------------|-------|
| 1 | 1300mm (roof batten) | -- | 500mm | |
| 2 | 1300mm (roof batten) | -- | 500mm | |
| 3 | 1300mm (roof batten) | -- | 500mm | |
| 4 | 1300mm (roof batten) | -- | 500mm | |

**All 4 sticks used for roof battens.**

### Weekend 4 shelf battens (6x 750mm, 50x22mm):
- 500mm offcuts from roof battens are too short for 750mm shelf battens.
- **SHORTAGE: Need 3 more 50x22mm 1.8m sticks** (each yields 2x 750mm with 297mm waste).
- Alternative: Buy 2 extra sticks and cut 2x 750mm from each (4 battens), plus 2x 750mm from a 3rd stick. Total: 3 extra sticks needed.

Actually -- let me optimise. From 1.8m: 750 + 3 + 750 = 1503mm, leaving 297mm. So 3 sticks yield 6x 750mm. **Need 3 extra 50x22mm sticks.**

---

## Cutting Plan: 15x38mm from 2.4m (2400mm) User-Supplied Sticks

**Material:** 8x 15x38x2400mm timber (user's own stock, not from B&Q).

These are used exclusively for X-braces. The thin 15mm section means both braces can overlap at the crossing point with only 30mm total stack-up (less than a single 47mm frame member).

| Stick # | Cut 1 | Cut 2 | Waste/Offcut | Notes |
|---------|-------|-------|--------------|-------|
| A | ~1100mm (BRACE_BACK_1) | ~1100mm (BRACE_BACK_2) | ~197mm | 1100 + 3 + 1100 = 2203. 197mm offcut. |
| B | ~1000mm (BRACE_LEFT_1) | ~1000mm (BRACE_LEFT_2) | ~397mm | 1000 + 3 + 1000 = 2003. 397mm offcut. |

**Only 2 of 8 sticks needed. 6 spare sticks remain.**

---

## Stock Comparison: Needed vs Available

### 50x47mm, 2.4m sticks

| | Count |
|---|---|
| **Available (B&Q list)** | **10** |
| **Needed** | **8** |
| **Surplus** | **2 sticks spare** |

> With braces moved to user-supplied 15x38mm stock, 2 sticks are freed up. These provide margin for miscuts.

### 50x47mm, 1.8m sticks

| | Count |
|---|---|
| **Available (B&Q list)** | **8** |
| **Needed** | **5** |
| **Surplus** | **3 sticks spare** |

> With noggins removed, only 5 sticks needed (4x 1300mm rails + 1x 500mm door rail). 3 spare sticks provide ample margin for miscuts.

### 15x38mm, 2.4m sticks (user-supplied)

| | Count |
|---|---|
| **Available (user stock)** | **8** |
| **Needed** | **2** |
| **Surplus** | **6 sticks spare** |

### 50x22mm, 1.8m sticks

| | Count |
|---|---|
| **Available (B&Q list)** | **4** |
| **Needed (roof battens)** | **4** |
| **Needed (shelf battens)** | **3** |
| **Total needed** | **7** |
| **SHORTAGE** | **3 sticks short** |

---

## Non-Timber Items Check

| Item | Qty in List | Sufficient? | Notes |
|------|-------------|-------------|-------|
| **Bitumen Shingles** (20 pcs, 3.2 m2) | 1 pack | YES | Roof area ~1.3m x 0.85m = ~1.1 m2. 3.2 m2 coverage is ample. |
| **Shed Felt** (10m x 1m) | 1 roll | YES | 10 m2 vs ~1.1 m2 needed. Very generous. |
| **Galv Screws (assorted box)** | 1 box | LIKELY YES | Weekend 1 alone needs ~76 screws (40x 75mm, 16x 65mm, 20x 50mm). A standard assorted box is 300-500 screws. Across all weekends (frame + cladding + door + shelves) expect ~200-300 total. One box should suffice if it is a decent assorted box. Check box contents match sizes needed (40mm, 50mm, 65mm, 75mm). |
| **T-Hinges** | 2 pairs | YES | Only 1 door, needs 1 pair (2 hinges). Second pair is spare or for a future gate. |
| **Cabin Hook / Bolt** | 1 | YES | 1 door, 1 latch. |
| **Felt Nails / Clout Nails 13mm** | 1 box | YES | ~40-60 nails needed for felt and shingles. Standard box is 500g (~200+ nails). |
| **White Fence Paint 5L** | 1 tin | YES | Covers 15-25 m2/litre = 75-125 m2 total. Bin store surface area is ~8-10 m2. Very generous. |
| **White Fence Paint 750ml** | 1 tin | YES | Second coat. 6-9 m2 coverage, sufficient for touch-ups or full second coat on visible faces. |
| **Exterior Plywood (18mm)** | NOT IN LIST | MUST BUY | Needed for roof sheathing (~1300x1000mm) and 3 shelf boards (~700x750mm each). Buy 1 full sheet (2440x1220mm) and cut both roof and shelves from it. |
| **Featheredge packs (1.8m, 10-pack)** | 3 packs (30 boards) | YES | Back wall ~13-15 boards + left wall ~8-10 boards + centre divider ~4-5 boards = ~25-30 boards. Tight but sufficient. |
| **Featheredge 3m lengths** | 8 pieces | YES | Door panel (~6-7 boards) + right front solid panel (~3-4 boards). 8 pieces covers both. |

---

## Items to Add to Shopping List

| Item | Qty | Reason |
|------|-----|--------|
| **Rough Sawn Treated Whitewood 50x22mm, 1.8m** | 3 extra (7 total) | Shelf battens for Weekend 4. Original 4 sticks all used for roof battens; none left for 6x 750mm shelf battens. |
| **Exterior Plywood 18mm, full sheet (2440x1220mm)** | 1 sheet | Roof sheathing + shelf boards. Already flagged as missing in original guide. |

---

## Key Findings

1. **50x47mm 2.4m sticks (10 available): 2 SPARE.** Only 8 sticks needed (6 posts + 2 door stiles, each paired with a 750mm rail or 500mm door rail). Moving braces to user-supplied 15x38mm stock freed up 2 sticks that previously held 1300mm rails + 1000mm braces. The spare sticks provide margin for miscuts.

2. **50x47mm 1.8m sticks (8 available): 3 surplus.** 5 of 8 needed (4 for 1300mm rails + 1 for door rail). With noggins removed, 3 spare sticks remain -- ample margin for miscuts.

3. **15x38mm 2.4m sticks (8 user-supplied): 6 SPARE.** Only 2 sticks needed for all 4 X-braces (2 back + 2 left, paired on 2 sticks). At 15mm thick, the crossing overlap is only 30mm -- less than the 47mm frame depth.

4. **50x22mm 1.8m sticks (4 available): 3 SHORT.** The shopping list only covers roof battens (4x 1300mm). Shelf battens (6x 750mm) for Weekend 4 require 3 additional sticks. Buy 7 total.

5. **Plywood: NOT IN LIST.** Must buy separately (1 full sheet covers roof + shelves).

6. **Design change impact (no right wall mid-rail):** Saves one 750mm cut. This is already reflected in the Weekend 1 guide cut list -- the right side wall has no mid-height depth rail. The plan above does not include one.

7. **Noggins removed from Weekend 1.** The mid-rail, top rail, and bottom rail provide sufficient fixing points for cladding. Noggins can be added in Weekend 3 if the cladding boards bow or feel loose.

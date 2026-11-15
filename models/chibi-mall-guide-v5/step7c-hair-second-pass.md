# Step 7c: second hair pass (2026-11-15)

Builds on `step7b-hair-layered.md`. Changes this pass:

- Locks close with a rounded dome at both ends (`kit.add_lock`, `HAIR_CAP_RINGS`); before, a lock with a thick end finished in a flat face that read as a spike in the side view (the forward-pointing bang of step 7b). The spike is gone.
- Fringe locks have their own taper and end floor (`FRINGE`, `FRINGE_B` in `config.py`), so their ends are fuller and blunt; their forward flare was cut because the thicker end had pushed the bangs about 20 px too far forward.
- The cap dome leans forward toward its top (`CAP['shear']`), as sheet B's cap does in the side view; this removed the cap-top rows that dominated the side-rear error.
- The skull is a little shallower and moved back (`HEAD` y radius 0.188, centre y 0.057), the ears moved up to z 0.60, side and back locks were thinned.
- Lock samples reduced to 12 per lock, 12 sides and 2 cap rings per end to keep the triangle budget: the rounded caps had raised the figure to 38,656 triangles.

## Gate result (threshold mean 9.3 px, max 17.5 px at 751 px/m, set before step 7; head rows 0..300 follow v4's z >= 0.60 m)

| View | Rows 0..300 mean / max px | Verdict |
| --- | --- | --- |
| Front half-width | 6.5 / 12.9 | **PASS** |
| Side rear | 6.2 / 20.0 | FAIL on max by 2.5 px; mean within the gate |
| Side front | 8.4 / 32.0 | FAIL on max; mean within the gate |

Worst rows: front 260 (ear and jaw); side rear rows 0, 77 to 78, 90; side front rows 192 to 195 (the sheet keeps hair forward down to about row 225 where ours ends at row 190). Rows 0..360 add the chin, neck and collar (still placeholders): front 8.7 / 61, side rear 7.7 / 71, side front 9.0 / 32. Overlays: `step7c-out/gate-overlay-*.png`; numbers: `step7c-out/hair-gate.json`.

History of the rows 0..300 numbers (front mean/max, side rear, side front): step 7 lobes 9.6/24, 15.2/42, 12.3/31; step 7b locks 7.4/15.9, 8.7/37, 13.4/27; this pass 6.5/12.9, 6.2/20, 8.4/32.

## Measurements

| Item | Value |
| --- | --- |
| Hair | 7,272 triangles (plan allocation 5,000) |
| Whole figure so far | 35,416 triangles of the 40,000 budget |
| Face check | head GLB (head and eyes only, rebuilt on the new skull) still validates with 0 errors and 0 warnings, and smile, surprised and blink still load in Three.js (`step7c-out/face-keys-az0.png`) |
| Overlaps | intended embedding only: Head x Hair 1,404, Cap x Hair 1,946, Cap x Head 183, Arm in Glove 40, thigh in Shorts 19, Head x Neck 119 |

## Visual review (mine, not independent)

From `step7c-out/head-sheet.png`: layered, flowing locks with rounded ends; the back and side views are the closest to sheet B; the bangs end in soft drips; the forward-pointing spike of step 7b is gone.

Remaining differences: the sheet's bangs are broader, rounder lobes and its side hair hangs lower over the temples; the hair colour is the sampled value (lighter than the sheet's rendered chocolate); the skull below the ears is still boxier than the sheet's; chin, neck and collar are placeholders. Not covered: independent review, the three-quarter and back views by overlay, UVs, rig, export.

## Open

- The gate is met on the front only. The remaining side misses are 2.5 px (rear max) and 14.5 px (front max, a hair-length difference at rows 190 to 225) over the gate.
- The standard still says "6 to 8 lobes" for hair (section 2) and in the framework table; the owner agreed to relax it. Not updated yet (my local checkout lags the pushed documents).

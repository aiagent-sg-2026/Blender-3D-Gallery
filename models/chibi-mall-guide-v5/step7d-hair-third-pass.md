# Step 7d: third hair pass (2026-11-15)

Builds on `step7c-hair-second-pass.md`. Changes (all in `config.py`): the centre bang is longer (ends at elevation 9 degrees, about z 0.72, between the eyes, as in sheet B's front view); the side fringe locks end at 21 degrees so they stay above the brows; the side locks hang lower over the temples (end at -18 degrees, just above the ears); the outer fringe overlay locks reach 22 degrees; the hair colour is darker (`4A2C22`, chosen by eye, the sampled value was lighter than the sheet's rendered brown).

## Gate result (threshold mean 9.3 px, max 17.5 px at 751 px/m; head rows 0..300)

| View | Rows 0..300 mean / max px | Verdict | Previous pass |
| --- | --- | --- | --- |
| Front half-width | 6.5 / 12.9 | **PASS** | 6.5 / 12.9 |
| Side rear | 6.2 / 20.0 | FAIL on max by 2.5 px | 6.2 / 20.0 |
| Side front | 6.4 / 21.0 | FAIL on max by 3.5 px | 8.4 / 32.0 |

All three means are within the gate. The side-front maximum fell from 32 to 21 px because the bangs now hang down to the sheet's height; the worst rows are now 214 to 217 (the end of the centre bang). The side-rear maximum (20 px) is unchanged: rows 0 and 77 to 90 (cap top and the back of the cap rim). Overlays: `step7d-out/gate-overlay-*.png`; numbers: `step7d-out/hair-gate.json`.

The side fringe change in the last edit (12 to 21 degrees) did not change any gate number, so it only matters for the look: it keeps the brows from being covered by the side bangs.

## Measurements

35,416 triangles for the whole figure so far (budget 40,000), hair about 7,300. Overlaps unchanged from step 7c (intended embedding only). The face keys were not rebuilt in this pass; the face geometry is unchanged.

## Visual review (mine, not independent)

`step7d-out/head-sheet.png`: the bangs now hang to eye level in the middle like the sheet's; the brows stay mostly visible; the side hair covers the temples; the hair is darker. Still different from the sheet: the sheet's bangs are broader and rounder lobes, the cap rim and cap top differ from the sheet's, the skull below the ears is boxier, and chin, neck and collar are placeholders. Not covered: independent review, UVs, rig, export.

## Open

Two gate maxima are 2.5 and 3.5 px over; the standard's hair rule (section 2 and the framework table) still says "6 to 8 lobes" and has not been updated.

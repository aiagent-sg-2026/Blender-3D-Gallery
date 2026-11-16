# Step 7b: layered hair (2026-11-15), replaces the eight lobes of step 7

The owner agreed to layered hair and to relaxing the "6 to 8 lobes" rule in the standard. The lobes of step 7 (`step7-hair.md`) are replaced by 18 swept locks in two layers: `hair.py` sweeps an elliptical section along a path over the skull, tapering to rounded ends with a floor (`HAIR_END_MIN`) so no end is a point; layer A (10 locks) covers the skull, layer B (8 locks) sits on top and overlaps A's seams. Values are in `config.py` (`HAIR_LOCKS`, `HAIR_TAPER`, `HAIR_END_MIN`). The cap now has its top at z = 1.00 m so the figure is 751 px tall like sheet B (the earlier lower cap shifted every row of the gate by about 10 px).

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_parts.py -- /tmp/parts-out   # head-sheet.png, parts-sheet.png, report
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/hair_gate.py -- /tmp/gate-out    # head-row silhouette gate
```

## Gate result (threshold set before step 7: mean 9.3 px, max 17.5 px at 751 px/m; head rows 0..300 follow v4's z >= 0.60 m)

| View | Rows 0..300 mean / max px | Verdict | Rows 0..360 mean / max px |
| --- | --- | --- | --- |
| Front half-width | 7.4 / 15.9 | **PASS** | 8.6 / 61.1 |
| Side rear | 8.7 / 37.0 | FAIL on max (mean within the gate) | 10.2 / 71.0 |
| Side front | 13.4 / 27.0 | FAIL | 12.7 / 27.0 |

Worst rows: front 259 to 261 and 286 (ears and jaw); side rear rows 0 to 3 (the very top of the cap: sheet 16 px wide and tilted forward, ours 36 px wide and level); side front rows around 181 (the end of the bangs). Rows 330 to 360 add the chin, neck and collar, which are still placeholders. Overlays: `step7b-out/gate-overlay-front.png`, `gate-overlay-side.png`; numbers: `step7b-out/hair-gate.json`.

Step 7's first hair for comparison (rows 0..300): front 9.6 / 24, side rear 15.2 / 42, side front 12.3 / 31.

## Measurements

| Item | Value |
| --- | --- |
| Hair | 7,488 triangles (plan allocation 5,000); cap 2,152 |
| Whole figure so far | 35,632 triangles of the 40,000 budget; the vest (7,756) and cap are the places to trim |
| Primitives | 27 as named parts, 13 materials |
| Overlaps | intended embedding only: Head x Hair 1,310, Cap x Hair 2,122, Cap x Head 187 (the solid cap sits into the hair and skull), Arm in Glove 40, thigh in Shorts 19, Head x Neck 133 |

## Visual review (mine, not independent)

From `step7b-out/head-sheet.png`: the hair now reads as flowing, overlapping locks with rounded ends and creases that follow the head, much closer to the sheet's layered style than the pebbles of step 7; the back view and the side view are the closest.

Defects I can see:
- In the side view one bang jutting forward at the forehead reads as a pointed tuft, the kind of tip the v4 review flagged. I reduced the forward flare of the fringe (0.034 to 0.022) and it remains. A real fix needs that lock redesigned, not another flare value.
- The bang ends look like soft drips from the front; the sheet's are broader, rounder lobes.
- The hair colour is the value sampled from the sheet, lighter than the sheet's rendered chocolate.
- The skull below the ears is still boxier than the sheet's; the neck and chin rows are placeholders.
- No independent review has been done.

## Open

- Gate not fully met (side rear max, side front). Decision for the owner: accept the hair and carry the side-view gaps into the QA run, or spend another pass on the cap top tilt and the forward bang.
- The standard must be updated: the hair rule (section 2, "6 to 8 thick, blunt, rounded locks") and the framework table now describe 18 layered locks. Not done yet because my local checkout lags the pushed versions of those documents.

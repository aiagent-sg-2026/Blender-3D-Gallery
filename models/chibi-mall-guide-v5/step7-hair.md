# Step 7: hair (2026-11-15)

Eight thick, blunt, rounded lobes wrapped on the skull by `hair.py` (three fringe lobes, two side lobes, three back lobes), values in `config.py` (`HAIR_LOBES`, `HAIR_P`). The cap now rests on the hair. The skull was widened and deepened and the ears moved to where sheet B has them. Silhouette gate in `hair_gate.py`. Blender 5.1.2 headless.

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_parts.py -- /tmp/parts-out   # renders head-sheet.png and parts-sheet.png
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/hair_gate.py -- /tmp/gate-out    # head-row silhouette gate
```

## Result: the head-row silhouette gate is NOT met

Gate (same as v4's G4 and the blockout, converted to 751 px/m): mean 9.3 px, max 17.5 px. It was set before this step. v4 applied it to head rows at z >= 0.60 m, which is sheet rows 0 to 300; I report that range and also rows 0 to 360 (which add the chin, neck and collar).

| View | Rows 0..300 mean / max px | Rows 0..360 mean / max px | Gate |
| --- | --- | --- | --- |
| Front half-width | 9.6 / 24 | 14.2 / 76 | FAIL (mean within 0.3 px on rows 0..300; max not) |
| Side rear | 15.2 / 42 | 18.9 / 94 | FAIL |
| Side front | 12.3 / 31 | 12.4 / 33 | FAIL |

Overlays (red outline of the built figure over sheet B): `step7-out/gate-overlay-front.png`, `step7-out/gate-overlay-side.png`. Numbers: `step7-out/hair-gate.json`. The side shift was fitted on the body rows, not on the head, so the head error is not hidden by the fit.

How the numbers moved while I tuned (rows 0..360 front mean): 17.9 with the first hair and blockout skull, 11.9 after widening the skull and placing the ears, 14.2 after rounding the jaw (p 4.0 to 3.2) to remove the box-like look. Tuning the jaw for looks cost silhouette accuracy.

## Measurements

| Item | Value |
| --- | --- |
| Hair triangles | 5,760 (plan allocation 5,000) |
| Whole figure so far | 33,904 triangles (budget 40,000); Head 5,516, Cap 2,152 |
| Primitives | 27 as named parts, 13 materials; merged per material about 13 |
| Overlaps | intended embedding only: Head x Hair (1,024; the lobes wrap the skull), Cap x Hair (690; the solid cap sits into the hair), Arm in Glove (40), thigh in Shorts (19), Head x Neck (133) |

Pointed tips: none; every lobe is a rounded superellipsoid (p = 2.4), which was the v4 lesson.

## Visual review (mine, not independent)

From `step7-out/head-sheet.png` (head close-ups, four views):

- Front reads as a bob with bangs and the cap on top; coverage of the skull is good.
- Not met against sheet B: the sheet's hair is swirled and layered with creases that flow around the head; here the lobes read as separate pebbles. The side lobes look like flat oval stickers from the side, and the three back lobes read as vertical sausages with creases between them.
- The skull below the ears is boxier than sheet B's; the ears were moved down to the sheet's height and now sit on the skull side.
- The face from step 6 was not changed except for the skull it sits on.

## Not covered

Independent reviewer (required by the standard for G5), a hair-versus-face check by overlay on the three-quarter and back views, UVs, rig, export, mall runtime. The hair colour is the sampled value from the sheet's front view, which looks lighter than the sheet's rendered chocolate.

## Decision for the owner

The gate was not met and the look is not the sheet's. Options: (1) accept this as the hair for the rig, animation and QA run and leave hair polish for later; (2) keep working the hair now (the sheet's style probably needs more than eight plain lobes, for example overlapping layers with a gentle swirl), which touches the "6 to 8 lobes" rule in the standard; (3) keep eight lobes and spend more passes tuning shapes against the gate.

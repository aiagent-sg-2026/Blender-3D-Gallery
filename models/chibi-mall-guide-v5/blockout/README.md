# Step 4: proportion blockout against sheet B (2026-11-15)

Primitive ellipsoids only (no real parts, no rig, no materials), built from `../config.py`, rendered orthographically at 751 px per metre and compared with the silhouette of `reference/turnaround-b.png`. Blender 5.1.2 headless.

```sh
# only to re-measure the sheet:
blender --background --factory-startup --python models/chibi-mall-guide-v5/blockout/measure_sheet.py -- \
  models/chibi-mall-guide-v5/reference/turnaround-b.png models/chibi-mall-guide-v5/blockout/sheet-b-silhouette.json
# build, render and compare:
blender --background --factory-startup --python-exit-code 1 \
  --python models/chibi-mall-guide-v5/blockout/build_and_compare.py -- /tmp/blockout-out
```

## What was measured from sheet B (evidence: `sheet-b-silhouette.json`)

- Cap top to sole is 751 px; this is taken as 1.00 m.
- The head without the cap is about 2.55 heads tall (hair top about row 60 to chin about row 360); with the cap, cap top to chin is about 2.1 heads. "About 2.5 heads" in the standard therefore holds for the head without the cap.
- The head including hair is about 0.50 m wide (wider than tall); the hair mass is the widest part of the figure.
- In the side view the head and hair mass sits about 0.083 m behind the body axis; the face is about 0.02 m in front of the torso front and the hair reaches about 0.22 m behind the torso back.
- Row landmarks (cap top = row 0): vest about 369 to 529, shorts 529 to 599, socks 619 to 689, shoes 689 to 751. These were read by eye from the sheet and the width profile, not measured automatically.

## Result against the gate set before the run

Gate: mean 8 px, max 15 px at 645 px/m (v4's G4), converted to 751 px/m: mean 9.3 px, max 17.5 px. Front compares the half-width of the character's left side (the sign prop is on the other side). Side compares the rear extent and the front extent outside the rows the sign and hand cover (sheet rows 330 to 520), after one fitted shift.

| View | Mean px | Max px | Verdict |
| --- | --- | --- | --- |
| Front | 9.1 | 47 | FAIL (max); the mean is within the gate |
| Side, rear | 11.3 | 59 | FAIL |
| Side, front | 17.6 | 54 | FAIL |

Overall: **the blockout does not pass the gate.** The total height matches (751 px). Overlays: `out/overlay-front.png` and `out/overlay-side.png` (red = blockout outline over the sheet); numbers: `out/blockout-report.json`.

## Why it fails

- Front max 47 px comes from the sole rows (about 735 to 740): the sheet's sneaker sole is wider and flatter than the ellipsoid shoe.
- Side front: the sheet's face sits about 40 px behind bangs that overhang it at rows 200 to 250; a single head ellipsoid cannot follow a hair overhang. This is hair and face shape, not body proportion, and will only be settled with the real head and hair.
- Side rear and the jaw rows: the real head tapers in depth faster than the ellipsoid.
- The blockout was tuned by hand in four passes. More ellipsoid tuning would overfit; the remaining error needs the real parts.

Open decision for the owner: keep this gate for the blockout (more tuning) or accept the blockout as a proportion reference now and apply the gate to the real head, hair and shoes at plan steps 6 and 7.

## Not covered

Colours, real garment shapes, face, rig, the sign prop, the three-quarter and back views, Three.js rendering.

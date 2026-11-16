# Step 6: head, face and eyes (2026-11-15), plus the step 5 overlap cleanup

Built by `head.py` (called from `build_parts.py`; `build_head.py` builds and exports the head alone for the Three.js check). Blender 5.1.2, Three.js 0.187.0 in headless Chromium (software GL). The head is a skull without hair; the cap still floats above it until the hair exists (step 7).

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_head.py -- /tmp/head-out
node models/chibi-mall-guide-v5/shoot-head.mjs /tmp/head-out /tmp/head-out/shots   # four states side by side: neutral, smile, surprised, blink
```

## What was built

- `Head`: skull (56 x 40 segments), ears, a small nose, brows, an open-smile mouth and two blush cheeks. Brows, mouth and cheeks are patches lying on the skull (flush with the skin at their edge, raised 1.5 to 3 mm in the middle), so the shapes are designed outlines instead of an intersection of two surfaces. Four material slots (skin, brow, mouth red, blush). No texture.
- `Eyes`: two elliptical patches (50 x 54 mm half-axes) with a dark iris and a white highlight, in one mesh with two material slots.
- Shape keys: `Head` has `smile` and `surprised` (brows, mouth and cheeks move; displaced vertices are re-projected onto the skull so they stay on the skin); `Eyes` has `blink` (the eyes sink 16 mm behind the skin; method chosen in `prototype/blink/`).
- Face landmarks come from sheet B (eyes z about 0.64, brows 0.735, mouth 0.57, chin 0.52); colours for the face were chosen by eye, not sampled.

## Results (measured)

| Item | Value |
| --- | --- |
| Triangles | Head 5,516; Eyes 832; whole figure so far 28,144 (budget 40,000) |
| Head GLB | glTF Validator 0 errors, 0 warnings, 0 infos (213 KB); keys load in Three.js with names intact |
| Blink | in the Three.js render both eyes disappear completely at blink = 1, from the front, 35 degrees and the side |
| Expressions | smile widens the mouth and lifts the cheeks; surprised raises the brows and makes the mouth a tall oval |
| Part overlaps | only intended ones remain: Arm in Glove (40), thigh in Shorts (19), neck into the head (135). Vest, Shirt and Neckerchief overlaps are cleared |
| Primitives | 26 as named parts, 12 materials; merged per material about 12, below the 20 draw-call limit once hair adds one |

Fixes made while building: the first smile and surprised keys moved patch vertices up without re-projecting them onto the curved skull, so the mouth corners sank into the skin and the mouth looked narrower; the keys now re-project. The cheek patches overlapped the lower eyes, so they were moved down.

## Known problems (my review, not independent)

- The hair is missing, so the head reads as bald and small beside the 0.50 m hair-inclusive blockout head; proportions can only be judged after step 7.
- The neutral expression is already a mild smile (the base mouth is a crescent). A calmer neutral may be wanted.
- Cheek patches show a little rough edge at grazing angles (depth precision at 2 mm lift); the mouth shows tiny speckles at the bottom of the surprised shape.
- The eye highlight is a faceted patch, not round; the iris has no pupil or sclera.
- The face is built from material patches instead of the planned 1024 px face texture. That saves a texture but costs four material slots on the head; merging into a texture is an option.
- The neck is still an ellipsoid placeholder.
- Not tested: the face against sheet B by silhouette gate or by an independent reviewer; mall runtime; performance.

## Files

`step6-out/head-az0.png`, `head-az35.png` (neutral, smile, surprised, blink), `head-report.json`, `figure-sheet.png` (whole figure, four views), `figure-report.json`.

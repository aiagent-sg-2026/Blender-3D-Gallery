# Step 5: body and garment parts (2026-11-15)

Named parts built procedurally from `config.py` by `build_parts.py` (modules `kit.py`, `garments.py`, `limbs.py`). Head and hair are still the blockout ellipsoids (`Head_placeholder`, `Neck_placeholder`). No rig, no UVs, no export. Blender 5.1.2 headless.

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_parts.py -- /tmp/parts-out
```

Outputs: `step5-out/parts-sheet.png` (front, three-quarter, side, back, Workbench render with material colours) and `step5-out/parts-report.json`. Palette: sampled from sheet B (`parts_palette.py`), stored in `config.py`.

## Parts and budget (measured)

| Part | Triangles | Plan allocation |
| --- | --- | --- |
| Vest (with buttons, badge, pockets) | 7,756 | 6,000 for vest, shirt and sleeves together |
| Shirt (torso shell, sleeves) | 2,624 | (included above) |
| Neckerchief | 1,192 | 800 |
| Shorts | 1,480 | 1,500 |
| Cap (dome, rim, pin) | 2,152 | 1,000 |
| Arms L/R | 366 + 366 | 2,000 |
| Gloves L/R | 720 + 720 | 2,000 |
| Legs L/R | 28 + 28 | 2,500 with socks |
| Socks L/R | 272 + 272 | (included above) |
| Shoes L/R | 2,008 + 2,008 | 3,000 |
| **Total body and garments** | **21,992** | about 19,300 |

The 40,000 triangle budget for the whole character still holds with about 18,000 left for head, hair and eyes (plan allocation about 14,200), but vest, cap, shoes and neckerchief are above their allocations. The vest is the main cost because it is built at 72 x 44 segments to keep its cut edges smooth; it can be reduced once the cut edges are modelled properly instead of deleting faces.

Primitives: 20 as separate named parts, 8 distinct materials. If meshes are merged per material at export (rigid skinning can use vertex groups per bone), the primitive count falls to about 8, which leaves room for the head, hair and eyes under the 20 draw-call limit. Not yet tested.

## Overlaps (BVH triangle test between every pair of parts)

Intended, not defects: Arm x Glove (the wrist ends inside the glove, 40 triangles); Shorts x Leg (the thigh enters the shorts leg, 19); anything with the placeholders (Cap x Head, Head x Neck; the real head and hair replace them).

Unresolved: **Vest x Shirt, 96 triangles**, located at the front centre, z 0.33 to 0.43, y -0.10 to -0.08 (x -0.04 to 0.06). My reading is that the vest's buttons and pockets, embedded into the vest wall, touch the shirt below; I did not confirm that. **Vest x Neckerchief, 70 triangles**, at x about 0, z 0.42 to 0.43: the neckerchief flap touches the vest front. The gate "no intersections" is therefore NOT met.

Overlaps fixed during this step: shoes against each other, shirt against shorts, vest and shirt against the neck, gloves against the shorts, vest and shirt against the arms. Fixes came from narrowing the torso (the blockout width included the arms), moving the arms outward, and making the front-surface function match the superellipsoid it is placed on.

## Visual review (mine, not independent)

Read from `step5-out/parts-sheet.png`: the proportions follow the blockout and the parts read as the right garments, but this is a rough stage.

- The vest and shirt cut edges (neck, armholes, hem) are slightly stepped because faces are deleted by centre position.
- The vest is a rounded bean with p-exponents, not the straighter tube of the sheet; the sleeves read as plain cylinders.
- The neckerchief is a thin ring with a knot and two small flaps; the sheet's version is a fuller draped scarf.
- Gloves are simple mittens with a thumb blob; shoes are four ellipsoids and lack the sheet's laces and side shapes.
- The brass badge and buttons are tiny.
- The head placeholder is 0.50 m wide because it includes the hair mass, so it looks oversized next to the body; this resolves when the real head and hair replace it.

## Not covered

Silhouette gate for the parts, UVs, rig and binding, the real head, hair, eyes, brows, the sign prop, the three-quarter and back views against the sheet, Three.js load of these parts, independent review.

## Decision for the owner

Accept step 5 as a rough parts pass (overlaps and detail polish carried into later steps), or keep refining the vest, neckerchief and shoes now. Not decided.

# GJH-M058 Premium Wall Shelf Endcap

Original wide retail endcap with **2.4 × 0.55 × 2.4 m outer dimensions** (width × depth × height), including trims. GJH-M058 is a separate GJH360 backlog identity, not a Gallery500 ID. It is not a narrow gondola endcap and does not silently reinterpret the requested footprint.

Three separate front-radius wooden shelves have open lateral access, narrow rear support posts, a finished rear panel and two rear docking anchors. Unlike M056's tall enclosed sides or M057's L-shaped corner footprint, the exposed rounded shelf noses make this endcap recognizable from either side. No X braces, products, logos or copied packaging are included. Emerald lacquer, champagne gold, warm wood and dark stone are original procedural materials; the two original baked PNG textures export into GLB. No Blender-only shader is required by the browser.

## Files and editable contract

- Canonical `.blend` and `generate.py`, four real LOD exports, `optimized.glb` identical to LOD0, and a conservative box `collision.glb`.
- 27 independently editable mesh parts with stable semantic names across LODs. Three shelves, price rails, five LEDs, cabinet, trims and blank header are independent.
- 24 product-placement anchors, 8 per row, plus two rear docking reference anchors. These are transforms, not executable behavior or a certified fastening system.
- `header_surface_front`: local +Z outward/+Y up, 2.04 × 0.36 m label area, optional overlay local Z +0.002 m. Actual full label-area visibility is ray-tested from front and both diagonal sides.
- Metre units, floor-centre origin. Blender +Z up/-Y front; glTF +Y up/+Z front.
- Shelf Inspector supports M058 selection, three row highlights, five LED toggles together, single-face concept text, manual LOD0–3, and reset. Desktop Chromium and 390px touch emulation verified; physical Android/iOS, automatic LOD and external product loading are not implemented. See `../../docs/shelf-inspector-m058-qa.md`.

## Actual local validation

| LOD | Triangles | Bytes |
| --- | ---: | ---: |
| 0 | 11,044 | 863,844 |
| 1 | 3,812 | 376,916 |
| 2 | 1,580 | 240,552 |
| 3 | 388 | 157,140 |

PASS: Khronos validation has zero errors and warnings for all four LODs and collider. The validator checks embedded textures, real dimensions, finite mesh attributes, independent components, stable anchors, rounded-corner occupied/empty points, open lateral access, shelf-to-back support, all five LED contacts and label visibility. See `reports/assets.json`.

PASS: canonical source opened, edited copy saved/reopened and exported without regeneration; canonical source hash unchanged. The test requires `reports/source-edit/edited.glb`; retain that artifact and the edited `.blend` as provenance, not as replacement source. See `reports/sources.json`.

PASS: actual final eight Blender previews inspected, then actual Gallery screenshots at 1440 and 390 inspected. Final Gallery browser cases at 1440, 768 and 390 verify the loaded GLB hash, orbit, zoom, reset and repeated reopen. Evidence: `reports/browser/results.json`, representative `*-1440-initial.png` and `*-390-initial.png`; full local screenshots remain available. Chromium viewport tests are **not** real Android/iOS testing.

PASS: three focused asset tests and normal repository build. The original 555 catalog entries and collection memberships are unchanged; local baseline 345f3104 gains one unique entry (556 total before later integration). See `reports/catalog-preservation.json`. This checkout predates M057's later main integration; release coordination must preserve that subsequent entry too.

A post-render review found the base LED 2 mm off its support; its centre was corrected and a fifth support-contact assertion added. All four exports/source and all previews were regenerated before final testing. `reports/base-led-contact-note.md` records this correction. Final evidence is from job 592f2d46-28ea-4bd4-9126-b7cf72d6b4e8, not the earlier incomplete support coverage.

No CI, publication, physical-device, structural-load, safety, accessibility, official-brand or photometric certification is claimed. Local status is validated, not deployed. See `LICENSE.md` for rights limits.

## Reproduction

Use the existing Blender 4.x environment: `blender -b -P models/gjh-m058-premium-wall-shelf-endcap/generate.py`. Then run its `validate.mjs`, the Blender `inspect_sources.py`, and `verify_source_edit.mjs`. `--skip-render` skips previews and does not create visual evidence. Run `node --test tests/gjh-m058.test.mjs`, the normal repository build, and `node scripts/test-gjh-m058-browser.mjs`. No tests, workflow or global viewer behavior were weakened or replaced.

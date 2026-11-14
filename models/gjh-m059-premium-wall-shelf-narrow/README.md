# GJH-M059 Premium Wall Shelf Narrow

Original modular narrow display cabinet: **0.8 × 0.55 × 2.4 m** outer dimensions (width × depth × height), including trim. This is an explicitly chosen interpretation of the backlog name “narrow”. The original table repeated **2.4 × 0.55 × 2.4 m**; this asset deliberately differs in width and must not be described as matching that original table footprint. GJH-M059 belongs to the separate GJH360 backlog, not Gallery500.

Three independent wood shelves, five independently editable supported LED diffusers, emerald cabinet panels, champagne-gold trims, dark stone base and a blank front header. No X braces, official brand art or products. Wood and stone appearance comes from original baked PNG textures embedded in GLB, not Blender-only procedural shaders. Real-world metre units; floor-centre origin; Blender +Z up/-Y front, glTF +Y up/+Z front.

## Product placement, not crowded point counts

Each 0.592 m-wide shelf has **two anchors**, at X ±0.14 m, for six total across three rows. Reference product footprints are 0.18 × 0.22 m. Actual GLB geometry tests verify each footprint corner lies over the shelf, at least 60 mm side clearance and 100 mm between the two footprints. Anchor centres are 280 mm apart. The contract does not claim arbitrary product heights or shapes fit; future product loading needs its own collision checks. Nothing is baked onto the shelves.

## Artifacts and scope

Canonical editable `.blend`, `generate.py`, four genuine LOD `.glb` files, identical `optimized.glb`/LOD0, conservative box collider, original textures, eight reviewed previews, metadata, support manifest and focused tests are included. All 29 mesh parts and six placement anchors keep stable names across LODs.

The explicit `header_surface_front` anchor has local +Z outward/+Y up and a 0.50 × 0.36 m label area. Front and both 45-degree views are tested against actual occluders. The manifest is ready for future integration, but **M059 Inspector support is not implemented yet**. Gallery orbit, zoom, reset and repeated reopening are verified. No automatic LOD or product loading is claimed.

## Actual local evidence

| LOD | Triangles | Bytes |
| --- | ---: | ---: |
| 0 | 8,700 | 709,252 |
| 1 | 3,132 | 334,728 |
| 2 | 1,276 | 220,508 |
| 3 | 348 | 153,436 |

- PASS `reports/assets.json`: four LODs and collider have zero Khronos errors/warnings; finite normals/UVs, bounded scale, embedded textures, real shelf support, all five LED contacts, label visibility and product footprint checks.
- PASS `reports/sources.json`: source opened, edited copy saved/reopened and re-exported without regeneration; canonical source remains unchanged. `reports/source-edit/edited.glb` is required by tests and must be retained along with its edited `.blend` provenance.
- PASS actual final eight Blender previews and representative Gallery1440/390 pixel inspection. Three browser viewport cases at1440/768/390 verify the actual loaded GLB hash plus orbit/zoom/reset/reopen. `reports/browser/results.json` and screenshots record the evidence. These are Chromium viewport emulations, **not physical Android/iOS tests**.
- PASS three focused asset tests and normal repository build. Final local job: fd5c96a0-ab15-4a8a-b41e-71cbd84b8576.
- PASS catalog preservation: baseline f466c66f had556 entries; only this registration added (557 locally), with all original objects and collection memberships unchanged. Parent integration must also preserve any later main additions such as M058.

Local validated status is not a CI, publication or deployment claim. No structural load, lighting-temperature, safety, accessibility or official-brand certification is made. See `LICENSE.md`.

## Reproduce

Use Blender4.x with `-b -P models/gjh-m059-premium-wall-shelf-narrow/generate.py`, then run its `validate.mjs`, Blender `inspect_sources.py`, and `verify_source_edit.mjs`. `--skip-render` omits all previews and cannot substitute for visual inspection. Run `node --test tests/gjh-m059.test.mjs`, the normal repository build and `node scripts/test-gjh-m059-browser.mjs`. Keep the source-edit GLB used by the test. No existing tests, workflows or runtime controls were weakened.


## Coplanar inner-lining correction, final browser gate pending

The initial browser interactions passed, but an independently inspected Inspector side view showed gold/green striping. This **visual FAIL** overrides the earlier broad pass interpretation. Across all four original LODs the gold lining and pillar visible surfaces differed by only 1.40e-8m. `reports/inner-trim-coplanar-before.json` and `inner-trim-regression-before.log` preserve the finding and failing new test; the original runtime screenshots remain unchanged.

Final geometry uses a real4mm lining: back face touches the pillar, visible face is4mm inward. Shelf/canopy width is0.592m and ends contact the lining, avoiding hidden volume overlap. Product side clearance remains0.066m. New actual-GLB tests require separation, support contact, wood end-contact and the lining as the first visible ray hit. All four LODs, canonical source and eight previews were regenerated; source-edit validation and focused tests pass. Those eight new previews were actually inspected. No camera, material depth offset or rendering workaround was introduced.

Job87764f9a-cb99-4e6e-9b86-f5de60293873 proves the repaired geometry/source checks only. Prior browser hash screenshots no longer represent these new exports. Final browser/Inspector side-view verification is **NEEDS REVIEW** and will run once after integration onto the release baseline; no final release or deployment pass is claimed here.

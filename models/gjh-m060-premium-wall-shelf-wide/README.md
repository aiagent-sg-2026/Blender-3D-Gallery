# GJH-M060 Premium Wall Shelf Wide

Local asset QA: **PASS**. Inspector integration: **NOT INTEGRATED**. This local report does not verify remote CI or deployment; see subsequent release records.

## Design and editable contract
Original double-bay cabinet, nominal and measured envelope 2.4 × 0.55 × 2.4 m (width/depth/height). A central supporting upright divides three display rows into six independently editable wooden boards, distinguishing it from M056 single-span and M058 open-sided endcap. Deep green lacquer, champagne-coloured trim, original wood/stone PNG textures, eight independent LEDs and one blank header. No X-brace, branded artwork, products, certified structural/load or lighting-temperature claims.

Blender +Z up / -Y front exports as glTF +Y up / +Z front. Floor-centre origin; metre units. All four LODs preserve 42 mesh names and 18 product anchors. Each row group `shelf_1` through `shelf_3` contains left/right board meshes. Each bay has three anchors per row. A 0.20 × 0.22 m reference footprint is checked against its own board, with 0.115 m within-bay separation and at least 0.06 m side clearance. Anchors describe placement only, not implemented product loading.

`support-manifest.json` records row groups, eight LED nodes, header anchor and conservative independent collider. The 1.92 × 0.36 m header surface uses local +Z outward / +Y upward. Four exported LOD files are available, but automatic LOD and Inspector controls are not implemented for this model in this local slice.

## Measured exports

| LOD | Triangles | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| 0 | 12600 | 981976 | `cb45dcc4711e6e3b87c7e5b75ef5530d33ae123cd25d6716481a67da909b102f` |
| 1 | 4536 | 439560 | `fe5c1339055787c9eb021cc9af5fc67e7f4de521e061421f5cd204427895453f` |
| 2 | 1848 | 273792 | `28ccd72c0a65e20c08d6df8bcea01a4f5773ef038cf8e323df3794275d5209c9` |
| 3 | 504 | 176744 | `c656eabf0aafc8dddd24d276c376d2340beae5f4ed6bf76954e0727d403012fd` |

`optimized.glb` equals LOD0. All four LODs and the collider pass Khronos validation with zero errors and warnings. Details: `reports/assets.json`. Budgets: 15,000 triangles / 3,000,000 bytes per visual LOD.

## Evidence and correction
The initial structural pass did not establish visual quality: actual rear-preview inspection found a dark central strip caused by coincident rear faces. `reports/rear-before-correction.png`, `rear-support-before.json`, `rear-support-regression-before.log` and `rear-support-correction.md` preserve that failure. The central upright depth was reduced from 0.50 to 0.46 m and moved 0.02 m forward, preserving its front and top contacts while its rear meets the back panel's front rather than its visible rear. A new exact contact regression fails the original geometry and passes the correction. No camera or shader workaround was used.

Final generation and verification job: `45c59c44-5079-4da4-9df2-8988bf87a725`. All four exports, canonical source and eight previews were regenerated together. Final checks include actual board/lining contacts, 4 mm visible gold-face separation, central rear contact, shelf/header/base LED support, footprint support rays, header visibility rays, stable anchors and editable-source roundtrip. `reports/source-edit/edited.glb` is required by the focused tests; retain it and the edited blend evidence.

Final three focused tests, build and Gallery 1440/768/390 loading/orbit/zoom/reset/reopen checks passed. Use `reports/*-final.log` and `reports/browser-final/results.json` for the final hashes; earlier logs/images are historical evidence, not the final geometry. Actual eight Blender PNGs were inspected: the corrected rear is continuous without the previous central strip. Final Gallery 1440 and 390 initial images were also visually inspected.

Eight full PNG previews remain available. The catalog uses a visually inspected 384 × 384 WebP thumbnail, 11,510 bytes; source-image hash and decode evidence are in `reports/thumbnail.json`.

## Limits and preservation
No physical Android/iOS device testing, automatic LOD, external product loading, or runtime part-highlight claim. Browser widths are Chromium desktop/emulated viewport tests. Existing 556 catalog entries and collection objects remain unchanged; this local slice adds only M060. Original procedural content provenance and redistribution limitations are in `LICENSE.md` and metadata.

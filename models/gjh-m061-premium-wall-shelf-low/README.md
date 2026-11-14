# GJH-M061 Premium Wall Shelf Low

Local asset QA: **PASS**. Inspector: **NOT INTEGRATED**. This local report does not verify remote CI/deployment; see subsequent release records.

## Deliberate dimension interpretation
The original backlog repeats 2.4 × 0.55 × 2.4 m for this named low variant. This asset deliberately uses **2.4 × 0.55 × 1.2 m** (width/depth/height) to form a recognizably low cabinet. It does not claim conformity to the original 2.4 m height. The actual glTF envelope is approximately [2.400000095, 1.199999966, 0.550000012] m in X/Y/Z.

Two rows contain four independently editable bay boards, separated by a solid central upright. Green lacquer, separate gold linings and price rails, original wood/stone textures, six independently editable LED strips, a continuous blank header and conservative separate collider. No X-brace, brand artwork or baked products. Source Blender +Z up / -Y front exports as glTF +Y up / +Z front; floor-centre origin, real metre units.

Twelve stable product anchors: three per bay in each of two rows. Tests require a 0.20 × 0.22 m footprint fully supported by its own board, at least 0.06 m edge clearance, more than 0.11 m within-bay separation and at least 0.12 m vertical clearance. These are reference placement constraints, not structural/load certification or implemented product loading.

## Measured LODs

| LOD | Triangles | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| 0 | 10800 | 862468 | `d2ff536e2b17ef918f7f4d4c0e69fde93e7a25055a92cda50c28298155c783ce` |
| 1 | 3888 | 390284 | `f37c86d78ddc9a4eb72d844c0596db6917b0ae4ec389c58302ccb5ca29da8525` |
| 2 | 1584 | 249148 | `f01eefeab98403af7fa4c1a89fa03aee2e95d233885fe256bc6909facc84b946` |
| 3 | 432 | 165936 | `41682651d971d4494e63163b2851682c2d147fd41d6f0c8dee19ad7934ea6658` |

Each LOD preserves 36 mesh names and 12 anchors. `optimized.glb` equals LOD0. All four LODs and the collider have zero Khronos errors/warnings; budgets are 15,000 triangles and 3 MB. Full evidence: `reports/assets.json`.

## Evidence
Generation/source-edit job `7f835bd4-c110-4e81-b207-fde084c4333d` succeeded. Focused three-test/build/Gallery job `852f96a6-5adc-4661-b67d-528426da1cce` succeeded. Logs are `reports/*-01.log`, with browser results in `reports/browser/results.json`.

Validation explicitly checks 4 mm non-coplanar gold linings, their support contacts and actual first-visible-face rays; board ends/back contacts; central pillar rear contact with the back panel front; shelf, header and base LED support; header visibility; metre bounds, finite normals/UVs and embedded texture structure. The saved source was edited, saved/reopened and exported without running generation. Canonical source hash stayed unchanged. Retain `reports/source-edit/edited.glb` and edited blend because the source-edit test depends on this evidence.

All eight actual PNG previews were inspected, including rear and all three reduced LOD views. The rear has no visible central coplanar strip. The 384px WebP thumbnail was decoded and visually inspected; actual size is 8312 bytes. Full PNG evidence remains; only the lightweight WebP is used in the catalog.

Gallery tests passed at 1440/768/390 widths, checking the actual consumed GLB SHA-256, rendering, orbit/zoom/reset, close/reopen and render-loop teardown. Final 1440 and 390 initial screenshots were visually inspected. These are Chromium viewport tests, not physical Android/iOS tests.

## Runtime and release limits
`support-manifest.json` exposes two row groups (each with two boards), six LED nodes and a front-facing 1.92 × 0.16 m header surface. Inspector integration for this **two-row** variant is not implemented in this asset slice. No automatic LOD, product loading, physical-device or deployment claim. Existing 557 assets and collection objects are preserved, adding only M061 (`reports/catalog-preservation.json`). No public redistribution license is invented; see `LICENSE.md`.

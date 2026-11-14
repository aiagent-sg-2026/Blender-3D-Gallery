# GJH-M062 Curved Luxury Wall Shelf

Local asset QA: **PASS**. Inspector: **PASS (local integrated Chromium tests)**. This local report does not verify remote CI/deployment; see subsequent release records.

## Actual design
Real outer envelope 2.4 × 0.55 × 2.4 m (width/depth/height), matching the backlog dimensions. Three separate single-span **horizontal** boards have a shallow curved front, matching independent gold rails and curved under-shelf LED strips. The Blender front follows `y = -0.25 + 0.10*(x/1.036)^2`: the centre projects 0.10 m beyond the ends. Rear edge is straight at y=0.21 m for a flat wall-facing back. The display surface is not vertically curved. LOD curve subdivisions are 24/12/8/4 with rounded manufactured edges on LOD0–2.

Independent cabinet, trim, shelf_1/2/3, price_rail_1/2/3, five LED strips and one blank anchored header. No X-brace, branded artwork or products. Original PNG wood/stone textures are embedded in GLB; UV coordinates and outward normals are exported. Floor-centre origin, metres, Blender +Z up / -Y front becomes glTF +Y up / +Z front. Conservative collider is separate from visual exports.

Eighteen stable product anchors, six per row, each tested with a 0.20 × 0.20 m footprint and at least 0.20 m vertical clearance. Placement is behind the shallowest curved front area, with genuine mesh ray support rather than bounding-box-only acceptance. No structural/load certification or automatic product loading is claimed.

## Measured exports

| LOD | Triangles | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| 0 | 9156 | 727388 | `8dbe67f737d67b380a8c1823a08f29557c757c3eae7595bca2a581b4dc9704ee` |
| 1 | 3876 | 380852 | `d829aa5e39c32a1b89dfc0026d21cb52636c142463ce2579adc7a375b7dc5dfd` |
| 2 | 2116 | 272068 | `4a134dc7d6d67bbf2474adbc1a5ecfa6544c7aa07f6e4376d71dbff6d943fbe7` |
| 3 | 528 | 165380 | `458f77d63a7fcb3ba69b826b421fe409950e7b3f7ed5af22ff06964044578ada` |

Each LOD preserves29meshes and18anchor transforms. `optimized.glb` equals LOD0. Four visual LODs and collider pass Khronos validation with zero errors and warnings. Budgets15,000triangles/3MB. Full measurements: `reports/assets.json`.

## Evidence
Generation, eight renders, structural validation and saved source edit job `2df37aab-f2ca-4bf3-b4ae-7fb0cbba6295` succeeded. Three focused tests, build and Gallery job `51c95eff-a627-4a60-9608-69a27eb8be36` succeeded. Logs `reports/*-01.log`; browser results `reports/browser/results.json`.

Checks include actual curved front intersection at seven X locations per LOD, measured bulge, less than8mm deviation from the analytic curve, matching curved LED support, full nine-point product footprint support, vertical clearance, 4mm visible lining separation, lining/pillar and board/back/side contacts, header visibility, finite UV/normals, stable names and anchors. Saved blend was independently edited, saved/reopened and exported without regeneration, with original source hash unchanged. Keep `reports/source-edit/edited.glb` and editedblend as required test evidence.

All eight PNG previews were actually inspected: arc readable in side/detail views, complete back, consistent reduced-LOD silhouette, no visible coplanar stripes or floating LEDs. The 384px WebP was decoded and visually inspected (11500bytes). Full PNGs remain; catalog uses only lightweight WebP.

Gallery1440/768/390 checks validate actual consumedGLB SHA, rendering, orbit/zoom/reset, close/reopen and teardown. Actual1440/390initial screenshots were visually inspected. These are Chromium viewport tests, not physical Android/iOS tests.

## Integration limits
`support-manifest.json` exposes three single-board rows, five LEDnodes and the1.92×0.36m frontheader surface. Inspector supports three row highlights, five LED strips, one concept header, four manual LODs and reset. No automaticLOD, product loading or physical-device claim. Existing558assets and collection objects preserved; onlyM062added (`reports/catalog-preservation.json`). Rights/provenance: `LICENSE.md` and metadata.

Integrated seven-fixture local evidence: `../../docs/shelf-inspector-m061-m062-qa.md`. No remote CI, publication or real-device claim.

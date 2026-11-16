# Mall event booth topology repair

Status: PASS. Exact-zero triangles: 118 → 0. Eight reviewed positive-area precision residues were also removed. Total triangles: 4,632 → 4,506; byte length remains 215,640. Canonical vertex positions, normals, material definitions, bounds, node hierarchy/pivots and other buffer payloads are retained through index reconstruction. Existing previews remain applicable.

The source preserves all 28 editable parts and three named collection modules. Four reviewed poster meshes and all three text objects use non-destructive cleanup. Source fingerprints and saved-source reopen pass. The existing joined-module bevel evaluation remains the export contract; disposable copies remove per-part cleanup before the legacy merge, then clean the evaluated module. DisplayContent explicitly uses Clip to retain its sample cylinder cap diagonals. A Beauty attempt added 18 unmatched triangles and was rejected without weakening surface checks.

Native re-import exposed two additional ~7nm font strips: they had positive Float64 GLB area but collapsed after Float32 world translation. Baking translations only on disposable export copies before cleanup removes those precision residues. Authored transforms and canonical GLB pivots stay intact. Actual canonical re-import and the complete fresh generation/export/re-import regression now report zero degenerate triangles.

- [Pre-fix regression](regression-before.log), [rejected cap triangulation](rejected-cap-triangulation.json), [Float32 collapse diagnosis](float32-reimport-before.json)
- [Source preservation](source-repair.json), [strict source export comparison](source-geometry-comparison.json)
- [Index repair](index-repair.json), [strict canonical comparison](delivery-comparison.json), [actual canonical re-import](delivery-reimport.json)
- [Fresh generator/export/import regression](generator-regression.log), [real saved-source edit execution](edit-execution.json)
- [Source edit verification](../../../../models/mall-event-booth/reports/source-edit.json), [verification](verification.json), [browser cases](browser-results.json)

691 tests and the build passed. The real saved-source YOUR STORY → NEW STORY edit changes only PosterPanel against an unchanged same-toolchain control. BoothStructure and DisplayContent retain geometry/indices/normals/transforms/material hashes. Shipped source/GLB hashes remain unchanged by that test, and all three actual GLBs are clean. Independent hide/replacement tests still isolate both poster and display modules.

All three browser widths passed (1440/768/390), checking consumed SHA, WebGL render, orbit/zoom/reset and no network/page/console errors or overflow. The actual desktop capture was inspected: poster headline/art, wings, walnut counter and display content remain intact. These results do not establish physical-device performance or deployment.

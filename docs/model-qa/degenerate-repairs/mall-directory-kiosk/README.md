# Mall Directory Kiosk degenerate geometry repair

Second asset in the active [campaign](../README.md), 2026-11-15. The first trash-bin repair was separately published as `fc4f24aa`.

## Result

- Exact zero-area delivered triangles: **394 → 0**. Total triangles: **5,360 → 4,940**. File size remains **178,068 bytes** because original vertex payloads and buffer allocation are preserved.
- Also removed **26 source precision residues**, each collinear at 1e-6 m quantization and with altitude at most **5.76e-8 m** (below the explicit 1e-7 m weld tolerance). They are counted separately from exact-zero geometry. A small area alone is not permission to remove a face.
- The actual delivery retains all remaining original oriented/material faces, vertex attributes, shading normals, material definitions, bounds and root transform. Maximum matched vertex displacement and changed normal triangles are both **zero**.
- The source reopens in Blender 5.1.2 with **23 editable parts**, including its original text, route curve, mesh data, material inputs and scene placement. Fourteen reviewed thin beveled parts/text receive non-destructive evaluated cleanup. Original data is not flattened, and evaluated geometry is free of degenerates.

## Cause and independent controls

Thin beveled housings, map/shop blocks, category tiles, ventilation strips and service covers contain clamped duplicate corners; the DIRECTORY text also has collapsed outline triangles. The same explicit cleanup hook runs during future generation.

A re-export of the unchanged source reproduced the 394 zeros. Its Float32 evaluation shifted a few vertices across a quantization boundary; quantized hashes alone incorrectly reported lost/added surfaces even though displacement was under one micrometre. A frozen regression using a valid **0.75-micrometre** translation reproduces that checker failure. The comparator now pairs unmatched oriented triangles by actual cyclic vertex distance within the original **1e-6 m** tolerance. It checks the full Euclidean displacement, including exact-hash candidates. Independent negative controls still reject a genuine 10-micrometre face deletion, flipped normals and a displacement beyond tolerance hidden inside the same quantization cell.

The cleaned native export matches the original material surfaces within a maximum **2.384e-7 m** positional difference; its normals can vary with the Blender exporter version. The committed GLB instead reconstructs original index streams against that reviewed source geometry, retaining all vertex/shading bytes. No vertex movement or shading drift is introduced into the delivered model.

## Evidence

- [Saved source and reopen](source-repair.json), [unchanged-export control](unchanged-export-control.json), [cleaned source geometry](source-geometry-comparison.json).
- [Index repair](index-repair.json), [independent delivered comparison](delivery-comparison.json).
- [Asset regression before](regression-before.log), [focused checks after](focused-after.log).
- [Comparator boundary regression before](comparator-before.log), [after](comparator-after.log). This failure is retained separately from the asset defect. Fixture min/max bounds are recomputed from actual Float32 positions so Khronos validation cannot mask the intended comparator test.

## Verification

[Final verification](verification.json): 676 full tests pass; 8 focused checks pass after the final comparator guard changes. Both native generator cases pass. Build and built-asset SHA-256 pass; the existing chunk-size advisory remains. Khronos reports zero errors/warnings. [Actual GLB re-import](delivery-reimport.json) confirms zero degenerates. [Browser results](browser-results.json) pass 15/15 across 1440/768/390, including consumed GLB SHA, render, orbit, zoom, reset, reload and close/disposal. [Desktop](viewer-1440.png) was visually inspected; [narrow viewport](viewer-390.png) is also retained.

## Reproduce

Use the same commands as the [trash-bin workflow](../mall-trash-bin/README.md#reproduce), substituting `mall-directory-kiosk`. Retrieve its original source/GLB from main `fc4f24aa1662c89182ece1f8d07b7fc1984d3de0`; the source migration validates the exact supplied SHA-256 before opening it. Use distinct, new stage/output paths. The source geometry comparison alone permits exporter normal drift; the final delivered comparison requires retained normals.

The other fixture sources/GLBs, existing previews, category/rights and runtime UI remain unchanged. This is geometry repair, not a new functional wayfinding screen. Physical-phone/FPS, certification and deployment acceptance are outside these checks. Text log trailing whitespace is normalized for publication.

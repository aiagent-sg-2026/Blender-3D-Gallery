# Mall Advertising Lightbox degenerate geometry repair

Third separately verified asset in the active [campaign](../README.md), 2026-11-15. The previous directory-kiosk repair was published as `576c07b7`.

## Result

- Exact zero-area GLB triangles: **200 → 0**. Total: **7,168 → 6,968**. No additional positive-area precision residues are removed.
- File size remains **235,832 bytes** because original vertex payloads and buffer allocation are preserved. This is topology repair, not a size optimization.
- Every remaining original oriented/material triangle, vertex position, shading normal, material definition, emissive value, bounding box and root transform is unchanged in the delivery. Independent comparison reports **zero vertex displacement and zero changed normal triangles**.
- All **18 authored parts** remain editable in the saved Blender 5.1.2 source. Original mesh data, text and material graphs are preserved. Eight reviewed parts receive the explicit non-destructive cleanup modifier. Reopening the source confirms zero degenerate evaluated triangles.

## Cause and method

Thin poster/frame/service-panel geometry and shallow campaign shapes contain clamped bevel corners; two text outlines also have collapsed triangles. The source now has the same reviewed triangulate/weld/exact-zero-delete stage used by the earlier assets, including future generation. The delivery reconstructs only original triangle indices against independently checked source geometry, retaining authored normal and emissive payloads. The source geometry oracle matches within the fixed 1e-6 m vertex-distance tolerance; its exporter-specific shading is not used to overwrite the original delivery.

## Evidence

- [Source repair and reopen](source-repair.json), [source geometry comparison](source-geometry-comparison.json).
- [Index reconstruction](index-repair.json), [independent delivered comparison](delivery-comparison.json).
- [Actual GLB regression before](regression-before.log): fails with 200 zeros. The same real-asset check passes after repair.

## Verification

[Final verification](verification.json): 677 tests and all three native generator cleanup cases pass. Build and built-asset SHA-256 pass; existing chunk-size/timing advisories remain. Khronos reports zero errors/warnings. [Actual delivered GLB re-import](delivery-reimport.json) confirms zero degenerates. [Browser checks](browser-results.json) pass 15/15 across 1440/768/390, covering the collection and consumed GLB SHA, render, orbit, zoom, reset, reload and close/disposal. [Desktop](viewer-1440.png) and [narrow viewport](viewer-390.png) captures are retained; the actual desktop Viewer capture was visually inspected.

## Reproduce

Use the [documented migration/check workflow](../mall-trash-bin/README.md#reproduce) with asset ID `mall-advertising-lightbox`. Retrieve the original source and GLB from main `576c07b7afc60e500c2bebb98d9383c25ff31891`; the source migration requires the exact supplied input SHA-256 and a distinct empty stage. Default final-delivery comparison requires unchanged normals. Native geometry comparison alone explicitly allows exporter normal drift.

Existing previews, the other fixtures' sources/GLBs, original rights/category and runtime UI are unchanged. No physical-device/FPS, deployment, certification or functional advertising-screen behavior is claimed. Text-log trailing whitespace is normalized for publication.

# Mall Waste Sorting Station degenerate geometry repair

Fourth separately verified asset in the active [campaign](../README.md), 2026-11-15. The advertising-lightbox repair was separately published as `ea9ed618`.

## Result and source preservation

- Exact zero-area delivery triangles: **199 → 0**. Total: **11,508 → 11,300**. Nine additional source precision residues are reported separately and satisfy the explicit 1e-7 m altitude limit plus collinearity at 1e-6 m quantization.
- All remaining original delivered oriented/material surfaces, vertex positions, shading normals, material definitions, bounds and root transform are retained. Maximum delivered position/normal displacement is zero. Allocated vertex payloads remain; this is not a file-size optimization.
- The real source is a **Collection root**, with **59 editable objects** in seven module collections. Original meshes, FONT data, materials, transforms, selection and collection membership/properties are fingerprinted before/after and after reopening. Seven reviewed thin meshes and all eleven editable text objects receive non-destructive cleanup. Text cleanup also handles future label edits.
- The source's Float32 world evaluation reports 195 exact-zero triangles before cleanup and zero after reopening. The delivered GLB's separate Float64 position/transform calculation reports 199 before; these arithmetic paths are observations with distinct scopes and must not be added together.
- The actual final GLB re-imports in Blender with 11,300 triangles and zero degenerates. Its seven independent module nodes and all three open apertures/liner bottoms remain covered by the existing geometry/raycast/replacement regressions.

## Shared indices and source edits

The original GLB shares two index accessors across multiple module/material primitives. Their deletion masks are identical and empty; they are not defective streams. A frozen shared-index fixture reproduced the earlier tool's unnecessary rejection. Index reconstruction now permits shared accessors only when every encountered use has exactly the same retained index list, and writes each stream once. A separate fixture with incompatible per-mesh masks must fail before writing an output. Actual module uses and masks are retained in [the review](shared-index-review.json).

The real saved-source edit driver exports an unchanged native control and a separately saved **RECYCLE → PLASTIC** edit with Blender 5.1.2. The same toolchain comparison proves that only `RecycleLid` changes; six siblings retain identical geometry attributes, indices, normals, transforms and material hashes. All three GLBs (shipped, control, edited) must be free of exact-zero triangles. Original shipped source/GLB hashes remain unchanged. The canonical delivery preserves original packing/shading, so its cross-version buffer layout is deliberately distinguished from the causal edit comparison. `--no-render` suppresses only preview rendering during these real exports.

## Evidence

- [Fresh collection-root inspection](source-inspection-before.json), [source repair/reopen](source-repair.json), [source geometry oracle](source-geometry-comparison.json).
- [Delivered index reconstruction](index-repair.json), [independent final comparison](delivery-comparison.json), [actual GLB re-import](delivery-reimport.json).
- [Original exported-asset failure](regression-before.log), [shared-accessor failure](shared-regression-before.log), [tool controls after](tool-controls-after.log).
- [Fresh generator and actual generated-GLB regression](generator-regression.log); [real edit execution/hashes](edit-execution.json). Current source-edit group results also live in the collection's `reports/source-edit.json`.

## Verification

[Final verification](verification.json): 680 tests pass, including aperture raycasts, independent module replacement and real saved-source editing. Fresh generation and its actual exported GLB are clean. Build and built-asset SHA pass; the existing chunk-size advisory remains. Khronos reports zero errors/warnings. [Browser results](browser-results.json) pass all 3 widths (1440/768/390) with consumed GLB hashes, render, orbit, zoom, reset, no page overflow or errors. [Desktop](viewer-1440.png) was visually inspected; [narrow viewport](viewer-390.png) is retained. [Source-edit verification](source-edit-verification.json) records the real controls. A fresh 62-asset raw GLB scan confirms eleven other affected assets remain.

## Reproduce

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 23 --python models/mall-waste-sorting-station/test_degenerate_cleanup.py
node models/mall-waste-sorting-station/validate.mjs
blender --background --factory-startup --disable-autoexec --python-exit-code 23 --python models/mall-waste-sorting-station/test_source_edit.py -- /absolute/new-isolated-edit
node models/mall-waste-sorting-station/verify_source_edit.mjs /absolute/new-isolated-edit
npm test
npm run build
MALL_QA_DIR=/absolute/new-browser-evidence node scripts/test-mall-waste-sorting-station.mjs
```

For exact canonical migration, retrieve the old source/GLB from main `ea9ed61873cd88c02436bf590c06c3e55df9d78a`. Run `models/mall-waste-sorting-station/repair_degenerates.py` with `--input ORIGINAL.blend --expected-sha256 HASH --output NEW_STAGE`, then use the shared source-comparison, index-repair and strict delivered-comparison commands documented in the [first repair](../mall-trash-bin/README.md#reproduce). The native source geometry comparison alone allows exporter normal drift; canonical delivery comparison requires retained normals.

Existing previews, original category/rights, runtime UI and other assets are unchanged. This remains a static decorative sorting concept; no live sorting, physical-device/FPS, certification or deployment acceptance is claimed. Text log trailing whitespace is normalized for publication.

After integrating unrelated upstream model/documentation work, the 680-test suite and build passed again. Repair source/GLB hashes and application/runtime dependencies were unchanged. Later unrelated documentation-only updates are reviewed separately before the fast-forward push.

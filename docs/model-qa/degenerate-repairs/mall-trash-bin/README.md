# Mall Trash Bin degenerate geometry repair

Completed geometry verification on 2026-11-15. This is the first of the 15 remaining assets in the [campaign](../README.md).

## Result

- Exact zero-area delivered triangles: **470 → 0**. Delivered triangles: **8,088 → 7,616**. File size stays **338,232 bytes** because vertex payloads and buffer allocation are deliberately preserved.
- Two additional source precision residues were removed: their positive double-precision areas are approximately 7.39e-11 and 3.07e-11 m², but altitudes are below the explicit 1e-7 m weld tolerance and their coordinates are collinear at 1e-6 m quantization. They are reported separately from the 470 exact zeros.
- All remaining oriented/material triangles match at 1e-6 m positional quantization. All original delivered vertex positions, normals, other attribute bytes, material definitions, dimensions and asset-root transform are retained. The independent comparison finds **zero changed shading-normal triangles**.
- The saved Blender 5.1.2 source keeps all **32 editable parts**, including its original mesh data, modifier settings, materials, object placement and editable Bfont labels. Six reviewed parts receive an explicit non-destructive cleanup modifier. The source reopens with zero degenerate evaluated triangles. The actual delivered GLB separately re-imports with 7,616 triangles and zero degenerates.

## Cause and method

The source lathe emits collapsed full rings at zero radius, the clamped badge bevel contains effectively coincident points, and the two font outlines generate collapsed triangles. The reviewed cleanup modifier triangulates before welding so existing quad diagonals are retained, merges within 0.1 micrometre and deletes exactly zero-area evaluated faces. Original authoring data remains editable; the base meshes/curves are not destructively flattened. The same hook is part of future trash-bin generation.

A controlled re-export without geometry repair reproduces all 470 zeros and also changes 4,668 triangles' shading normals when moving from the original Blender 4.0.2 export to 5.1.2. Therefore the committed delivery is reconstructed from the original GLB's index streams, keeping its authored shading and all other binary payload bytes. The native cleaned export is used as a geometry oracle, not as an excuse to overwrite the original shading. This intentionally preserves allocated vertex data; it is not a size optimization.

## Evidence and checks

- [Native source repair and reopen](source-repair.json), [unchanged-export control](unchanged-export-control.json), [source geometry comparison](source-geometry-comparison.json).
- [Delivered index reconstruction](index-repair.json), [independent final GLB comparison](delivery-comparison.json), [Blender GLB re-import](delivery-reimport.json).
- [Original regression failure](regression-before.log): actual GLB fails with 470 zeros. [Focused checks after](focused-after.log): 7/7 pass. The tool controls also reject deletion of a real 10-micrometre face and reject flipped normals, even though the face has a tiny area.
- Native generator cleanup regression passes with authored data unchanged and no duplicate modifier on repeat use. `npm test` passes 675/675; build and built-GLB SHA-256 pass. Khronos validation is zero errors/warnings. [Final verification](verification.json).
- [Browser results](browser-results.json): 15/15 on Chromium 156.0.8078.4 / SwiftShader, including the four-fixture collection at 1440/768/390. Actual consumed GLB hashes, render, orbit, zoom, reset, reload and close/disposal are checked. [Desktop capture](viewer-1440.png), [narrow viewport](viewer-390.png). The desktop capture was visually inspected. Physical phones/FPS and deployment are not claimed.

## Reproduce

Run the native regression and delivery checks from the repository:

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 23 --python models/mall-essentials/test_degenerate_cleanup.py
node models/mall-essentials/validate.mjs
node --test tests/glb-degenerate-tools.test.mjs tests/mall-degenerate-repairs.test.mjs tests/mall-essentials.test.mjs
npm test
npm run build
MALL_QA_DIR=/absolute/fresh-evidence node scripts/test-mall-essentials.mjs
```

For exact shading-preserving migration, retrieve the original GLB and `.blend` from main commit `1e94207991e702451ce931d3f76d30925a903453`. The original source SHA-256 is `d6040540b0963d8d6d838680051dfd59519f579f2f5a7b33e559bff8fb667748`. Pass the original source to `models/mall-essentials/repair_degenerates.py` using `--id mall-trash-bin --input ORIGINAL.blend --expected-sha256 HASH --output EMPTY_STAGE`. Then:

```sh
node scripts/check-degenerate-repair.mjs ORIGINAL.glb EMPTY_STAGE/mall-trash-bin.glb SOURCE_COMPARISON.json --allow-normal-drift
node scripts/repair-glb-degenerates.mjs ORIGINAL.glb DELIVERY.glb INDEX_RECEIPT.json SOURCE_COMPARISON.json
node scripts/check-degenerate-repair.mjs ORIGINAL.glb DELIVERY.glb FINAL_COMPARISON.json
```

The explicit normal-drift option is used only for the native geometry oracle; final delivered comparison requires preserved normals. Positive-area residues must both collapse at the stated position quantization and have altitude at most the weld tolerance. A small area alone never qualifies. Existing previews, the other fixture GLBs/sources and all unrelated project work are unchanged. Text-log trailing whitespace was normalized for publication.

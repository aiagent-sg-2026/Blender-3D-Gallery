# TV Demo Table

Original, brand-neutral static retail asset for GJH Virtual Mall stores S13/S14, priority P1. Category: existing **Equipment**. Status: draft / **NEEDS REVIEW** pending manager art review. No external geometry, images, textures, fonts, logos, packaging or readable text.

The 2 × 1 m table has a measured 0.80000001 m worktop, a 0.25200000 m lower shelf, three small blank 16:9 screens on riser stands, a recessed graphite edge strip, a blank sign card and covered rear cable routes. Total exported size: 2 × 1.36500001 × 1 m (width, height, depth). The source keeps 62 editable mesh parts. Export bakes their saved modifiers and batches by material into three meshes and three primitives: 6,696 triangles, 245,228 bytes, three opaque shared materials, no textures or animation.

Metres; origin at floor centre of the table footprint. Authoring: Blender +Z up / -Y front. Export: glTF +Y up / +Z front. Studio floor, camera and lights are excluded from GLB. Source parts remain separate; export preserves saved edits and does not modify the source.

From the repository root:

```sh
/opt/homebrew/bin/blender --background --python models/tv-demo-table/generate.py
node models/tv-demo-table/validate.mjs
/opt/homebrew/bin/blender --background --python models/tv-demo-table/inspect_sources.py
node models/tv-demo-table/verify_source_edit.mjs
npm run validate:assets
npm test
npm run build
node models/tv-demo-table/verify_page.mjs
```

Generator options after `--`: `--skip-render`, `--views=hero,front,side,3q,rear`, or `--export-source` to export the saved `.blend` without rebuilding. Rebuilding overwrites this asset's source/export/previews. Source inspection creates ignored disposable edit copies in `reports/source-edit/`.

Evidence: [measured GLB](reports/assets.json), [Khronos](reports/khronos.json), [source checks](reports/sources.json), [clean rebuild](reports/reproducibility.json), [duplicate search](reports/duplicate-search.json), [acceptance](reports/acceptance.json). Existing `tv-floor-stand`, `desktop-monitor` and ordinary tables have different roles and were preserved. No existing TV demo table was found.

Static visual prop: no video playback, electrical behavior or interactive screen controls. The asset's three primitives do not establish a complete mall's 200 draw-call budget or physical-device performance. Physical Android/iOS, WebKit, full 17-shop assembly, structural load/stability and remote deployment are unverified. No push or release is included.

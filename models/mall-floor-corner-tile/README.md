# Mall corner floor tile — 1.2 m outside corner

A complete square floor module for a 90° outside corner. It reuses the existing mall floor's original terrazzo artwork, four-slab pattern, 1.2 m pitch and 30 mm depth, with two 20 mm champagne-coloured inlays on the outside edges. The module is a decorated square tile, not an L-shaped or inside-corner floor section.

## Assembly

- GLB is **1.2 × 0.03 × 1.2 m** (X/Y/Z), origin at the bottom centre. Blender Z is up; GLB Y is up. Place its root at `(0, -0.03, 0)` to put the finished top at Y=0. The inlays face GLB +X and +Z.
- Straight floor neighbours sit at `(-1.2, -0.03, 0)` and `(0, -0.03, -1.2)`. The [mitred trim pair](../mall-floor-mitred-trim/README.md) sits at `(0, 0, 0)`; it replaces the two terminal straight trims and square corner cap in this arrangement.
- Each slab, filled joint, inlay and support is editable in the Blender source. This is visual asset geometry, not a fabrication, collision or safety specification. Original project geometry and texture; public redistribution terms are unspecified. Gallery download is disabled.

## Local verification

Blender 5.1.2 reopened the source and reimported the GLB, with source/reimport bounds matching within 0.1 mm: [report](reports/source-reimport.json). The **162,152-byte, 528-triangle GLB** (`SHA-256 8d370fea8c516d50ae13e9907fa6b8d06ec754f6477fbb1dad53177d7685ad36`) has **0 errors and 0 warnings** in Khronos glTF Validator. [Assembly validation](reports/validation.json) checks actual GLB bounds, neighbour alignment and top-surface samples on the adjacent mitred pair. It covers one 90° outside layout, not all triangle intersections, configurations, target devices or construction safety.

The local [corridor preview](../../mall-modules-preview/) places the tile at the front-right corner and provides an individual view. The project backlog's proposed 2 m dimensions remain unresolved.

## Source

The reproducible generator is [generate.py](generate.py). It builds both this tile and the accompanying trim, and **refuses to overwrite existing Blender sources**. Run on a clean copy or after preserving the sources; it writes both GLBs and renders. Independently recheck with `node models/mall-floor-corner-tile/validate.mjs` and `blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python models/mall-floor-corner-tile/inspect-sources.py`.

Local Chromium rendered this GLB in the Gallery at 1440 × 900 and emulated 390 × 844; the runtime bytes matched the documented hash, the viewer closed cleanly, and no normal-flow browser errors were observed. [Desktop](reports/gallery-desktop.png) · [mobile](reports/gallery-mobile.png). Physical devices remain untested.

# Mall mitred floor trim — 90° outside corner

A pair of straight champagne-finish edge profiles joined along a 45° mitre, supplied as one GLB with separate editable front/right cap and support meshes. Each profile is 60 mm wide and 30 mm high, matching the existing straight edge trim. The pair's outside bounding footprint is **1.26 × 1.26 m**, measured in GLB X/Z.

## Assembly

With the [corner floor tile](../mall-floor-corner-tile/README.md) at `(0, -0.03, 0)`, put this pair at `(0, 0, 0)`; its top is at finished floor level. Its diagonal joint runs from GLB `(0.60, 0, 0.60)` to `(0.66, 0, 0.66)`. Continue existing straight trims at `(-1.2, 0, 0.63)` and `(0.63, 0, -1.2)`, rotating the latter 90° around Y. The pair replaces the two end strips **and** the square corner cap; do not overlap them.

Original geometry and project-owned materials. Gallery download is disabled because public redistribution terms have not been specified. This is a decorative outside corner; inside corners, structural performance, installation and safety are outside its scope.

## Local verification

Blender 5.1.2 source/reimport bounds agree within 0.1 mm: [report](reports/source-reimport.json). The **5,644-byte, 48-triangle GLB** (`SHA-256 27e9cf16c0693f50e5090e81f1f7f54d0f1a5b22ea0f1b6b9926ae198f4b3203`) has **0 errors and 0 warnings** in Khronos glTF Validator. [Assembly validation](reports/validation.json) checks one 90° layout against actual tile and straight-trim GLBs and probes each side of the diagonal on the exported mesh. This is not exhaustive intersection, collision or target-device testing.

The [local corridor preview](../../mall-modules-preview/) uses this pair at its front-right corner; the previous square cap remains individually selectable. Generator and verification commands are in the [corner tile README](../mall-floor-corner-tile/README.md).

Local Chromium rendered this GLB in the Gallery at 1440 × 900 and emulated 390 × 844; the runtime bytes matched the documented hash, the viewer closed cleanly, and no normal-flow browser errors were observed. [Desktop](reports/gallery-desktop.png) · [mobile](reports/gallery-mobile.png). Physical devices remain untested.

# Mall floor edge trim — 1.2 m

An original static straight trim for the owner's mall floor. It reuses the existing floor's 1.2 m pitch and 30 mm depth. This is a visual edge strip, not a completed corner/miter, general floor transition, or the user-provided backlog's unreviewed provisional dimensions.

## Contract

- Dimensions **1.20 m long × 0.06 m deep × 0.03 m high**. Blender +Z up, GLB +Y up; the origin is top centre at finished floor height. Two editable source meshes form the dark base and champagne-coloured cap.
- For the existing floor at GLB root `(0, -0.03, 0)`, place the trim root at `(0, 0, 0.63)`; its edge touches the floor's Z=0.60 boundary, with matching top height. Repeat trim roots at 1.2 m X increments.
- No corner join, mitre, collision proxy, animation, texture, real light, slip rating, installation, fabrication or engineering certification is supplied. Its edge placement is a visualization convention, not a building detail.
- Original owner-project geometry and materials; no external artwork. Public redistribution terms are unspecified. Gallery download is disabled.

## Verification — 2026-11-15

- Blender 5.1.2 reopened the source with two editable meshes. Clean GLB reimport preserved the source bounds and top-centre level: [source/reimport results](reports/source-reimport.json).
- Actual GLB: **4,188 bytes, 24 triangles, two materials**; SHA-256 `f327fbd76b5d722dfc21c52563c28e2ec96b7ff08b48b425de422a492215b3db`. Khronos validator reported **0 errors / 0 warnings**. Three.js checked the 1.2 m repeat and alignment with the existing floor's edge and top using bounding boxes: [validation results](reports/validation.json).
- A fresh Chromium Gallery loaded the matching actual GLB hash and produced WebGL draws at 1440 × 900 and emulated 390 × 844. Downloads were hidden, no normal-flow browser errors occurred and viewer close removed the canvas. [Desktop screenshot](reports/gallery-desktop.png), [mobile screenshot](reports/gallery-mobile.png). The corridor preview loaded with this strip in the front edge.

**Related work:** the separate [mitred outside-corner pair](../mall-floor-mitred-trim/README.md) connects to this straight strip in one checked 90° arrangement. Floor-transition design, full triangle contact and multi-module assembly review, target-device performance and physical Android/iOS remain open. Local registration and the visual preview do not establish release or safety approval.

## Reproduce

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python models/mall-floor-edge-trim/generate.py -- --export-source
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 2 --python-exit-code 1 --python models/mall-floor-edge-trim/inspect_source.py
node models/mall-floor-edge-trim/validate.mjs
```

`--export-source` preserves the saved source but overwrites the GLB and PNG. The generator refuses to overwrite an existing source without explicit `--rebuild`; preserve manual changes before rebuilding. Refresh the JPEG and metadata hashes after intentional changes.

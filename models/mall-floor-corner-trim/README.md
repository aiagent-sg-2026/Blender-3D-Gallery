# Mall floor corner trim — outside 90° cap

A static 60 mm square corner cap for the existing 1.2 m mall floor and straight edge trim. The cap fills the square between two perpendicular straight strips; it is a **square cap**, not a mitred strip or a complete corner floor tile.

## Assembly contract

- Dimensions: **0.06 × 0.03 × 0.06 m** in glTF X/Y/Z. The origin is top-centre at finished floor height. Blender +Z maps to glTF +Y. Two editable source meshes provide the matching dark support and champagne cap.
- In glTF metres, put the existing floor at `(0, -0.03, 0)`, a straight trim at `(0, 0, 0.63)`, another at `(0.63, 0, 0)` rotated 90° about Y, and this cap at `(0.63, 0, 0.63)`.
- This is one outside 90° arrangement. Inside corners, other angles, varying trim profiles and collision or navigation are not included. No slip, safety, fabrication or installation certification is implied.
- Original owner-project geometry and materials; no external artwork. Public redistribution terms are unspecified. Gallery download is disabled.

## Local verification — 2026-11-15

- Blender 5.1.2 reopened the editable source and reimported the actual GLB with matching bounds: [source/reimport report](reports/source-reimport.json).
- The GLB is **4,344 bytes, 24 triangles**, SHA-256 `913bb6aa74b5a13145af09767c26beb73b71b5d92eaff4a7e2f53f294af36582`. Khronos glTF Validator reported **0 errors / 0 warnings**. Three.js checked the two trim-to-cap contacts and five top-surface ray samples on actual GLBs: [corner validation](reports/corner-validation.json).
- Local Chromium Gallery loaded the exact GLB hash and rendered WebGL at 1440 × 900 and emulated 390 × 844 with no normal-flow browser errors. Viewer close removed its canvas and downloads remained hidden: [desktop](reports/gallery-desktop.png), [mobile](reports/gallery-mobile.png). The corridor preview includes the cap at its front-right corner.

These are checks of a single outside-corner arrangement, bounding boxes and sample rays, not proof of every triangle intersection, target-device performance or physical Android/iOS support. The 400-item backlog's 2 m floor-corner dimensions remain provisional and are not automatically fulfilled.

## Reproduce

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python models/mall-floor-corner-trim/generate.py -- --export-source
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 2 --python-exit-code 1 --python models/mall-wall-corner/inspect-sources.py
node models/mall-wall-corner/validate-corners.mjs
```

`--export-source` retains the saved source but overwrites the GLB and PNG; `--rebuild` replaces the source. Preserve manual edits first and update JPEG/metadata hashes after intentional changes.

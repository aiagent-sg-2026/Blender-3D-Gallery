# Mall solid wall — 1.2 m module

An original, static architectural module for the owner's shopping mall, made with Blender 5.1.2. It is locally registered as `mall-solid-wall`; it is not a completed acceptance of the user-provided `MALL-STR-010` 2.0 × 0.15 × 2.8 m provisional specification. This version follows the existing 1.2 m floor/ceiling grid and 3 m column height.

## Contract

- Dimensions: **1.20 m wide × 0.12 m deep × 3.00 m high**. Blender uses Z-up; the GLB uses Y-up. The origin is the bottom centre and the front is Blender −Y / glTF +Z.
- Repeat on 1.2 m centres. Connector nodes are at local X −0.60 and +0.60 m. A continuous core reaches the edge; the three front panel strips sit within that core's edges. No end, corner, doorway, collision shape or editable runtime behavior is supplied.
- Six independently editable source meshes: one solid core, three decorative panels, upper trim and skirting. The GLB has three materials, no external image/URI, no camera, light or animation.
- Original geometry and materials were created for the owner's project. Public redistribution terms have not been specified. Gallery download stays disabled.
- This visual model is not a structural, acoustic, fire, accessibility, installation or construction specification.

## Verified locally — 2026-11-15

- Blender reopened the actual `.blend` with six meshes; a clean GLB reimport had matching dimensions and ground origin: [source and reimport results](reports/source-reimport.json).
- The actual 29,676-byte GLB has 360 triangles and SHA-256 `4e42b9f7c84e5f769a5940485ef2af81ee667fc03579d56f4065788c4d840708`. Khronos glTF Validator reported **0 errors / 0 warnings**; Three.js measured correct Y-up bounds and two straight 1.2 m joins, with approximately 0.05 micrometre floating-point overlap: [validation](reports/validation.json). These are bounding-box checks, not full triangle/contact or arbitrary corner validation.
- A second Three.js check reused the existing floor GLB in an L-shaped five-module arrangement and aligned the wall to one floor module at finished-floor height: [floor/wall results](reports/floor-wall-assembly.json). This checks bounding boxes and four floor edges only; it does not supply or validate a finished corner trim.
- Actual GLB loaded in the local Gallery in Chromium at 1440 × 900 and emulated 390 × 844. Runtime bytes matched the GLB hash, real WebGL draws were observed, download was hidden, no normal-flow browser errors were seen, and closing the viewer removed its canvas. The local mall preview also loaded the individual wall and corridor. Desktop screenshot: [Gallery view](reports/gallery-desktop.png); mobile screenshot: [Gallery mobile view](reports/gallery-mobile.png).
- `node --test tests/catalog.test.mjs`: 6 passed. The card preview is a JPEG made from a Blender source render; viewer evidence above is the actual GLB.

**Still open:** representative assembled-wall fit against glazing, door frames, floor and ceiling; corner/transition fit; sustained device performance; physical Android/iOS; review of the original 2 m backlog variant; release and rights decisions. A local Gallery registration is not a deployment or production approval.

## Reproduce

From the repository root:

```sh
# Export the saved source and render it without rebuilding authored geometry.
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 4 --python-exit-code 1 --python models/mall-solid-wall/generate.py -- --export-source
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --threads 2 --python-exit-code 1 --python models/mall-solid-wall/inspect_source.py
node models/mall-solid-wall/validate.mjs
node models/mall-solid-wall/verify-assembly.mjs
node --test tests/catalog.test.mjs
```

The generator refuses to replace an existing source unless `--rebuild` is explicitly passed; that option overwrites the source, so preserve manual changes first. `--export-source` preserves source edits but overwrites the GLB and PNG render. Check artifact hashes and regenerate the JPEG/metadata if outputs change.

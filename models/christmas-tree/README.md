# Christmas Tree

F01 is an original stylized evergreen for the Festivals & Local Life gallery.
It has seven foliage layers, a gold star and garland, colored baubles and warm
emissive lights. The artwork is static; the gallery provides orbit, zoom and
reset. No external models, images, fonts or brands are used. Public
redistribution terms are unspecified, so the gallery download is disabled.

## Source and reproducibility

- `sources/christmas-tree.blend`: editable source, before export batching.
- `generate.py`: deterministic authoring and GLB export (Blender 5.1.2, seed 41).
- `exports/christmas-tree.glb`: standalone glTF 2.0, ornaments batched by
  material for fewer draw calls; source ornaments remain independently editable.
- `render.py`: creates `previews/hero.png` by reimporting the actual GLB;
  `previews/hero.webp` is the gallery thumbnail.
- `metadata/christmas-tree.json`: attribution, display settings and measured data.

From this directory, reproduce using Blender with `blender -b --python
generate.py` followed by `blender -b --python render.py`; convert the PNG to a
WebP thumbnail (the recorded thumbnail was made with `cwebp -q 83 -resize 480 0`).
Use only trusted project scripts. Review the result rather than assuming a new
Blender version will generate identical bytes.

## Local verification (2026-11-15)

- Khronos glTF Validator: 0 errors, 0 warnings; 1,015,308 bytes and
  34,944 triangles. Preview was rendered after reimporting the exported GLB.
- Full asset validation and production build passed on the F01 asset before
  incorporating the subsequent gallery-initialization fix; the final tree
  passed a fresh Vite production build. The intervening fix changed only
  `index.html` and `src/main.js`, not asset files or catalog.
- Project unit suite: 665 passed before that fix; catalog/registry tests: 18
  passed on the final tree. Desktop 1440×900 and emulated mobile 390×844
  Chromium checks covered search, lazy GLB loading, real WebGL draws, orbit,
  reset click, viewer close, console errors and horizontal overflow.
- Physical devices, screen readers, network error and no-WebGL fallback states
  were not tested for this asset. No deployment is claimed by these local checks.

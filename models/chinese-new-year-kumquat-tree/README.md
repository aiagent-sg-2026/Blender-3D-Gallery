# Chinese New Year Kumquat Tree

F05 is an original stylized potted kumquat tree for the Festivals & Local Life
collection. A glazed ceramic pot supports a branching tree with green leaves,
orange fruit and hanging red packets. It is a decorative interpretation, not a
botanical reference. The artwork is static; the gallery viewer provides orbit,
zoom and reset. Public redistribution terms are unspecified, so gallery download
is disabled.

## Source and reproducibility

- `sources/chinese-new-year-kumquat-tree.blend`: editable source, with separate
  pot, trunk, branches, individual leaves, fruit and red packets.
- `generate.py`: deterministic Blender 5.1.2 geometry and export, seed 509.
- `exports/chinese-new-year-kumquat-tree.glb`: standalone glTF 2.0. Evaluated
  export meshes are batched by material; the source remains independently editable.
- `render.py`: renders `previews/hero.png` from the reimported actual GLB;
  `previews/hero.webp` is the gallery thumbnail.
- `metadata/chinese-new-year-kumquat-tree.json`: attribution and measurements.

All geometry and materials are original; no external models, images, fonts or
brands were used. From this directory, run `blender -b --threads 2 --python
generate.py`, then `blender -b --threads 2 --python render.py`. The checked
thumbnail was made with `cwebp -q 83 -resize 480 0`. Use only trusted project
scripts and review output when using a different Blender version.

## Local verification (2026-11-15)

- Khronos glTF Validator: 0 errors and 0 warnings; GLB is 1,921,260 bytes with
  57,482 triangles, ten material batches and ten materials. The preview was
  rendered after reimporting the actual exported GLB.
- Reopened the Blender source and confirmed independently editable pot, soil,
  trunk, branches, 224 leaves, 36 fruits and seven red packets.
- `npm run build` passed, including full asset validation; `npm test` passed all
  665 tests. The build retains its existing large-chunk advisory.
- Chromium tests at 1440×900 and emulated 390×844 covered search, lazy GLB
  loading, actual WebGL draws, orbit, reset click, viewer close, console errors
  and horizontal overflow. A direct-link test also injected an HTTP 503,
  confirmed the descriptive poster and error message, and verified retry recovery.
- Physical devices, screen readers and no-WebGL fallback were not tested for
  this asset. Local checks do not establish deployment.

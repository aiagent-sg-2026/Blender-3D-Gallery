# Christmas Gift Boxes

F02 is a set of four original stylized wrapped presents for the Festivals & Local
Life gallery. Each has an independent box, lid, crossing ribbons and bow in the
Blender source. The static gallery model can be inspected with the existing orbit,
zoom and reset controls. There is no gift-opening animation. No external models,
images, fonts or brands are used. Public redistribution terms are unspecified,
so the gallery download is disabled.

## Source and reproducibility

- `sources/christmas-gift-boxes.blend`: editable Blender source.
- `generate.py`: original procedural authoring and GLB export, Blender 5.1.2.
- `exports/christmas-gift-boxes.glb`: standalone glTF 2.0; evaluated export
  meshes are batched by material while source objects stay separate.
- `render.py`: renders the actual reimported GLB to `previews/hero.png`;
  `previews/hero.webp` is the gallery thumbnail.
- `metadata/christmas-gift-boxes.json`: attribution and measured asset details.

From this directory, run `blender -b --threads 2 --python generate.py`, then
`blender -b --threads 2 --python render.py`. Convert the PNG to WebP; the checked
thumbnail used `cwebp -q 83 -resize 480 0`. Use only trusted project scripts and
review results when using a different Blender version.

## Local verification (2026-11-15)

- Khronos glTF Validator: 0 errors and 0 warnings; GLB is 1,039,580 bytes
  with 18,096 triangles, five material batches and five materials. The preview
  was rendered by reimporting the actual exported GLB.
- Reopened the saved Blender source and confirmed each of the four boxes has
  its own box, lid and two independently editable bow loops.
- `npm run build` passed, including the full asset validator; `npm test` passed
  all 665 tests. The build retains its existing large-chunk advisory.
- Chromium tests at 1440×900 and emulated 390×844 covered catalog search, lazy
  loading, actual WebGL draws, orbit, reset click, close, console errors and
  horizontal overflow. A direct-link test also injected an HTTP 503, confirmed
  the descriptive poster and error message, and verified retry recovery.
- Physical devices, screen readers, and the no-WebGL fallback were not tested
  for this asset. Local checks do not establish deployment.

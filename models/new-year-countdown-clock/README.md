# New Year Countdown Clock

F03 is an original, year-independent festive clock display for the Festivals &
Local Life gallery. The static face reads approximately 11:55, suggesting the
final minutes before midnight; it is not a live countdown or functioning clock.
The gallery viewer provides orbit, zoom and reset. Public redistribution terms
are unspecified, so the gallery download is disabled.

## Source and reproducibility

- `sources/new-year-countdown-clock.blend`: editable source with independent
  clock face, hands, numerals, twelve hour markers and framing stars.
- `generate.py`: procedural authoring and GLB export using Blender 5.1.2.
- `exports/new-year-countdown-clock.glb`: standalone glTF 2.0 with evaluated
  export meshes batched by material; source objects remain independent.
- `render.py`: creates `previews/hero.png` by reimporting the actual GLB;
  `previews/hero.webp` is the gallery thumbnail.
- `metadata/new-year-countdown-clock.json`: attribution and measured asset data.

All geometry and materials are original; numerals use Blender's bundled Bfont
converted to mesh. No external models or images are used. From this directory,
run `blender -b --threads 2 --python generate.py`, then `blender -b --threads 2
--python render.py`. The WebP thumbnail was created using `cwebp -q 83 -resize
480 0`. Use only trusted project scripts and review output from different Blender
versions.

## Local verification (2026-11-15)

- Khronos glTF Validator: 0 errors and 0 warnings; GLB is 845,684 bytes
  with 16,004 triangles, five material batches and five materials. The preview
  was rendered after reimporting the actual exported GLB.
- Reopened the Blender source and confirmed the face, both hands, four numeral
  meshes, twelve hour markers and framing stars remain separately editable.
- `npm run build` passed, including full asset validation; `npm test` passed all
  665 tests. The build retains its existing large-chunk advisory.
- Chromium tests at 1440×900 and emulated 390×844 covered search, lazy GLB
  loading, actual WebGL draws, orbit, reset click, viewer close, console errors
  and horizontal overflow. A direct-link test also injected an HTTP 503,
  confirmed the descriptive poster and error message, and verified retry recovery.
- Physical devices, screen readers and no-WebGL fallback were not tested for
  this asset. Local checks do not establish deployment.

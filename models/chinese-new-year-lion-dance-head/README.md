# Chinese New Year Lion Dance Head

F04 is an original, stylized southern Chinese lion dance head for the Festivals
& Local Life gallery. It features prominent painted eyes, curved brows, a horn,
forehead ornament, whiskers, open mouth, individual teeth, mane and beard. The
model is a creative interpretation rather than a reconstruction of a specific
troupe's costume. It represents only the head; the eyes and jaw are static.
The gallery viewer provides orbit, zoom and reset. Public redistribution terms
are unspecified, so the gallery download is disabled.

## Cultural context

Lion dance is performed in Singapore on auspicious occasions including Chinese
New Year; see [National Heritage Board's Roots article](https://www.roots.gov.sg/stories-landing/stories/High-Leaps-and-Clashing-Cymbals/Story)
and [Singapore Tourism Board's festival guide](https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/Q1-2016-Quarterly-Guide-Singapore-Insider.pdf).
The project concept board is an illustrative design reference, not an authentic
craft specification. This model does not claim to represent every lion dance
tradition or a particular historical object.

## Source and reproducibility

- `sources/chinese-new-year-lion-dance-head.blend`: artist-editable source;
  individual eyes, teeth, fur locks and decorative curves remain separate.
- `generate.py`: original procedural authoring and GLB export, Blender 5.1.2.
- `exports/chinese-new-year-lion-dance-head.glb`: standalone glTF 2.0 with
  evaluated export meshes batched by material.
- `render.py`: renders `previews/hero.png` from the reimported actual GLB;
  `previews/hero.webp` is the gallery thumbnail.
- `metadata/chinese-new-year-lion-dance-head.json`: attribution and measurements.

All geometry and materials are original. No external models, images, fonts or
brands were used. From this directory, run `blender -b --threads 2 --python
generate.py`, then `blender -b --threads 2 --python render.py`. Convert the PNG
to WebP; the checked thumbnail used `cwebp -q 83 -resize 480 0`. Use only
trusted project scripts and review output from different Blender versions.

## Local verification (2026-11-15)

- Khronos glTF Validator: 0 errors and 0 warnings; GLB is 1,146,920 bytes
  with 37,428 triangles, seven material batches and seven materials. The preview
  was rendered after reimporting the actual exported GLB.
- Reopened the Blender source and confirmed separately editable shell, eyes,
  pupils, forehead ornament, horn, mouth, muzzle, 7 teeth and 22 side mane locks.
- `npm run build` passed, including full asset validation; `npm test` passed all
  665 tests. The build retains its existing large-chunk advisory.
- Chromium tests at 1440×900 and emulated 390×844 covered search, lazy GLB
  loading, actual WebGL draws, orbit, reset click, viewer close, console errors
  and horizontal overflow. A direct-link test also injected an HTTP 503,
  confirmed the descriptive poster and error message, and verified retry recovery.
- Physical devices, screen readers and no-WebGL fallback were not tested for
  this asset. Local checks do not establish deployment.

# Basketball (Size 7)

Original, brand-neutral basketball. Category: Sports (browse: Parks & Recreation); pairs with the existing `basketball-hoop` asset. No external assets, fonts, text, logos or product markings.

Real scale: skin diameter 238.6 mm, circumference 749.6 mm (29.5 in, FIBA/NBA size 7). Eight panels in the standard layout: two perpendicular great-circle seams cross at the poles (Blender ±Z / glTF ±Y) and two curved "C" seams loop around the ±X sides, each crossing the X–Z belt seam twice. Channels are real recessed geometry: round 6 mm wide, 3 mm deep grooves cut with an exact Boolean, finished in a black rubber material. The pebbled grain on the orange rubber is a 2048×1024 tangent-space normal map baked in Cycles from 3D Voronoi bumps (seamless on the sphere) and embedded in the GLB as JPEG, so it survives glTF export. Static asset; no bounce or physics.

The `.blend` keeps the editable UV sphere `BALL_Shell` with its live Boolean modifier, the seam tube cutter `CUTTER_SeamChannels` (hidden) and the baked map at `sources/textures/basketball_pebble_normal.png`. Export evaluates the Boolean into a temporary triangulated copy (sliver cleanup, smooth-by-angle 35°), exports one mesh with two primitives/materials and leaves the saved source unchanged. Units are metres; the origin is the floor contact point under the ball centre; the GLB uses +Y up / +Z front (Blender +Z up / -Y front).

Run from the repository root:

```sh
blender --background --python-exit-code 1 --python models/basketball/generate.py
node models/basketball/validate.mjs
blender --background --python-exit-code 1 --python models/basketball/inspect_sources.py
npm run validate:assets
npm test
```

To export saved manual edits, append `-- --export-source --skip-render` to the generator command. To rebuild without rendering, append `-- --skip-render`. To render saved geometry only, append `-- --export-source --previews-only`.

`validate.mjs` writes `reports/khronos.json` and `reports/assets.json`: Khronos validator 0 errors / 0 warnings, one embedded texture, size-7 dimensions, orange skin on the sphere surface, black channel geometry under every sampled seam point, and exactly 8 separate orange panels. `inspect_sources.py` reopens the `.blend` and re-imports the GLB in Blender (`reports/sources.json`). Rebuilds are geometrically identical but not byte-identical because the exact Boolean orders output elements per run (`reports/reproducibility.json`). Preview PNGs are hero, front, side and 3q (Cycles, 32 samples); studio lights and camera are not exported. Browser/WebGL, WebKit and physical mobile checks have not been run; review remains required. Owner-project reuse is authorized; public redistribution terms are unspecified.

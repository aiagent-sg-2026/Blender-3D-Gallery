# Football

Original, unbranded classic soccer ball. Existing controlled category: `Balls`; its own collection avoids classifying soccer equipment as billiards. Draft, not downloadable. No external assets, fonts, images, logos, text or packaging.

The golden-ratio icosahedron has 12 vertices and 20 triangular faces. Truncating each directed edge at one third gives exactly 60 vertices, 12 black pentagons and 20 white hexagons. Each editable panel samples eight points along each edge and twelve radial rings, projecting onto a nominal 0.11 m sphere. The outer 20% rolls down to a 0.8 mm recessed shared seam. Each panel has a closed inward backing. Smooth custom normals come from the actual top geometry, excluding the backing. There are no image textures; black and warm-white materials use plain PBR colour and roughness.

The source retains 32 separate editable panel meshes. Export merges temporary evaluated copies into two meshes, one per material, under `ASSET_Football`; it preserves the authoring source. No camera or lights are exported. There are no external dependencies to pack into the blend. Units are metres and the origin is at the ball centre, matching individual billiards exports (`generate.py` relocates ball roots to zero while preserving their centred geometry). Blender +Z up / -Y front becomes glTF +Y up / +Z front. Nominal size 5 diameter is 0.22 m; the measured mesh envelope is about 0.219602 m on every axis. This is a visual model, not a certified sporting product or physics simulation.

Run from the repository root with Blender 5.3.0 and the repository's Node dependencies:

```sh
npm ci --ignore-scripts # only if node_modules is missing
blender --background --python-exit-code 1 --python models/football/generate.py
blender --background --python-exit-code 1 --python models/football/generate.py -- --skip-render
node models/football/validate.mjs
blender --background --python-exit-code 1 --python models/football/inspect_sources.py
node models/football/verify_source_edit.mjs
npm run validate:assets
npm run build
node models/football/check_browser.mjs
```

Append `-- --export-source --skip-render` to export manual edits, or `-- --export-source --previews-only` to render saved geometry only. Source-edit QA writes a disposable blend and GLB in the system temporary directory and checks that the original source hash stays unchanged. Compare the two build GLB SHA-256 values; `reports/reproducibility.json` records the actual identical hashes. No random seed or external asset is used.

Evidence is in `reports/`: measured assets, Khronos results, source geometry and source-edit proof, reproducibility, checks and the blocked browser attempt. All four Blender renders were visually inspected: the black pentagons, white hexagons and shallow seams read as a soccer ball. Limitations: white-to-white seams are subtle under broad studio lighting, and the recessed panel boundaries create slight silhouette undulations at close range. PNGs are hero, front, side and 3q; hero also has a lightweight WebP.

Local asset validation and the production build passed. Browser verification was blocked before launch by sandbox `listen EPERM` on 127.0.0.1; real browser rendering, orbit/zoom, mobile hardware and target GPU performance are unverified. The wider `npm test` run failed (89 passing files, 21 failing files); its output did not give detailed child-test errors. Blender generated all artifacts and source-inspection evidence, but its process remained alive during PulseAudio shutdown in this environment, including with `-noaudio`; this is not recorded as a clean process exit. An attempted IP-based PulseAudio override aborted at startup. Review is still required. No commit, push or publication was performed.

Original procedural geometry and materials. Reuse in the owner's projects is authorized. Public redistribution terms have not been specified.

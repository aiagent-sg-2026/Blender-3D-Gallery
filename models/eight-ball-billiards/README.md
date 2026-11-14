# Eight-ball billiards asset pack

Original, unbranded, meter-scale 3D assets created procedurally with Blender 5.1.2. The gallery build includes the independently selectable GLBs and the complete scene; the editable Blender source remains in the repository. No redistribution license has yet been selected.

## Contents

- `scene.blend`: editable Blender source, with asset roots named `ASSET_*` and a separate `STUDIO` group for the preview camera, floor and lighting.
- `generate.py`: source used to recreate the scene, render and GLB exports.
- `preview.webp`: 1600 × 1200 preview of the modeled scene.
- `exports/billiards-scene.glb`: complete scene without the studio objects.
- `exports/ball_00.glb` through `ball_15.glb`: cue ball and numbered balls, each centered on its own origin.
- `exports/table.glb`, `cue_01.glb`, `cue_02.glb`, `triangle_rack.glb` and `chalk.glb`: separately reusable assets. Individual exports are positioned at their asset-root origin; the table origin is at floor level.

The outside table dimensions are approximately 2.54 × 1.40 m, ball diameter 57.15 mm and cue length 1.47 m. Balls use curved geometry for the number marks, attached to each ball's root on opposite sides. The spherical marks sit within 0.09 mm of the ball surface to avoid visible floating. Materials use glTF-compatible Principled BSDF base color, metallic and roughness values; no external textures are required. UV layers are present, but a dedicated non-overlapping texture atlas has not been produced. The design is simplified and uses clean, untextured surfaces rather than photographic wood grain, cloth fibers or wear.

## Reproduce

From the repository root, with Blender 5.1.2 and `cwebp` installed:

```sh
blender --background --factory-startup --python models/eight-ball-billiards/generate.py
cwebp -q 88 models/eight-ball-billiards/preview.png -o models/eight-ball-billiards/preview.webp
```

The generator writes and replaces the artifacts in this directory. It also produces the intermediate `preview.png` and Blender may create a `scene.blend1` backup when overwriting. Inspect any existing work before regenerating.

## Verification performed

The updated balls have smoother geometry and curved number marks on both sides. Run `npm test` and `npm run validate:assets` to verify their exported geometry and glTF structure. The ball geometry, materials and viewer have been reviewed from multiple angles; desktop browser checks do not replace tests on every target engine or mobile device. Redistribution terms remain to be decided.

## Independent export and catalog maintenance

The saved source contains 21 `ASSET_*` roots. To export them without changing the source file, provide a destination directory:

```sh
blender --background models/eight-ball-billiards/scene.blend --python scripts/export-selected-assets.py -- /tmp/billiards-exports
npm run validate:assets
```

Each individual export contains only its asset root and children, with the root at the origin. The table origin is at floor level; balls use their centers. The full scene preserves the assembled positions and the original `?model=eight-ball-billiards` link.

Card thumbnails were generated from the corresponding source asset, using `scripts/render-asset-thumbnails.py` with Blender Workbench, then converted to WebP with `cwebp`. The catalog at `models/catalog.json` maps identities to exports and thumbnails. Triangle counts and file sizes are calculated from the GLBs at build time.

## Game table revision

The Game page reuses the individual exports. Cushion lengths and twelve pocket-jaw pieces were updated in the Blender source and generator so the six visible pocket approaches agree with the planar game colliders. The table, assembled scene, source, scene WebP and table thumbnail were regenerated; ball identities, curved markings and separate asset roots were retained. See [game implementation](../../docs/game-implementation-plan.md) for measured dimensions and [verification](../../docs/game-verification.md) for source/export/browser results.

## Sequential model QA: table support and inlays

MODEL-0001 corrects twelve floating rail sights and a 3.5 mm air gap below the
slate/cloth slab. The 2 mm deep sight discs are seated in the wood, with tops
0.1 mm above the rail. The slab underside is seated on the cabinet with a 0.1 mm
overlap while the playing surface remains at Z=0.7785 m. The generator and saved
source agree. Only sight/slab node heights and the slab mesh change in the table
and dependent assembled GLBs. Other mesh data, materials, gameplay colliders and
independent ball/cue/rack/chalk exports are preserved.

Run `node --test tests/pool-table.test.mjs` for both seating regressions.
Use `scripts/model-qa-blender.py` for one-root geometry inspection and eight-view
renders, and `scripts/test-pool-table-qa-browser.mjs` against a running gallery
for desktop/tablet loading and controls. The optional mobile viewport requires
`MODEL_QA_INCLUDE_MOBILE=1`; the owner excluded mobile testing from this QA
campaign. Viewport emulation is not physical-device performance verification. See the
[QA progress tracker](../../docs/3d-model-qa-progress.md) for current gate and
release status and production evidence.

## Cue 01 normal QA

MODEL-0002 corrects Cue 01 end-cap shading: eight cap faces are flat and their 144 boundary edges are sharp; tapered sides remain smooth. Dimensions, geometry, UVs, materials, transforms, Cue 02 and other standalone exports are preserved. The generator limits this reviewed change to Cue 01.

`scripts/repair-cue-01-normals.py` is a guarded one-time migration from its recorded source SHA256; preserve the baseline first. It exports only `cue_01.glb` and the dependent assembled scene. Do not run the full pack generator merely to update this cue. `scripts/model-qa-cue-details.py` renders the five source/re-import detail views without saving its input; diagnostic cap modes modify memory only.

From the repository root, with Node 24 and a built local preview server, run `MODEL_QA_ID=cue-stick-01 MODEL_QA_URL=http://127.0.0.1:5179/ node scripts/test-model-qa-browser.mjs` for fresh desktop/tablet loading, exact GLB payload/hash and controls. Exported cap/side normal regression checks are in `tests/cue-stick-01.test.mjs`; campaign evidence and remaining gates are in `docs/model-qa/MODEL-0002/README.md`. Physical mobile testing is excluded by the owner.

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

## Cue normal QA

The two straight cues share planar-cap shading in `cue_shading.py`: caps are flat, their boundary edges are sharp, and tapered sides remain smooth. Keep this helper beside `generate.py` when moving the source folder. Per-model QA/release status remains in the [campaign tracker](../../docs/3d-model-qa-progress.md); a shared rule does not imply that every model has completed acceptance.

`scripts/repair-cue-01-normals.py` and `scripts/repair-cue-02-normals.py` are revision-guarded one-time migrations. Preserve their recorded baselines first. They share `scripts/cue-normal-migration.py` and export only the selected cue and dependent assembly; no full-pack regeneration is needed. `blender --background --disable-autoexec models/eight-ball-billiards/scene.blend --python scripts/model-qa-cue-details.py -- --root ASSET_Cue_02 --output /tmp/cue-detail-review` renders the selected cue without saving its source. Diagnostic cap modes modify memory only; imported GLBs support the source/observe mode.

From the repository root, with Node 24 and a built preview, run `MODEL_QA_ID=cue-stick-02 MODEL_QA_URL=http://127.0.0.1:5179/ node scripts/test-model-qa-browser.mjs`. The geometric-normal regression rule is shared by the two cue test files. Read the [planar-cap prevention note](../../docs/model-qa/blender-planar-cap-normals.md) for the verified cause, bounded repair, axis convention and preservation checks. Physical mobile testing is excluded by the owner.

## Triangle rack joint and seating QA

MODEL-0004 closes the three original cylindrical bars on common miter planes,
retaining their radial profiles, face topology, UVs and material assignments.
`rack_geometry.py` owns this geometry operation for both the generator and
`scripts/repair-rack-joints.py`. Keep it and `cue_shading.py` beside the generator.
The helper separates planar caps from smooth sides and supplies analytic radial
side normals: oblique cuts otherwise change corner-angle weighting. The rack
root is lowered 12.6 mm so its lowest points overlap the preserved cloth top by
0.1 mm; independent exports remain centered on their own origin.

The migration accepts only its recorded source revision, fingerprints all source
objects, and exports only the rack and dependent assembly. Preserve originals
before invoking it. `scripts/model-qa-rack-details.py` renders six corner details
without saving; its optional candidate mode modifies memory only.
`node --test tests/triangle-rack.test.mjs` checks matching joint rings, cap and
radial normals in both exports, and assembly support. These tests use glTF's
local Y cylinder axis; the straight-cue world-X checks are not reused for the
rotated rack bars. Campaign acceptance remains in the progress tracker.

The MODEL-0004 capacity follow-up makes the rack centerline an equilateral
350 mm triangle so a five-row pack of fifteen touching57.15 mm balls fits.
`rack_geometry.py:rack_vertices` owns these endpoints for the generator and
`scripts/repair-rack-capacity.py`; only three rack bars resize. Its seven rack
regressions include actual exported-triangle/sphere collision checks for both
standalone and assembly. Diagnostic witness spheres are not product geometry.
The initial published revision was not accepted after this extra defect was
found; its own Actions run was cancelled before deployment. See the
[functional-scale note](../../docs/model-qa/billiards-functional-scale.md) and
current report for the final candidate and acceptance evidence.

# MODEL-0001 — Pool Table QA

Status: TESTING. Local repair is implemented; required regression and release
verification are in progress. No commit or push has been made for this model.

## Identification and scope

- Model ID: `pool-table`; QA ID: `MODEL-0001`.
- Source: `models/eight-ball-billiards/scene.blend`, root `ASSET_Table`.
- Generator: `models/eight-ball-billiards/generate.py`, Blender 5.1.2.
- Export: `models/eight-ball-billiards/exports/table.glb`.
- Dependent assembly: `models/eight-ball-billiards/exports/billiards-scene.glb`.
- Baseline revision: `1f9656346107bb49bdacc2b651c4f7e9ce869ac8`.
- Isolated release candidate base: `65e56ac20802cd8969fac3d9de9131e87319b96a`.
- Version identity is recorded with artifact SHA-256 in `artifact-regression.json`.
- Original source and affected artifacts are recoverable in Git and the local
  `output/model-qa/MODEL-0001/original/` snapshot with its SHA-256 manifest.

The inventory includes concurrent, uncommitted user assets. Its 554 catalog
entries, 2,338 physical 3D files and 1,825 queue records are a discovery snapshot,
not a claim that those local assets are all on GitHub. No historical/test variant
has been silently exempted. Dependencies, Git internals and generated `dist`
replicas are excluded from the authoring inventory.

## Defect and repair

TABLE-001 — P2: all 12 ivory rail sights floated above the wooden rail. The
source rail top is Z=0.8535 m; the old 2 mm deep sight was centered at Z=0.856 m,
leaving a measured 1.5 mm gap under its base. The detail render confirms this gap
and detached shadow. Root cause: the generator used the wrong sight elevation.

The corrected center is Z=0.8526 m: the base sits inside the wood and the top
remains 0.1 mm above it, avoiding coplanar depth conflicts. The generator, saved
Blender source, standalone GLB, dependent assembled GLB and corresponding two
WebP previews are updated. Geometry buffers, materials, cushion/pocket locations,
game colliders and all 20 independent sibling exports remain unchanged.

The seating regression test fails on both original GLBs and passes on both
corrected GLBs. `artifact-regression.json` verifies exactly 12 node-height changes
per affected GLB and byte-identical binary payloads; this is stronger than an
export-success message.

## Validation

| Gate | Result | Evidence / limitations |
| --- | --- | --- |
| Geometry | PASS | 52 meshes, 6,360 triangles; no source non-manifold edges, inconsistent winding, loose vertices or degenerate triangles. Bounds agree with authored dimensions of 2.54 × 1.40 m; corrected height 0.8536 m. |
| UV / textures | PASS for current untextured asset; texture-atlas quality N/A | UV values are finite. Six constant-color Principled materials use no image textures; no missing images, labels, normal maps or color-space bindings. Existing projected UVs are not a production texture atlas; no claim of texture-ready UVs. |
| PBR | PASS | Six opaque dielectric materials, metallic=0, roughness within [0,1]. Exact authored PBR values survive export/reimport. Rendered comparison inspected under identical neutral lighting. |
| Multi-angle visual | PASS | Actual front, back, left, right, top, bottom, 3/4 and rail-detail renders inspected before/after and after GLB reimport. Independent read-only visual review found no blocking defects (subjective viewer score 89/100, desktop/tablet). No supplied approved golden/reference set exists; this is a correction against the authored source contract, not a photorealism score. |
| GLB structure | PASS | Both affected GLBs: Khronos validator 0 errors, 0 warnings. Informational unused-UV messages: 52 table / 148 assembly; retained to preserve existing authoring compatibility. |
| GLB reimport | PASS | Same dimensions, triangle count and PBR values. Raw exported hard-normal/UV seams split vertices; welding positions at 1e-7 m **only in an inspection BMesh** produces 0 non-manifold or inconsistent-winding edges. Saved source and GLB are not welded or smoothed. |
| Animation / rig | N/A | Table is static: no armature or animation tracks. Gameplay physics is a separate caller and is covered by regression checks. |
| Runtime viewer | PASS for tested desktop browsers / viewports | Actual production gallery at 1440×900, 768×1024, 390×844: load, keyboard orbit/zoom/reset; mobile viewport also emulated touch orbit. No page errors or HTTP errors. Exact desktop/tablet reset-image comparison passes. An exploratory emulated-touch mobile reset screenshot differed; mobile validation is excluded by subsequent owner instruction, and no mobile reset PASS is claimed. |
| Static asset budgets | PASS against repository candidate targets | Table: 417,656 bytes, 6,360 triangles, 6 materials, 0 image textures; below 5 MiB / 100k-triangle candidate targets. No visible-quality reduction. Production software-WebGL observation: 52 draw calls / 6,360 triangles per rendered frame. |
| Physical mobile performance | N/A by explicit owner instruction | User instructed “no need test by mobile” after the missing-device finding. Stop mobile testing; no phone performance claim is made. |
| Regression | PARTIAL | Local full unit suite: 592/592. Isolated candidate unit suite on the required Node v24.21.0: 589/589; different counts reflect unrelated local/uncommitted tests. Both builds passed with pre-existing large-bundle warnings. Full Game browser suite failed on a page-navigation timeout before its second scenario; isolated reproduction then passed both the exact Chromium case and the existing WebKit shot smoke. The default Node 23 retry was interrupted after finding the documented Node 24 requirement. Full-suite execution on Node v24.21.0 is in progress; its first two scenarios passed. No claim that full browser regression passes. |
| GitHub main / Actions | NOT EXECUTED | Current QA gates are incomplete; commit, push and remote Actions are intentionally pending. No next model has been selected for repair. |

`structural-checks.json` contains executed source/reimport assertions.
`source-reimport-image-comparison.json` records per-view mean absolute RGB errors
of 0.0009–0.0078 on a 0–255 channel scale; these are descriptive measurements,
not invented visual-approval thresholds. Contact sheets and the full eight-view
PNGs are retained under `before/`, `after/`, and `reimport/`.

Browser evidence is retained at
`output/playwright/model-qa/MODEL-0001-release/`. Warnings are explicit: Playwright
blocks service-worker registration by test configuration, and screenshot capture
can trigger SwiftShader `ReadPixels` GPU-stall warnings. No phone-performance
claim is drawn from this environment. The Vite build warns about the existing
~2 MB application chunk; no unrelated application refactoring was attempted.

## Reproduction

From the repository root:

```sh
node --test tests/pool-table-inlays.test.mjs
/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec models/eight-ball-billiards/scene.blend --python scripts/model-qa-blender.py -- --root ASSET_Table --output /tmp/table-source-qa --render
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python scripts/model-qa-blender.py -- --root ASSET_Table --glb models/eight-ball-billiards/exports/table.glb --output /tmp/table-reimport-qa --render
MODEL_QA_URL=http://127.0.0.1:5179/ node scripts/test-pool-table-qa-browser.mjs
```

`scripts/repair-pool-table-sights.py` is a guarded, one-time baseline migration:
it requires the old 0.856 m source elevation and refuses an already-repaired or
unexpected source. Do not run the full pack generator merely to re-export this
table; it replaces unrelated sibling assets. The saved-source repair exports only
the table and its required dependent assembly.

## Release record

Commit SHA: none. GitHub main verification: not executed. Required Actions:
not executed. No force push, branch-protection bypass, unrelated-file staging or
model advance has occurred. Original user changes remain in the main worktree;
the candidate is isolated on `codex/model-qa-pool-table` at
`/tmp/blender-model-qa-release`.

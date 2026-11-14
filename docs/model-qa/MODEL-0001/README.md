# MODEL-0001 — Pool Table QA, Revision B

Status: READY_TO_PUSH. Both confirmed P2 model defects are repaired and all applicable
local gates have passed. Main synchronization and remote release verification remain. The local model commit is prepared; no push has occurred and no next model has
entered repair.

## Identification and recovery

- Model ID: `pool-table`; QA ID: `MODEL-0001`.
- Source: `models/eight-ball-billiards/scene.blend`, root `ASSET_Table`.
- Generator: `models/eight-ball-billiards/generate.py`; Blender 5.1.2.
- Export: `models/eight-ball-billiards/exports/table.glb`.
- Dependent assembly: `models/eight-ball-billiards/exports/billiards-scene.glb`.
- Original source revision: `1f9656346107bb49bdacc2b651c4f7e9ce869ac8`.
- Candidate branch: `codex/model-qa-pool-table`, isolated at
  `/tmp/blender-model-qa-release`; initial base `65e56ac20802cd8969fac3d9de9131e87319b96a`.
- Exact revision-B input hashes: `after/inspection.json`,
  `reimport/inspection.json`, and `artifact-regression.json`.
- Originals remain in Git and local `output/model-qa/MODEL-0001/original/`;
  checksums are in `original-manifest.json`.
- Intermediate revision A assets remain at `output/model-qa/MODEL-0001/revision-a/`.
  Its images, checks, first independent review and full browser log are retained
  under `revision-a/`. Revision A did not repair TABLE-002 and is not the release
  candidate. Its passing tests are baseline evidence only.

Discovery found 554 catalog entries, 2,338 physical 3D artifacts and 1,825 queue
records, including uncommitted user assets and historical/test variants. This is
an explicit discovery snapshot, not a claim that every path is on GitHub or has
passed QA. Dependencies, Git internals and generated build replicas are excluded.
See `../inventory.json` and `../discovery-validation.json` for complete coverage.

## Defects and repairs

| ID | Severity | Root cause and evidence | Correction |
| --- | --- | --- | --- |
| TABLE-001 | P2 | Twelve 2 mm deep rail sights centered at Z=0.856 m had their base at 0.855 m, 1.5 mm above the rail top at 0.8535 m. `before/detail-rail-sight.png` shows the gap and detached shadow. | Seat the discs at Z=0.8526 m, with tops 0.1 mm above the wood to avoid coplanar faces. |
| TABLE-002 | P2 | The slate/cloth underside at Z=0.7535 m was 3.5 mm above the cabinet top at Z=0.75 m. `contact-before/slate-cabinet-contact.png` exposes the background through this gap. | Extend the underside to Z=0.7499 m while retaining the playing top at Z=0.7785 m and its 2.30 × 1.18 m footprint. Preserve the 2 mm bevels. The generator derives the bottom from the actual cabinet top with a 0.1 mm seating overlap. |

The second defect was found during extra interface inspection after the initial
whole-table visual review. A successful topology test did not prove assembly
contact. `contact-after/` and the new slate-support regression close that coverage
gap. The first support migration attempt used an invalid Euler API property and
exited before saving; the corrected migration succeeded. Failed attempts remain
recorded, not silently discarded.

The generator, saved Blender source, standalone and assembled GLBs, and two WebP
previews are updated. `artifact-regression.json` independently compares original
and final serialized exports: only the slate mesh attributes and 13 node heights
change; all other mesh data and PBR materials remain identical. All 20 independent
sibling ball/cue/rack/chalk exports retain their original hashes. Game colliders,
pocket jaws, playing height, roots and names remain compatible.

## Validation gates

| Gate | Current result | Evidence and scope |
| --- | --- | --- |
| Geometry | PASS, revision B | 52 meshes; 6,360 triangles; no source non-manifold edges, inconsistent winding or degenerate triangles; positive signed volumes and unit world scales. Outside footprint remains 2.54 × 1.40 m; overall height 0.8536 m. Contact regression verifies the slate is supported and the playing height is unchanged. |
| UV / textures | PASS for current untextured asset; texture-atlas quality N/A | Finite UV values; no image textures or missing maps. Existing projected UVs are not a production texture atlas. No claim of texture-ready UVs is made. |
| PBR | PASS | Six unchanged, opaque, dielectric Principled materials; metallic=0 and valid roughness. Authored parameters survive reimport and are visually checked under the same neutral source/import lighting. |
| Multi-angle visual | PASS | Final source and reimport front/back/left/right/top/bottom/3/4/rail-detail renders inspected. Matched contact close-ups confirm TABLE-002 closure. A separate read-only reviewer accepts B with no blocking findings and subjective desktop/tablet viewer score 89/100. No approved photographic or golden reference set was supplied; this preserves the authored simplified style, not a photorealism claim. |
| GLB structure | PASS | Both affected files: Khronos validator 0 errors / 0 warnings. Table remains 417,656 bytes; assembly 3,518,732 bytes. Informational unused-UV messages remain: 52 table / 148 assembly. |
| GLB reimport | PASS | Same dimensions, triangle count and PBR values. glTF duplicates vertices at hard-normal/UV seams; welding positions at 1e-7 m **only in a disposable inspection BMesh** yields 0 non-manifold or inconsistent-winding edges. No source or export welding is performed. |
| Rig / animation | N/A | Table has no armature or animation tracks. Separate gameplay behavior is exercised by regression tests. |
| Runtime viewer | PASS for executed desktop/tablet checks | Actual production gallery at 1440×900 and 768×1024: model fetch, visible WebGL draws, keyboard orbit/zoom and reset; no page or HTTP errors. Final evidence is in `output/playwright/model-qa/MODEL-0001-final/`. |
| Performance | PASS against repository candidate asset budgets | 417,656 bytes, 6,360 triangles, 6 materials, 0 image textures; below 5 MiB / 100k-triangle targets. Observed software-WebGL drawing: 52 calls / 6,360 triangles per frame. No FPS, GPU-memory or speed-improvement claim is made. |
| Mobile | N/A by owner instruction | User explicitly replied “no need test by mobile”. New model probes default to desktop/tablet; mobile is opt-in. Existing repository regression suites are unchanged. No phone-performance PASS is claimed. |
| Regression | PASS, revision B | Node v24.21.0: 591/591 unit tests (including 4/4 seating/support checks), 46/46 complete Game browser scenarios and 31/31 complete game-experience scenarios; 0 page errors and no test-selection filters. Revision-A results remain baseline evidence only. |
| Main / Actions | REMOTE PENDING | Local commit prepared and synchronized to main `345f3104dad5e76bad31c86d63608820a5d65d55`; asset hashes preserved, post-sync build and 602/602 unit checks pass, as do both actual Viewer profiles. Push, remote SHA verification and required Actions remain pending. |

## Evidence and limits

`structural-checks.json` binds source/import assertions to actual SHA-256 inputs.
`contact-after/contact.json` records a support gap of approximately -0.000100 m
(the intended seating overlap) and an unchanged playing top. The gray through-gap
visible before repair is gone afterward. The black area above it is the shaded
underside/rail region, not the original exposed-background gap.

`source-reimport-image-comparison.json` records descriptive per-view mean RGB
errors, not invented approval thresholds. Contact sheets and detail images are
permanent evidence. Full-resolution local render attempts are retained in this
QA directory, including revision A; not every intermediate PNG is staged for Git.

The independent review proves what its images show; it does not claim all-object
physical connection or manufacturing correctness. Full positional claims rely on
structural and actual-GLB checks. Existing simplified pocket inserts and untextured
surfaces are retained; no new real-world reference dimensions are invented.

Warnings are retained: screenshot `ReadPixels` stalls in SwiftShader, service-worker
registration blocked by the browser test configuration, and the existing large
application bundle. These do not establish phone performance. An early Node-23
browser attempt failed during navigation; Node 23 does not match this repository's
Node-24 requirement. The failure log and subsequent Node-24 baselines are retained.
A temporary read-only request observer confirmed the long revision-A gallery loop
was progressing; it changed no HTTP responses or test expectations and its local
inspector was closed.

## Reproduce

```sh
node --test tests/pool-table.test.mjs
blender --background --disable-autoexec --python-exit-code 1 models/eight-ball-billiards/scene.blend --python scripts/model-qa-blender.py -- --root ASSET_Table --output /tmp/table-source-qa --render
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/model-qa-blender.py -- --root ASSET_Table --glb models/eight-ball-billiards/exports/table.glb --output /tmp/table-import-qa --render
blender --background --disable-autoexec --python-exit-code 1 models/eight-ball-billiards/scene.blend --python scripts/render-pool-table-contact.py -- /tmp/table-contact-qa
MODEL_QA_URL=http://127.0.0.1:5179/ node scripts/test-pool-table-qa-browser.mjs
```

Use Node 24 and Blender 5.1.2. The two `repair-pool-table-*.py` scripts are guarded
one-time migrations from their documented baseline states; preserve sources first.
Do not run the full pack generator merely to update one table, since it replaces
unrelated sibling outputs.

## Release record

Repair commit SHA is resolved from Git history and recorded after publication.
Remote main: not yet verified for this repair. Required Actions:
not yet run for this repair. No force push, protection bypass or unrelated-file
staging has occurred. The progress tracker remains authoritative for sequential
advancement; no next model may enter repair until this model's main release and
required remote checks are verified.

Post-sync acceptance: `post-sync-validation.json` and `post-sync-viewer.json` bind the synchronized main parent, exact model hashes, successful build, 602/602 unit tests and the repeated desktop/tablet model flow. The extra upstream Visitor v2 branch does not execute for this table.

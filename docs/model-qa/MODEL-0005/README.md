# MODEL-0005: Chalk

Status: READY_TO_PUSH. CHALK-001 is repaired; current648 unit/22 targeted,
source/import, export, guarded migration replay, Viewer, independent visual
and full Game46/experience31 checks pass. No commit/main/Actions/production
PASS is claimed. MODEL-0006 has not started.

Selected only after final MODEL-0004 release51dfcfe3 passed required
Actions43655719588 and exact production/runtime acceptance. Source:
`models/eight-ball-billiards/scene.blend`, root `ASSET_Chalk`;
standalone `exports/chalk.glb`, dependent `exports/billiards-scene.glb`.
`original-manifest.json` preserves the complete baseline and sibling hashes.

## Defect and smallest repair

CHALK-001(P2): the bottom was atZ≈0.855 m while the supporting flat wooden rail
is atZ≈0.8535 m, leaving a 1.5 mm air gap. Native source contact views and an
actual exported-triangle ray test independently reproduce it. The entire
25×25 mm footprint fits within the rail's flat top, outside its bevel.

Lower only the chalk root by 1.6 mm. The new bottom isZ≈0.8534 m with 0.1 mm
intentional overlap. Shape,25×25×27 mm dimensions, two mesh objects/216
triangles, bevels, UVs, material assignments, normals and core/sleeve contact
remain unchanged. The exposed usable face stays above the sleeve.

The generator contains the same root adjustment. The guarded migration
`scripts/repair-chalk-contact.py` accepts only recorded source907f2038.
Final source SHA256:
`6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672`.
Per-object geometry hashes are identical before/after. Only world transforms
of the root and its two children move; all unrelated transforms are preserved.

## Export preservation and replay

All 21 standalone GLBs remain byte-identical. Normalized chalk export has no
placement change. A fresh export differs only in historical generic Cube mesh
labels: every other JSON field and the complete binary payload match. The
migration proves this identity before retaining the original standalone bytes.
Asset-root and object-node identities are unchanged.

Chalk remains16,768 bytes, SHA256
`218bb66d9eb918e0d6131800e5f3446e5820e5c74a2ba4c56840faccdbe25915`.
The assembly remains3,518,732 bytes, SHA256
`6e11310f233ca08c86cffa9b075500fd47d07396deb78b3e5ef06af611c3e7ff`.
Its complete binary payload is byte-identical; the only JSON change is
`ASSET_Chalk` translation Y lowered1.6 mm. Every material, mesh, UV, normal,
hierarchy relation and unrelated node remains unchanged.

The final guarded entry point was replayed on a separate preserved baseline
copy. Both resulting exports match the working candidate byte-for-byte;
`migration-replay/results.json` records the comparison. Neither immutable
originals nor active source were modified by that replay.

## Executed QA

- Source and changed-assembly re-import: closed positive volumes, no degenerate
  triangles, loose vertices, inconsistent winding or non-finite UV. Disposable
  position welding accounts for glTF UV/normal seam vertices without saving
  geometry changes. The original standalone re-import remains current because
  its file is byte-identical.
- Two unchanged opaque untextured blue dielectric materials, metallic0,
  roughness0.6/0.95. Atlas/stretch assessment is N/A. Static model with no rig or
  embedded animation: animation N/A.
- Seven overview views each for source/import before and after, plus two actual
  rail-contact views before/source-after/import-after. Nine final native matched
  views have maximum mean RGB-channel error0.006518 on a0–255 scale; these are
  descriptive values, not an invented threshold. Separate visual review accepts
  the repair, no blockers, subjective Viewer89/100.
- Both actual exports validate with0 errors/0 warnings; unused untextured UV
  infos retained. Baseline chalk tests: two scale/core-sleeve PASS, rail seating
  FAIL at1.5 mm. After repair all22 chalk/rack/table/cue tests and complete
  unit suite648/648 PASS. Build PASS with the existing bundle-size advisory.
  Five independent rays confirm actual flat rail triangles support the footprint.
- Fresh built chalk and assembly Viewer each pass desktop1440×900 and
  tablet768×1024 exact decoded payload/SHA, loading, keyboard orbit/zoom, exact
  reset and mouse orbit, with zero page/HTTP errors, context loss or overflow.
  Sampled software WebGL shows chalk2 calls/216 triangles and assembly148/98,100
  per observed frame. Physical mobile testing is excluded by the owner; no
  hardware FPS claim is made.
- Full current Game46/46 (including all561 gallery previews/downloads) and
  experience31/31 PASS, without filters or page errors.

## Evidence and acceptance still required

All34 native PNGs were inspected before packaging; `render-publication.json`
hashes every image and preserves its local native path. Six native contact
PNGs, seven contact sheets and current Viewer images are retained. Numerical
comparisons and independent review used native images. `contact*.json` records
support selection and measurements; scripts reproduce views without saving.

The [support-contact lesson](../billiards-support-contacts.md) records independent
regression ownership for repeated placement defects. No global Skill or KB
memory was changed. Current regression is complete. Scoped review/main synchronization,
separate commit/push, required Actions and actual production acceptance must
pass before MODEL-0006 starts. The overall campaign remains incomplete.

Because this repair affects assembly placement, actual production acceptance must
cover the changed assembly payload/hash and Viewer as well as the unchanged
standalone chalk. A standalone-only production check would not prove this fix.

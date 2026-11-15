# MODEL-0004: Triangle Rack

Status: PUSHED / accepted. Final `51dfcfe36477df12895287b0db3aee3d5a29a43f` is
verified on main. Required Actions43655719588 completed successfully, including
Pages deployment. Independent production fetch matchesbb5ffe12; fresh desktop
and tablet Viewer controls pass. All four defects are closed. The initial
cb0c0c60 attempt remains historical and unaccepted. MODEL-0005 had not started
at this acceptance.

This model was selected only after MODEL-0003 passed main, required Actions and
exact production payload/runtime acceptance. Source:
`models/eight-ball-billiards/scene.blend`, root `ASSET_Triangle_Rack`;
standalone `exports/triangle_rack.glb`, dependent `exports/billiards-scene.glb`.

## Confirmed defects and final behavior

- RACK-001(P2): flat-ended bars left outside V-notches at three corners. Matching
  miter planes close all three joint rings, retaining the radial profiles,
  three source meshes,132 triangles, UVs and face/material assignments.
- RACK-002(P2): all-smooth caps distorted highlights. Caps are flat and sharp at
  their boundaries; clipped cylinder sides use analytic radial normals because
  oblique cuts alter corner-angle weighting. `rack_geometry.py` owns the rule.
- RACK-003(P2): assembled rack bottom was12.5 mm above the cloth. Lowering only
  its root12.6 mm seats the bottom atZ≈0.7784 m with0.1 mm overlap against the
  unchangedZ=0.7785 m cloth. Capacity follow-up preserves this root position.
- RACK-004(P2): the original unequal centerline triangle could not accommodate
  a touching five-row fifteen-ball pack at the authored 57.15 mm diameter.
  Initial QA missed this functional-size check. Two added tests reproduce real
  exported triangle/sphere intersections on cb0c0c60 while its five prior rack
  checks pass. The final centerline is equilateral with 350 mm sides, retaining
  the 9 mm bar radius and centroid. Balls are never shrunk or repositioned in
  product files. The new pack fits without intersecting any actual GLB triangle.

Final physical bounds are about0.339109 ×0.381177 ×0.018 m. The supporting
circular-bar analysis evaluates all piecewise rotation extrema, and indicates
about3.03 mm horizontal clearance surplus after resizing. This mathematical
model supplements the direct exported-mesh checks; diagnostic sphere renders
alone cannot establish millimeter clearance.

## Preservation and reproducibility

`original-manifest.json` preserves the pre-QA source228720e3 and all sibling
hashes. `capacity-baseline.json` separately preserves the initial published,
unaccepted revision cb0c0c60/sourceefaf70ef. Originals remain under local
`output/model-qa/MODEL-0004/`; no baseline is overwritten.

`scripts/repair-rack-joints.py` remains the one-time initial migration.
`scripts/repair-rack-capacity.py` accepts only its recordedefaf70ef source;
`rack_geometry.py` supplies the same 350 mm centerline to the generator.
No full-pack generation is run. The final source SHA256 is
`907f2038d32c0ded1906d89d7f14bc6b2364cde22002c337d8187c5d3431c287`.
The capacity migration fingerprints every source object: only the three rack
bar meshes/transforms change; the rack root and all other objects are unchanged.
UVs, radial coordinates and face/material assignments remain preserved.

Twenty sibling standalone GLBs remain byte-identical to the pre-QA baseline,
including the accepted table and both cues. `capacity-artifact-regression.json`
compares the follow-up against cb0c0c60 and proves all138 unrelated assembly
mesh payloads, all materials, unrelated nodes and root seating unchanged.
The initial migration and artifact reports remain historical evidence of
RACK-001/002/003, rather than current candidate fingerprints.

Current standalone:8,136 bytes, three mesh objects/132 triangles, SHA256
`bb5ffe129f0008420247a24c76e8abfb555a8b9131e8b69cd980d50f2972e0a4`.
Current assembly:3,518,732 bytes, SHA256
`425ad14274d8d765df1929db78b0bb0fa2e1cceec30c1916d4e5c17e2a23962b`.
Equal bar geometry permits export-data reuse without removing scene objects.

## Executed current-candidate QA

- Source/re-import: positive volume; no degenerate triangles, loose vertices,
  inconsistent winding or non-finite UV. Disposable position welding accounts
  for UV/hard-normal seams without modifying saved geometry. Each bar is closed
  and adjacent cap rings meet; this is not a destructive Boolean union.
- One unchanged opaque untextured walnut dielectric, metallic0/roughness0.28.
  Texture atlas/stretch quality is N/A. No rig or embedded animation: N/A.
- Seven overview and six corner views for final source and imported GLB.
  Thirteen native comparisons have maximum mean RGB-channel error0.003545 on
  a0–255 scale (descriptive, not an invented quality threshold). Four additional
  before/after fifteen-ball witness views are diagnostic only; spheres are
  neither saved nor exported into product files. Second independent visual
  review accepts the final candidate, no blockers, subjective Viewer89/100.
- Current exports: Khronos validator0 errors/0 warnings; unused UV infos retained.
  All 19 rack/table/cue checks pass, including seven rack checks with both new
  sphere/triangle capacity cases. Complete unit suite645/645 and build PASS.
  The existing large-bundle advisory remains. Initial results643/17 belong to
  the superseded local candidate and are not presented as current coverage.
- Fresh actual built rack and assembly Viewer each pass desktop1440×900 and
  tablet768×1024 exact decoded payload/SHA, loading, keyboard orbit/zoom, exact
  reset and mouse orbit with no page/HTTP errors, context loss or overflow.
  Sampled software WebGL shows rack3 calls/132 triangles and assembly148/98,100
  per observed frame. No physical-device FPS is claimed. Physical mobile testing
  is excluded by the owner's explicit instruction.
- Full current Game46/46, including all561 gallery preview/download entries,
  and experience31/31 PASS without filters or page errors. Earlier initial
  results remain historical evidence, not substituted for these current runs.

## Evidence and remaining release gates

`capacity-*` files contain the final candidate. Thirty new native PNGs were
independently reviewed before packaging; `capacity-render-publication.json`
hashes and locates every native file. Three final native joint top views,
four native capacity witnesses and contact sheets are retained. Numerical
comparisons used native images. The initial52-image manifest remains historical.

`capacity-witness-*` contains temporary spheres for size inspection only.
`scripts/model-qa-rack-details.py --candidate` requires an original uncut source;
current repaired inputs use observation mode. The historical initial intermediate
candidate predates analytic radial normals, as recorded in its settings.

Current regression, scoped diff/main synchronization, follow-up commit/push,
exact main/blob verification, required Actions and actual production acceptance
are complete before selecting MODEL-0005. Initial own-run cancellation is not success. Post-push closure
metadata will travel with the next validated campaign commit instead of creating
a metadata-only push that supersedes required checks. Campaign remains incomplete.

Current publication evidence: `release-evidence.json`. Initial cancelled attempt
is retained separately in `initial-release-evidence.json`.

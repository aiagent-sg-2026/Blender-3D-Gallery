# MODEL-0006: Cue Ball

Status: PUSHED / accepted. QA-only `e23be21ca38289ffc6b7a56218779891a197592f` is
verified on main. Required Actions43664847183 and Pages deployment succeeded.
Actual cue-ball and assembly payloads, four fresh browser profiles and three
checks on downloaded production files pass. No product repair was required.
MODEL-0007 had not begun at this acceptance.

Selected only after MODEL-0005 final8c61a369 passed required Actions43660711896,
exact standalone and changed-assembly production payloads, four browser profiles
and direct downloaded-file support checks. Source root `ASSET_Ball_00` lives in
`models/eight-ball-billiards/scene.blend`; independent export `exports/ball_00.glb`.
Original source/generator/previews and all22 exports are preserved with hashes.

## Observed model and preservation

One unnumbered resin body, authored57.15 mm diameter,3968 triangles. Source
geometry is closed with positive volume, no degenerate triangles, loose vertices,
inconsistent winding or non-finite UV. Disposable position welding verifies
imported seams without modifying saved geometry. Outward smooth normals follow
the sphere; half the authored angular grid spacing bounds their deviation.

The sphere bottom is tangent to the actual cloth, within1 micron in the direct
exported-triangle ray test. Source/import contact inspection reports a gap of
about5.96e-8 m, consistent with floating-point resolution. No seating correction
is needed. One unchanged opaque ivory dielectric has metallic0/roughness0.24.
UVs are finite; texture-atlas/stretch quality is N/A for the untextured material.
No rig or embedded animation: N/A. The existing Game interaction suite covers
its user-facing reuse separately.

All product files remain unchanged, including source SHA256
`6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672`,
all22 GLBs, generator, scene preview and card thumbnail. The retained standalone
is93,692 bytes, SHA256
`6fde7586234f2c7d4082a42e72e825aec4dd2205f30b2066c73108651558a732`.
No speculative cosmetic change, regenerated card or replacement GLB is published.

## Export replay and retained instrument history

The first scratch replay's byte-equality hypothesis failed: fresh output SHA
`aabd0a694deb26bd2df038debc334717dd17776be259b25179e832409ed819fd`
differs from the original despite identical full JSON and every non-index byte.
Inspection proves all3968 oriented triangles, including multiplicity and winding,
are identical. Only triangle submission order differs. The original failed
predicate, source/output hashes, script and raw log are retained.

The corrected uniform semantic comparison checks complete JSON, all binary
bytes outside the index region, and sorted cyclic-normalized oriented triangles.
It does not ignore winding, UVs, normals, material ownership or object identity.
A parser-only syntax attempt was NOT_RUN; its record/log are retained. Splitting
the function onto its own line and compiling first fixed that tool issue.
The semantic replay then passed once. `exact_standalone_replay=false` remains
explicit. No model was edited to make the verifier pass, and neither source nor
product file was saved or overwritten by the scratch export.

Original standalone, assembly and replay GLB each validate with0 errors/0 warnings;
unused untextured UV info remains. The canonical comparison follows the existing
[export-preservation reasoning](../blender-planar-cap-normals.md); it does not
turn a file-hash mismatch into a byte-identity claim.

## Executed current QA

- Seven source and seven standalone re-import views, plus two source and two
  assembly re-import contact views. Nine matched native comparisons
  have maximum mean RGB-channel error0.001065 on a0–255 scale, descriptive rather
  than an invented acceptance threshold. Independent review accepts the model,
  no required repair, subjective Viewer89/100.
- Three new checks cover radius/normals/PBR in both GLBs and actual cloth
  contact in the assembly. All25
  current billiards regressions and complete651/651 unit tests pass. Build PASS
  with the existing bundle-size advisory.
- Fresh actual Viewer passes desktop1440×900 and tablet768×1024 exact decoded
  payload/SHA, loading, keyboard orbit/zoom, exact reset and mouse orbit, without
  page/HTTP errors, context loss or overflow. Sampled software WebGL shows one
  draw/3968 triangles per observed frame. Physical mobile is excluded by the
  owner; these results do not establish hardware FPS.
- Full current Game46/46 (including all561 gallery preview/download entries)
  and experience31/31 PASS, without filters or page errors.

## Evidence and remaining acceptance

All18 native images were independently inspected before packaging. Six native
PNGs and four contact sheets are retained; `render-publication.json` hashes
and locates every native original. Numerical comparisons used native files.
`artifact-preservation.json` proves product preservation independently of
`export-replay-results.json`, which proves semantic re-export equivalence.

Current regression, scoped diff/main synchronization, the separate QA commit/push
and exact main/blob verification are complete. Required Actions and actual
production payload/runtime acceptance passed before selecting MODEL-0007. The full repository campaign remains incomplete.

Publication evidence: `release-evidence.json`. Post-push closure metadata will
travel with the next validated campaign commit rather than superseding this
release with a metadata-only push.

Production evidence includes the unchanged standalone and assembly hashes,
current Viewer controls and direct sphere/cloth tests on downloaded GLBs.

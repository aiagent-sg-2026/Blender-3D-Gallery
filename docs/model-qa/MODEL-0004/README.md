# MODEL-0004: Triangle Rack

Status: READY_TO_PUSH. All applicable local gates pass. No commit, remote
Actions or production PASS is claimed yet; MODEL-0005 has not started.

Selected only after MODEL-0003 main, required Actions43648248917 and exact
production payload/runtime acceptance passed. Baseline8d96b619 and
`original-manifest.json` preserve original hashes. Editable source:
`models/eight-ball-billiards/scene.blend`, root `ASSET_Triangle_Rack`;
standalone `exports/triangle_rack.glb`, dependent `exports/billiards-scene.glb`.

## Confirmed defects and repairs

- RACK-001(P2): flat-ended bars meet only at their centerlines, leaving visible
  outer V-notches and protruding ends. Matching miter planes close all three
  corner rings. Only ring vertices' longitudinal positions change; radial
  profiles, three source meshes,132 triangles, UVs and face/material assignments
  are preserved. Overall intended closed-joint bounds are about
  0.33635 ×0.36044 ×0.018 m; the former notched bounds were0.31334 ×0.34577 ×0.018 m.
- RACK-002(P2): all-smooth caps distort end/side shading. Caps are flat and sharp
  at their boundaries; clipped cylinder sides use analytic radial normals.
  Oblique cuts alter corner-angle weights, so the straight-cue shading check
  alone is insufficient. `rack_geometry.py` is shared by generator and migration.
- RACK-003(P2): the assembled rack bottom is12.5 mm above the preserved cloth
  top. Lowering only the rack root by12.6 mm seats the bottom atZ≈0.7784 m,
  overlapping the unchanged cloth topZ=0.7785 m by0.1 mm.

`scripts/repair-rack-joints.py` refuses any source revision except recorded228720e3.
The resulting source SHA256 is
`efaf70ef5c6071813edd0a869ca5f143cc83c58d82253123df1752b54dccff56`.
`source-migration.json` fingerprints every object: only the rack root and its
three meshes change. Twenty sibling standalone GLBs remain byte-identical,
including the accepted table and two cues. `artifact-regression.json` proves all
138 unrelated assembly mesh payloads and all materials are unchanged; hierarchy
and transforms are unchanged apart from the rack's intended Z translation.

Standalone GLB:8,928 bytes (was8,136), three meshes/132 triangles, SHA256
`860629a1fdf95867bc096df4f550a7ba631f2de633fac5a817382be464588cc1`.
Assembly:3,519,528 bytes (was3,518,732). Extra exported vertices separate cap
and side normals without increasing triangles.

## Executed QA

- Source and imported geometry: positive volume; no degenerate triangles, loose
  vertices, inconsistent winding or non-finite UV. Disposable position welding
  distinguishes exporter seam vertices from actual open boundaries; saved
  geometry is not welded. Each of the three bars is closed and meets its neighbor
  at a shared cap plane; this is not a destructive Boolean union.
- One unchanged opaque untextured walnut dielectric, metallic0/roughness0.28.
  Texture atlas/stretch assessment is N/A; this is a simplified untextured model.
  No armature or embedded animation, so animation is N/A.
- Seven overview and six corner views for both final source and imported GLB.
  Thirteen native comparisons have maximum mean RGB-channel error0.003741 on a
  0–255 scale (descriptive, not an invented acceptance threshold). Independent
  visual review accepts the repair without blockers; subjective Viewer89/100.
- Both exports: Khronos validator0 errors/0 warnings; unused untextured UV infos
  retained. Five new exported joint/normal/support checks fail on the original
  baseline and pass after repair; all17 rack/table/cue checks pass. Complete
  unit suite643/643 PASS. Build PASS with the existing large-bundle advisory.
- Fresh actual built Viewer rack and assembly each pass desktop1440×900 and
  tablet768×1024 loading, exact decoded payload/SHA, keyboard orbit/zoom, exact
  reset and mouse orbit, without page/HTTP errors or context loss/overflow.
  Sampled software WebGL shows rack3 calls/132 triangles and assembly148/98,100
  per observed frame. These measurements do not establish hardware FPS.
- Full Game46/46 (including all561 gallery preview/download entries) and
  experience31/31 PASS, without filters or page errors. Final build includes the
  regenerated scene/card previews; fresh final desktop/tablet rack runtime also
  passes. Physical mobile testing is excluded by the owner's explicit instruction.

## Evidence and remaining gates

Native images were independently reviewed and numerically compared before
packaging. Six before/after native top-joint PNGs and eight contact sheets are
retained; `render-publication.json` hashes all52 native PNGs and records local
preserved paths. Runtime evidence includes desktop/tablet rack and assembly page
and canvas images. Source/re-import scripts and recorded inputs reproduce final views. The historical
intermediate candidate predates analytic radial normals; its settings record that
limitation. Current candidate mode invokes the final helper.

Complete scoped diff review, main synchronization, separate commit/push,
required Actions and exact production acceptance must pass before
MODEL-0005 starts. The overall campaign remains incomplete.

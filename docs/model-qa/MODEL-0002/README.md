# MODEL-0002: Cue Stick 01

Status: READY_TO_PUSH. All local gates and independent review pass. Main synchronization and post-sync checks are complete. No main release or remote-check PASS is claimed for this model yet.

Source: `models/eight-ball-billiards/scene.blend`, root `ASSET_Cue_01`. Generator: `generate.py`. Standalone: `exports/cue_01.glb`; dependent assembly: `exports/billiards-scene.glb`. Baseline main integration is `2bf3f961`; originals are preserved in Git and the local campaign backup, with hashes in `original-manifest.json`. MODEL-0001 passed required Actions and production acceptance before this model entered QA.

## Confirmed defect and repair

CUE-001 (P2): smooth planar end caps and unmarked cap boundaries average the cap and side normals. The long tapered butt develops a pinched highlight and its end appears rounded despite planar geometry. The same construction affects the shaft, ferrule and tip. Source-quad normal measurements and controlled macro renders confirm the cause. On the butt, the original side normal's absolute axial component is about .674; the intended tapered-side value is .01165.

The controlled comparison establishes that flat cap flags alone correct the cap face but leave the side highlight pinched in Cycles. Explicit sharp cap boundaries are also required. The repair changes exactly eight cap smooth flags and 144 boundary sharp flags on the four Cue 01 meshes. Side surfaces stay smooth. The generator applies this rule only to Cue 01; Cue 02 and every other model remain unchanged.

`source-migration.json` independently fingerprints all source objects: vertex/face geometry, UVs, material assignments, parent ownership and world transforms remain identical, and no unrelated source shading changes. `artifact-regression.json` checks both GLBs. The exporter reorders Cue 01 vertex/index buffers, so raw accessor ordering changes; canonical oriented triangles including UVs remain identical. Every unrelated shared-scene mesh payload is byte-identical, and the other 20 standalone GLBs are unchanged. The standalone stays 14,632 bytes; the assembly grows by 1,084 bytes because previously shared cue data is no longer identical. Mesh/triangle counts remain 4/272 for the cue.

## Executed checks

- Source and re-import geometry: closed after accounting for export seam splits; positive volumes, finite UV, no loose or zero-area geometry, no inconsistent winding, unit scales. The inspection weld is disposable and never changes saved geometry.
- Four unchanged opaque dielectric materials; untextured asset. Atlas/stretch quality is N/A. No texture or rig/embedded animation is introduced.
- Seven source and seven re-import overview directions plus five detail views each are rendered. End caps, butt highlight, joint, ferrule and tip are inspected. Source/re-import comparison covers 12 matched views; largest mean RGB-channel error is .00308 on a 0–255 scale (descriptive, not an invented quality threshold).
- Both exported GLBs validate with zero errors and zero warnings. Four unused-UV informational messages for the cue are retained.
- New geometric-normal regression tests fail 4/4 on the baseline for the actual cap/side alignment defects. After repair, the four cue tests and four preserved table-support tests pass 8/8.
- Complete unit suite: 613/613 initial, 617/617 after M058 synchronization and 621/621 after M059 synchronization passed. Build passed, with the pre-existing bundle-size advisory.
- Actual built Viewer: desktop 1440×900 and tablet 768×1024 loading, keyboard orbit/zoom, exact reset, mouse orbit, exact decoded payload size and SHA256 all pass. Zero page/HTTP errors and no context loss. Observed rendering is four calls and 272 triangles per sampled frame in desktop software WebGL; no physical-device FPS claim is made.
- Shared browser-probe migration also passes both Pool Table profiles. `probe-calibration.json` explains consistent focus-visible states for exact reset comparisons.
- Physical mobile testing is excluded by explicit owner instruction. Embedded animation/rig tests are N/A for this static asset; actual Game procedural cue interactions are covered by the completed regression suites.

## Integration and release readiness

Independent read-only visual review accepted the repair with no P0/P1/P2 or required P3; subjective Viewer presentation score is 87/100 (threshold85). Scope and limitations are recorded in `independent-visual-review.md`.

Full Game 46/46 and experience 31/31 passed with zero page errors and no selection filters. That local gallery loop covered the 556-entry baseline. After synchronizing main `44aaed6a`, 617/617 unit checks, a fresh build and both exact-payload Viewer profiles passed. Game/Viewer code is unchanged by the M058/Shelf Inspector integration. The new upstream catalog entry is explicitly queued as PENDING; required remote checks will exercise the complete 557-entry release before any next-model advance. See `post-sync-validation.json`.

The normal migration preserves all geometry/UV/material/transform ownership; standalone and assembly validators pass, all siblings remain byte-identical, and the separate Cue01 normal tests enforce both cap and side correctness. Final diff review, scoped commit, push/main verification, required Actions and production acceptance remain. MODEL-0003 has not started. The full campaign remains incomplete.

## Render evidence packaging

The four `contact-sheet.jpg` files retain overview coverage; `shading-fresh/comparison.jpg` shows the original, flat-cap-only and sharp-boundary comparison. Six full-resolution native butt-side/butt-end PNGs retain the key before/after source and re-import evidence. Viewer screenshots are also native PNG. `render-publication.json` hashes every native render and records its retained local path under `output/model-qa/MODEL-0002/native-renders/` when it is omitted from Git. Numerical image comparisons were computed on native PNGs, before contact-sheet conversion. The separate reviewer inspected the original native files before packaging. Reproduce omitted renders with the recorded input hashes, Blender version, settings and QA scripts; no generated models or temporary candidate sources are committed as evidence.

Final pre-commit synchronization: `f62f5809` adds M059/Shelf Inspector changes while Game/Viewer implementation and repaired cue payload remain unchanged. `final-base-validation.json` and verbatim compressed logs record 621/621 unit tests, build, and both fresh exact-payload Viewer profiles passing. Catalog count is now 558; the new upstream model is appended PENDING, and required remote latest-catalog checks remain mandatory.

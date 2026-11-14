# MODEL-0003: Cue Stick 02

Status: READY_TO_PUSH. All applicable local gates, full regressions, independent visual review and post-sync integration checks pass. Scoped commit, main/required Actions and production acceptance remain. MODEL-0004 has not started.

Selected only after MODEL-0002 passed required Actions43637504290 and production acceptance. Baseline13ef9c10 and `original-manifest.json` preserve originals. Source `models/eight-ball-billiards/scene.blend`, root `ASSET_Cue_02`; standalone `exports/cue_02.glb`, dependent assembly `exports/billiards-scene.glb`.

## Defect, ownership and preservation

CUE-002(P2): smooth planar caps and unmarked cap boundaries average cap/side normals, producing pinched highlights and falsely rounded planar ends. Actual source/import inspection and matched before/candidate macro views independently confirm the same construction defect as Cue01. The butt's axial normal component changes from about.674 to the taper's.01165.

The persisted repair changes eight cap smooth flags and144 sharp boundary edges on four Cue02 meshes. `cue_shading.py` now owns this operation for generator and revision-guarded migration wrappers. Geometry, UVs, material assignments, hierarchy and world transforms are unchanged; unrelated source shading is unchanged. `source-migration.json` fingerprints every source object before/after. Source SHA256 is `228720e3c3db914cb3aed912d701d34b95955d527c43d410e6fa74fa420db5de`.

`artifact-regression.json` confirms that export vertex/index reordering preserves canonical oriented triangles and UVs. Only Cue02 payloads change; all other mesh payloads and20 sibling GLBs remain byte-identical. Cue01's accepted SHA932029a3... and the table are preserved. Standalone remains14,636 bytes, four meshes/272 triangles, SHA256 `e33be9d887a2a99ce637107acfb7b242d0213ab0d12e693446ee59a6220081d1`. The assembled file returns to3,518,732 bytes as the matching cue data can be shared again.

The original Cue01 migration entry point is retained. Running the shared implementation on an isolated original source copy reproduces both accepted13ef9c10 exports byte-for-byte; `legacy-compatibility/results.json` records this independent compatibility check. No baseline source or active working export was overwritten by that test.

## Executed QA

- Source/re-import geometry: positive volumes; no zero-area/loose geometry, inconsistent winding or non-finite UV. Disposable position welding accounts for export UV/hard-normal seams without modifying saved geometry.
- Four unchanged opaque dielectric untextured materials. Texture-atlas/stretch quality is N/A. No rig or embedded animation; that gate is N/A for this static asset.
- Seven overview and five detail views rendered for both repaired source and re-import. Twelve native comparisons have maximum mean RGB-channel error.00381 on a0–255 scale (descriptive, not an invented quality threshold). Separate visual review accepts the repair with no blocking findings and subjective Viewer score87/100.
- Both real exports validate with zero errors/warnings; unused-UV infos are retained.
- Shared geometric-normal checks retain the original Cue01 criteria. Baseline results: Cue01 four PASS, Cue02 four FAIL for actual cap/side defects. After repair: both cues and preserved table support checks12/12 PASS. Complete initial unit suite625/625 and post-sync638/638 PASS; build PASS with the existing bundle advisory.
- Fresh built Viewer Cue02, full assembly and prior Cue01 each pass desktop1440×900 and tablet768×1024 loading, exact decoded payload/SHA, keyboard orbit/zoom, exact reset and mouse orbit with zero page/HTTP errors. Cue02 observes four calls/272 triangles per sampled software-WebGL frame; assembly observes148/98,100, matching unchanged geometry counts. No physical-device FPS claim is made.
- Physical mobile testing is excluded by the owner's explicit instruction. Full Game46/46 and experience31/31 PASS with no filters or page errors. The local gallery loop covered558 entries; required remote gates will cover the final561-entry release.

## Reusable prevention

The [planar-cap prevention note](../blender-planar-cap-normals.md) records the reproduced pattern, root cause, insufficient flat-cap-only comparison, shared source operation, independent exported-normal check, known-axis requirement, native visual evidence and bounded Skill-search decision. This is project documentation, not an unverified global Skill or user-memory update.

## Remaining acceptance

Main85448e31 synchronization,638 unit checks, fresh build and exact-payload desktop/tablet Viewer profiles pass; Game/main style/Viewer implementation remains unchanged. Review the complete scoped diff and commit this model separately and verify main, required Actions and actual production before the next model. The campaign remains incomplete.

## Render packaging

Four overview/detail contact sheets and `shading-comparison.jpg` retain the inspected views. Six full-resolution native cap/side PNGs and four actual Viewer images are committed. `render-publication.json` hashes all52 native PNGs and records retained local paths for omitted files. Numerical comparisons and the separate visual review used native files before packaging. Reproduce renders from the recorded source hashes, settings and QA scripts; no temporary model variants are published.

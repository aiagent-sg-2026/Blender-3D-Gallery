# MODEL-0010: Ball 04

Status: TESTING. Selected only after MODEL-0009 passed required Actions 43683566612, deployment and actual production acceptance. Baseline: 1e942079. No confirmed product defect or required repair has been found. Full Game/experience regression recovery remains pending; this model has not been committed or released by the campaign.

## Inspection and preservation

ASSET_Ball_04 has a 57.15 mm purple resin body, two opposite ivory medallions and two black numeral 4 surfaces: five meshes and 5312 triangles. The physical sphere is closed, has positive signed volume and smooth outward normals. Each medallion has 432 triangles and 48 intentional boundary edges; each numeral has 240 triangles and 60 intentional boundary edges. No degenerate triangles, loose vertices, inconsistent winding or nonfinite UV coordinates were found. Number layers remain 50 and 90 microns outside the resin sphere. Their extent explains the slightly larger decorated bounding box; body diameter is checked separately.

Raw imported numeral connectivity includes 194 components from normal/UV vertex splits. Disposable position welding at 1e-7 m restores one component per mesh and the original boundary counts. Source and GLB remain unchanged. The shared inspector now reports welded connectivity using the same component-counting procedure as its raw metric, so seam splits can be distinguished from disconnected product geometry.

Original opaque, untextured dielectric materials are preserved: purple linear RGB (.22, .035, .37), roughness .23; ivory .24; black ink .29. Image-texture atlas/stretch checks are N/A without image textures. The model is static and unrigged, so authored animation is N/A; Game interactions need their separate regression gate.

Original leaf SHA-256: `f3551b4d3ebd39f8eeb0ac78dc3a83e8742b4e3e5515eaa6db4d456c0bbc8e85`, 157064 bytes. Original source, generator, previews, leaf and assembly hashes are preserved in original-manifest.json; all 22 sibling GLBs are unchanged and backed up. See artifact-preservation.json.

The leaf, full assembly and fresh scratch export each pass glTF Validator with zero errors and warnings. Fresh export differs only in triangle index submission order: complete JSON and non-index bytes agree, and all 5312 oriented triangles, including winding and multiplicity, match. This is semantic replay, not byte-exact reproduction. The unchanged comparator's negative controls remain recorded under MODEL-0007; no new control run is claimed here.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 1 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python docs/model-qa/MODEL-0010/export-replay.py -- /tmp/ball04-replay
```

## Completed local gates

- 678 unit tests, 45 targeted billiards tests and the 567-asset build pass. Unit concurrency 2 preserves every test and assertion while limiting host resource pressure.
- Four standalone/assembly desktop 1440x900 and tablet 768x1024 Viewer profiles pass original payload hashes, rotation, zoom and exact reset with no page or HTTP errors. The sampled standalone software WebGL frame has five draws and 5312 triangles. ReadPixels diagnostics do not establish hardware performance; physical-device FPS is not claimed.
- Seven source and seven standalone-reimport angles plus three contact angles for both source and imported assembly were rendered at the established quality settings. Both numeral sides are legible. Actual source/import cloth separation is 5.960464477539063e-8 m, supported separately by the real-cloth-triangle geometry test.
- Independent visual review accepts at 89/100 with no evidenced P0/P1/P2 or required P3. Primary inspection agrees. All 20 native views were independently inspected before packaging; eight native PNGs and four contact sheets are retained, and every native is archived locally with a verified hash. Ten native matched comparisons have a maximum mean RGB channel error of 0.0021641666666666667/255, descriptive only.
- Physical mobile testing is excluded by the owner for the campaign.

## Full regression recovery

The first host Game run failed while saving the winner-case screenshot, after observing the correct finished/winner state. Its original 30000 ms screenshot timeout was retained. Host load was elevated at the failure observation; resource causality is a supported suspicion, not a proven product root cause. Experience did not run because the first command failed. No fresh Game results JSON was written; an older shared result file predating this run was explicitly excluded. See game-first-attempt.json and game-first-attempt.log.gz.

Recovery uses the original, unfiltered browser scripts and fixed Node 24.21.0 in an isolated Linux workspace at pinned application revision 1e942079. Each suite gets a unique TEST_ARTIFACT_DIR. The first isolated setup failed before tests because nested npx inherited incompatible npm exec options. Direct invocation of the installed CLIs corrected that startup issue. A second setup exposed omitted non-catalog LOD/customization/solar-demo inputs in the recovery checkout; the complete models directory is now included. Original assertions, inputs, viewport coverage and timeouts remain unchanged. These setup attempts are not counted as test passes. See remote-regression.json and the recorded recovery commands.

Full Game and experience acceptance, publication, required final-commit Actions and production acceptance remain pending. MODEL-0011 has not started. The full inventory campaign remains incomplete.

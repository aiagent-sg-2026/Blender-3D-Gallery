# MODEL-0009: Ball 03

Status: PUSHED. QA-only commit2b8d7e10 is verified on main; required Actions43683566612, deployment and final-release production acceptance all pass. No confirmed product defect; source, generator, previews and all22 GLBs remain unchanged. Selected only after MODEL-0008 QA release582a37a0 passed required Actions43673948892, Pages and complete isolated production acceptance. Inspection baseline6982fb07 had1889 records/564 catalog assets. The pure append sync7f6291a7 now has1892 records/567 catalog assets; all additions remain PENDING. Originals are preserved in original-manifest.json.

## Inspection and decision

ASSET_Ball_03 contains a57.15mm red resin body, two opposite ivory medallions and two black numeral3 surfaces. Five meshes total6400 triangles. The physical body is closed with positive signed volume and smooth outward normals. Curved decorative surfaces are intentional open paint layers50microns and90microns outside the body radius; each medallion has48 and each numeral3 has204 boundary edges. Source components and position-welded reimport topology agree. No degenerate triangles, inconsistent winding, loose vertices or nonfinite UVs were found. Direct tests check body radius/normals, both marks, outward winding and actual cloth-triangle support within1micron.

Original opaque untextured dielectric materials are preserved: red linear RGB(.61,.018,.025), roughness0.23; ivory0.24 and black ink0.29. Texture atlas/stretch checks are N/A without image textures. The root is static and unrigged; model animation is N/A. Applicable Game interactions are covered by regression separately.

## Export and preservation

Original leaf SHA256: a78935075c2b991166b60fd9b4fba5248e5baf8c1fefa4ef2eec54a754701352; 268828bytes. Original leaf, assembly and fresh scratch export each pass glTF Validator with zero errors and warnings. Fresh export differs only in triangle index submission order: full JSON and all non-index binary bytes are identical; all6400 oriented triangles, including winding and multiplicity, match. This is semantic replay, not byte-exact replay. The unchanged comparator's controls are recorded in MODEL-0007/export-comparison-controls.json; no new control run is claimed here.

Replay without saving source or replacing original products:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 1 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python docs/model-qa/MODEL-0009/export-replay.py -- /tmp/ball03-replay
```

## Current checks

- 670 unit tests and40 targeted billiards checks PASS. Unit concurrency2 reduces host resource pressure while preserving every test and assertion; required CI also passes all670 tests using its standard command.
- Four desktop1440x900 and tablet768x1024 standalone/assembly Viewer profiles pass exact original payload and controls, without page/HTTP errors. Standalone268828bytes,5draws/6400triangles in sampled software WebGL. Physical-device FPS is not established.
- Seven source and seven standalone-reimport angles are rendered and inspected; both numeral3 sides are legible. Detailed contact rendering was serial, low-priority and single-threaded to reduce host load; quality settings are unchanged. Source and imported contact separation is5.96e-8m. Independent review accepts at89/100; primary inspection agrees. All20 native views were inspected before packaging; eight native PNGs and four contact sheets retained, all originals archived with hashes. Ten native matched pairs show maximum mean RGB channel error0.0021370833333333333/255, descriptive only. Full unfiltered Game46/46 and experience31/31 passed at6982fb07, including all564 catalog previews/downloads. Upstream7f6291a7 changes only appended resources: every old asset, collection field/order and application/dependency/billiards file is identical. A fresh670-unit run,567-asset build, four current-model Viewer profiles and nine additional desktop/tablet/fallback checks cover the three additions, including exact download hashes. See upstream-sync.json and upstream-regression.json. These additions remain PENDING for individual deep QA. Required CI now passes its complete unfiltered release suite on commit2b8d7e10 at567 catalog entries; see ci-summary.json and actions.log.gz.
- Physical mobile testing is excluded by the owner.

Main publication, original GLB blob, required Actions and actual production acceptance are verified. Both actual payloads match the original standalone and assembly hashes; four fresh desktop/tablet profiles and five downloaded-file geometry/contact tests pass. All18 production artifact hashes and four test-script digests were verified after transfer, and primary inspection of actual production screenshots found no new defect. See release-evidence.json, live-deployment.json and remote-execution.json. Commit2b8d7e10 remains an ancestor of main1e942079, whose queue-stanchion repair changes no application, catalog or billiards files. Those three upstream models remain PENDING. Closure metadata will travel with the next validated campaign commit. Full campaign remains incomplete.

The full-gallery smoke harness now reports progress after each25 checked resources and at completion. This stdout-only change preserves all assertions, inputs and timeouts; syntax checked. The full baseline run started before this logging addition. Required CI executed the final script successfully and reported1134/1134 existing DOM preview/download iterations; that iteration count is not a unique-model count.

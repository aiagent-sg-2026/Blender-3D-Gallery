# MODEL-0008: Ball 02

Status: PUSHED / accepted. QA-only582a37a0 is verified as a main ancestor; Actions43673948892 and Pages deployment succeeded. Complete production acceptance passed in isolated Ubuntu with the original scripts, four fresh browser profiles and five downloaded-file tests. MODEL-0009 had not begun at acceptance. No confirmed product defect; source, generator, previews and all22 GLBs remain unchanged. Selected only after MODEL-0007 QA release ed66da5e passed Actions43669406927, Pages deployment and actual standalone/assembly production acceptance. Originals are preserved in original-manifest.json.

## Inspection and decision

ASSET_Ball_02 contains a57.15mm blue resin body, two opposite ivory medallions and two black numeral2 surfaces. Five meshes total5824 triangles. The physical body is closed with smooth outward normals. Curved decorative surfaces are intentional open paint layers50microns and90microns outside the body radius; medallions have48 and numeral2 surfaces132 open boundary edges each. Source connected components and position-welded reimport edge topology agree. Zero degenerate triangles, inconsistent winding, loose vertices or nonfinite UVs were found. Direct tests check body radius/normals, both marks, their outward winding and true cloth-triangle support within1micron.

Original opaque untextured dielectric materials are preserved: blue resin linear RGB(.015,.09,.55), roughness0.23; ivory0.24 and black ink0.29. Texture atlas/stretch checks are N/A without image textures. The root is static/unrigged; animation is N/A, with applicable Game interactions covered separately. Source contact render records separation5.96e-8m above the actual cloth.

## Export and preservation

Original leaf SHA256: 4c541de60d4d2641a316ca4e635d2329994a45de751e78d06d6cd01a27a7202a; 215296bytes. Original leaf, assembly and fresh scratch export each pass glTF Validator with zero errors and warnings. Fresh export differs only in triangle index submission order: full JSON and all non-index binary bytes are identical; all5824 oriented triangles including winding and multiplicity match. This is semantic replay, not byte-exact replay. The unchanged comparator's negative-control evidence is MODEL-0007/export-comparison-controls.json; no new control run is claimed here.

Replay without saving or replacing original products:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 2 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python docs/model-qa/MODEL-0008/export-replay.py -- /tmp/ball02-replay
```

## QA candidate checks (582a37a0)

- 661 unit tests and35 targeted billiards checks PASS. Shared assertNumberMarks in tests/helpers/ball-geometry-checks.mjs owns the same unchanged geometric criteria for Ball01 and Ball02. The existing Ball01 five checks remain active and passing; Ball02 adds five.
- Desktop1440x900 and tablet768x1024 standalone/assembly Viewer loading and controls pass in four fresh profiles. The exact original standalone payload is215296bytes; sampled software WebGL shows5draws/5824triangles. No physical-device FPS claim.
- Seven source and standalone-reimport views plus three marked-face/contact views each for source and assembly are rendered. Primary overview, both marked-face and grazing inspection finds no required repair. Independent review accepts the existing product at89/100; primary inspection agrees. All20 native views were inspected before packaging; eight native PNGs and four contact sheets retained, all originals archived with hashes. Ten matched native pairs show maximum mean RGB channel error0.002135/255 (descriptive only). Full current Game46/46 (including561 catalog resources) and experience31/31 PASS without filters or page errors.
- Physical mobile testing is excluded by the owner.

Main publication and original GLB blob are verified. Required Actions and complete production acceptance passed; see release-evidence.json. Closure metadata will travel with the next validated campaign commit. No later model may start until those gates pass. Full campaign remains incomplete.

Upstream main was safely fast-forwarded to 6982fb07; billiards source/exports and this test harness are unchanged. Eight new tracked 3D artifacts append five PENDING records across two reconciliations; no additional model was inspected. The first local live run failed at full-page screenshot capture under host load254/swap10.6GB and is retained in live-first-attempt.json/log.gz. That attempt is not accepted. The isolated Ubuntu recovery passed all original checks with unchanged timeouts; see remote-recovery.json, live-deployment.json and the retained screenshots/logs.

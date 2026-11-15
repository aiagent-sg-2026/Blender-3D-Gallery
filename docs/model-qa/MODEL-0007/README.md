# MODEL-0007: Ball 01

Status: READY_TO_PUSH. No confirmed product defect; source, generator, previews and all22 GLBs remain unchanged. Selected only after MODEL-0006 QA release e23be21c passed required Actions43664847183 and actual production acceptance. Originals are preserved in original-manifest.json.

## Inspection and decision

ASSET_Ball_01 has a57.15mm yellow resin body and two opposite ivory medallions with black numeral1. The five meshes total4896 triangles. The body is closed with outward smooth normals. The four decorative overlays are intentional curved, open surfaces, offset50microns and90microns from the body radius. Their outward winding, finite UVs, footprint and layering pass direct checks in the standalone and assembly.

Raw glTF vertex connectivity includes normal/UV splits. An initial ad-hoc raw-components assertion was inapplicable to those splits. Exact-identical-position connectivity is one component per mesh; position-welded body topology is closed and intended overlay boundaries match source. See geometry-assessment.json and welded-connectivity.json. No vertices were changed to satisfy inspection.

Three original opaque, untextured dielectric materials are preserved: yellow resin roughness0.23, ivory0.24 and black ink0.29. Texture stretching/atlas checks are N/A because no image textures are used. The source and imported body sit on actual cloth triangles within1micron; contact diagnostics measure source separation5.96e-8m. The root is static and unrigged; model animation is N/A, while applicable Game interactions are covered separately.

## Export reproducibility

The original leaf remains3283df10e89d9d37ef384045d45885331b46917253a110175725f16f5bbd897a,120536bytes. Fresh export has different triangle submission order and therefore a different hash. Full JSON and all non-index bytes are identical; all4896 oriented triangles, including winding and multiplicity, match. This is semantic replay, not byte-exact replay. Negative controls reject changed positions and reversed winding.

Reproduce without saving or replacing product files:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --disable-autoexec --threads 2 models/eight-ball-billiards/scene.blend --python-exit-code 1 --python docs/model-qa/MODEL-0007/export-replay.py -- /tmp/ball01-replay
```

The guarded replay uses scripts/glb-index-order-equivalence.py for all five primitives. Original leaf, assembly and scratch export each pass glTF Validator with zero errors or warnings. Original files are independently checked against recorded hashes.

## Current checks

- 656 unit tests and30 targeted billiards checks PASS. The previous cue-ball's three assertions remain active through tests/helpers/ball-geometry-checks.mjs; five new Ball01 tests check the body, marks and true support contact.
- Desktop1440x900 and tablet768x1024 Viewer controls, exact payload hash and reset image PASS with no page/HTTP errors. Sampled software WebGL shows5 draws/4896triangles. Asset size120536bytes.
- Seven source and seven standalone-reimport angles plus three detailed marked-face/contact angles for source and assembly are rendered. Independent review accepts the existing asset at89/100; primary inspection agrees. All20 native views were reviewed before packaging, with eight native PNGs and four contact sheets retained. Ten matched native pairs show maximum mean RGB channel error0.00209/255 (descriptive, not a quality threshold). Full current Game46/46 (including561 catalog resources) and experience31/31 PASS without filters or page errors. Assembly runtime also passes both desktop/tablet profiles.
- Physical mobile testing is excluded by the owner. Desktop software rendering does not establish physical-device FPS.

Main publication, required Actions and actual production acceptance remain pending. No later model may start before those gates pass. Full campaign remains incomplete.

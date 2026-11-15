# M057 corner shelf topology repair

Four delivery LODs were checked independently. LOD0/1/2 contained 60/36/24 exact-zero triangles on trim_crown_lip; they now contain zero. Triangle counts are 13,620 / 4,908 / 2,008 / 576. LOD3 and the separate collision GLB are byte-identical to their originals. optimized.glb remains an exact LOD0 alias. Byte sizes are unchanged because unused buffer capacity is retained.

The editable source retains 78 child objects, 42 semantic meshes, 24 product anchors and both packed PNG textures. An additive cleanup modifier on trim_crown_lip uses Clip for concave caps to retain the original diagonals. Original source geometry, bevel settings, materials, UVs, image bindings/packed bytes and scene state were fingerprinted before/after/reopen. LOD1/2 source oracles derive only their documented bevel segment levels from the original saved LOD0.

All three native source exports and strict canonical comparisons pass. Canonical filtering changes only triangle indices/accessor counts; effective surface positions, shading normals, UVs, embedded PNGs and all other binary payloads remain unchanged. The older exporter emitted six material records, including two equivalent Warm wood definitions through duplicate texture aliases; the native exporter deduplicates them to five. The comparison resolves actual image SHA and sampler definitions before accepting equivalent same-name records. Negative controls reject changed image bytes or distinct same-name PBR definitions.

The shared source fingerprint now includes writable scalar modifier settings and packed-image hashes. The Node PNG structural loader was extracted behind its existing compatibility import. It validates PNG headers and dimensions; it does not decode pixels. Real browser/visual verification is separate.

Fresh native generation exercises all four LODs, collider, two textures, stable anchors, label-rectangle visibility, actual L-footprint/notch raycasts, rear-spine/LED contact and budgets through the production validator. All four delivered LODs re-import in Blender 5.1.2 with zero degenerates; the cleanup is idempotent.

A real LED_1_A source edit was saved/reopened/exported and compared with an unchanged same-toolchain export. Exactly one part's position/normal/index geometry changes; 41 siblings match. Four sibling UV values differ by at most 1.863e-9 during native evaluation (explicit 1e-7 UV guard). Only the intended shared Warm LED diffuser roughness changes to 0.71. All original source/export/texture hashes remain unchanged by the edit probe. Previous reports/source-edit artifacts are retained as historical evidence; source-edit-current is the current probe.

- [Four-LOD structural acceptance](assets.json), [native fresh/import regression](native-regression.json), [fresh generation log](fresh-generator.log)
- [LOD0 source preservation](source-repair-lod0.json), [LOD1](source-repair-lod1.json), [LOD2](source-repair-lod2.json)
- [LOD0 native comparison](source-comparison-lod0.json), [LOD1](source-comparison-lod1.json), [LOD2](source-comparison-lod2.json)
- [LOD0 canonical comparison](delivery-comparison-lod0.json), [LOD1](delivery-comparison-lod1.json), [LOD2](delivery-comparison-lod2.json)
- [LOD0 index filtering](index-repair-lod0.json), [LOD1](index-repair-lod1.json), [LOD2](index-repair-lod2.json)
- [Pre-fix regression](regression-before.log), [tool controls](tool-controls.log), [rejected material alias assumption](rejected-material-alias-check.json)
- [Saved-source edit](sources.json), [edit verification](source-edit-verification.json), [final verification ledger](verification.json)

Existing previews remain valid because canonical visible surfaces and textures are unchanged. These checks do not establish physical-device support, FPS, deployment, load capacity or certification.

695 JavaScript tests and the repository build passed. Three Gallery cases (1440/768/390) and two focused M057 Inspector cases passed on local Chrome/ANGLE Metal, including actual consumed GLB hashes, manual LODs, row highlight, LED/title/reset, ownership/resource cleanup and load-failure/race recovery. Gallery 1440/390 and Inspector desktop images were inspected. Earlier bundled Chromium/SwiftShader attempts timed out/hung; their available failure log is retained, without assigning an unverified cause. See the verification ledger for exact scope.

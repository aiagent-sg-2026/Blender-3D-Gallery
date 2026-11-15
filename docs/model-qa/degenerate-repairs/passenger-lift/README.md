# Passenger lift topology repair

PASS: four exact-zero glyph triangles removed from fixed Shaft_Label; 7,656 → 7,652 triangles, 422,336 bytes. No positive-area residue exception or index split is needed. Original positions, normals, materials, bounds and all five animation descriptor/accessor payloads are unchanged. All 90 authored child objects (77 Mesh, three FONT, ten Empty) remain editable. Source reopen, fresh production generation and canonical native import pass on matching Blender 4.0.2.

The cleanup target and its ancestors are static. Source snapshots preserve five actions, 15 curves, 45 keys, assignments, interpolation/handles and frame/FPS settings. A real keyframe mutation/restoration exercises the snapshot. The production validator retains exact raw tracks, mutually exclusive door/travel modes, 121 swept-clearance samples per mode, doorway aperture raycasts and both floor alignments. An actual browser renderer repeats 121 samples per mode (242 total), verifies visible movement, exact pixel restoration, absence of errors and exact consumed GLB SHA. Gallery checks independently cover 1440/768/390 and normal controls/lifecycle.

The existing wall edit remains supported: Cab_BackWall moves +0.123 m in local X and shared Brushed steel roughness becomes 0.73. The edited copy is saved/reopened/exported and compared with an unchanged same-toolchain control. All 80 geometry payloads and all five clips match; exactly one node transform and the intended material property change. Canonical files retain their hashes.

The first full run exposed omitted legacy report fields in a registry-driven consumer. They were restored from actual exported node/material values, without changing the consumer's assertions. Current visual-review hashes now point to current source/delivery and actual inspected Gallery/motion images; previous studio review and handoff manifest are preserved under reports/pre-topology-repair. The handoff manifest is regenerated from actual current files. Search report fields and data-driven registries when tracing consumers, rather than relying only on asset-slug searches.

- [Source preservation](source-repair.json), [native comparison](source-comparison.json), [canonical comparison](canonical-comparison.json), [index repair](index-repair.json)
- [Fresh native regression](native-regression.json), [fresh/canonical comparison](fresh-comparison.json), [pre-fix regression](regression-before.log)
- [Rejected report-contract run](rejected-report-contract.log.gz), [restored contract regression](contract-regression.log.gz)
- [Current asset checks](../../../../models/passenger-lift/reports/assets.json), [mechanism checks](../../../../models/passenger-lift/reports/mechanism.json), [saved source](../../../../models/passenger-lift/reports/source.json), [saved edit proof](../../../../models/passenger-lift/reports/source-edit-export-proof.json)
- [Gallery cases](gallery-browser.json), [motion cases](motion-browser.json), [verification ledger](verification.json)
- [Desktop](gallery-1440.png), [390px](gallery-390.png), [doors open](doors-mid.png), [cab at upper floor](travel-mid.png)

Original studio previews are reused for unchanged meaningful surfaces. The new source was reopened/exported but not rerendered in Cycles. Actual current delivery frames were inspected. The browser motion harness now records its actual platform/launch options instead of a hard-coded Ubuntu/SwiftShader claim.

Reproduce native checks with Blender 4.0.2: --background --threads 2 --python-exit-code 1 --python models/passenger-lift/test_degenerate_cleanup.py -- /new/owned/output. Run inspect_sources.py and verify_source_edit.mjs for the saved edit. Node gates are tests/passenger-lift-degenerate-repair.test.mjs, tests/gapextract06.test.mjs and tests/mall-degenerate-repairs.test.mjs. After the normal build, use scripts/test-mall-degenerate-browser.mjs with MALL_QA_ASSETS=passenger-lift and browser-motion.mjs for the isolated sweep; local evidence uses Chrome/ANGLE Metal.

No operational elevator, new Gallery component controls, phone/FPS, deployment or safety certification is claimed. Draft status, mutually exclusive animation modes and existing physical-device limitations remain unchanged. Raw failure logs retain original whitespace.

# Report contract retention

Bug pattern: a richer producer report drops required fields read by existing consumers.

Root cause: consumer discovery searched the asset slug; the failing consumer loads a shared registry and reads edit_proof.material_roughness_survived_save_reopen_export plus current visual/source/GLB identities. The new report omitted that field.

Fix: keep the existing schema, derive its legacy fields from the actual saved/exported node and material, archive historical review/manifest snapshots, and update current identities only after current visual evidence is inspected. Keep consumer assertions intact. The source-edit verifier additionally proves unrelated geometry, transforms, materials and clips remain unchanged.

Regression: unchanged tests/gapextract06.test.mjs now passes, along with the focused source-edit/handoff checks and the complete 717-test suite. The first failing run is retained as rejected-report-contract.log.gz.

Prevention: trace consumers by schema fields, report filenames and registry loaders as well as the asset slug. Read the current artifact shape before rewriting it. Make extensions additive or introduce an explicit migration; do not silently replace a protocol or suppress its tests. Reusable guidance is queued for the existing canonical Blender KB procedure after campaign acceptance.

# Food court tray station topology repair

PASS: 2 exact-zero triangles removed; 5,412 → 5,410 triangles, 353,656 bytes. Canonical vertex attributes, normals, materials, roots and bounds stay unchanged. No residue tolerance exception or shared-index split is needed.

Matching Blender 4.0.2 preserves all 23 source objects, two editable FONT labels and 13 modules. Applying cleanup before the established welded FONT evaluation changed 676 oriented triangles and was rejected. The accepted exporter temporarily disables only its own source cleanup with try/finally, retains legacy evaluation, restores modifier flags, then cleans the disposable joined SignText. Authored fingerprints match before/after export and reopen. Fresh production generation, idempotence and clean canonical native reimport pass.

Existing report contracts and production checks remain in place: counter support, 1.36 m opening, two 0.33 m shelf clearances, four hollow trays, stacking gaps and collision-free 0.62 m tray removal. A real counter vertex edit, Tray04 material edit and ReturnLabel edit survive save/reopen/export; ten sibling modules are unchanged.

28 targeted tests, build and three Gallery viewports pass. Actual loaded GLB SHA, orbit, zoom, exact reset/reopen, lifecycle cleanup, focus and no console/network errors are checked. Current 1440/390 images were inspected. The first browser pass overlapped an unfinished build and correctly detected old bytes/404; its failures are retained and all three cases pass on the completed fixed build. Build must finish before launching consumers.

See [verification](verification.json), [source preservation](source-repair.json), [source geometry](source-comparison.json), [canonical preservation](canonical-comparison.json), [index receipt](index-repair.json), [fresh native checks](native-regression.json), [browser checks](gallery-browser.json), [desktop](gallery-1440.png), [390px](gallery-390.png). Run test_degenerate_cleanup.py with Blender 4.0.2 and a new owned output directory; inspect_sources.py plus verify_source_edit.mjs retain the real edit workflow.

Original studio previews are reused for unchanged meaningful surfaces. No physical phone/FPS, deployment or hygiene/safety certification is claimed. The existing unrelated demo reload limitation remains documented. Raw pre-fix logs retain original whitespace.

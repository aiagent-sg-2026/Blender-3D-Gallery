# M060 Shelf Inspector local QA

Candidate base `03366093`, building on queued M059/M058 work. Not remote CI, deployment or physical-device evidence.

## Scope

Adds the fifth explicitly enumerated fixture M060. Dimensions 2.4 × 0.55 × 2.4 m; two bays, six boards grouped into three row controls, eight LEDs, one anchored 1.92 × 0.36 m concept header, eighteen static product anchors. Core parts/page/loader unchanged: existing group traversal handles both child meshes. Independent four-LOD URL registration does not preload all exports. No geometry, catalog, CI or publication queue changes by this slice.

## Verification

Job `9a1d577f-5456-4fc4-a321-17de90876d37` succeeded 2026-11-14 19:45:52–19:47:06 UTC:14 relevant unit tests, build, affected M057/M058/M059 explicit option-list cases and new M060 desktop/mobile cases. Gallery three-width checks already passed for these final GLBs and same Viewer baseline, so were not repeated.

Tests retain exact five IDs/options and existing assertions. New grouped-row unit checks each of the three row selections applies highlight to both named board meshes and no other row, restores source materials, toggles all eight LEDs, and disposes the sole overlay. Browser cases verify all four actual GLB hashes, title/highlight/LED state, five-fixture repeated switching with exact GPU equality, obsolete delayed M060 response superseded by a different fixture and final M060LOD3, blank pending scene, reset and exact original image, context loss,390px touch controls and viewport width.

Actual final desktop/front/side/mobile screenshots inspected: two bays/six boards and central support are visible, DOUBLE BAY COLLECTION reads fully without mirroring or occlusion, no observed inner-face striping; mobile model and heading fit. Evidence under `qa/shelf-inspector-m060/`. LOD0 SHA256 `cb45dcc4711e6e3b87c7e5b75ef5530d33ae123cd25d6716481a67da909b102f`; all hashes recorded in validated-files.json.

## Limits

Chromium desktop and390px touch emulation, not physical Android/iOS/Safari. Manual LOD only. No product loading or auto-assembly; anchor count is not product rendering. LED controls change emissive materials, not photometric lighting. README/support-manifest/nested metadata updated only after local test and image review.

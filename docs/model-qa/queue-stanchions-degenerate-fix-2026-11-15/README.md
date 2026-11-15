# Queue stanchion axis-cap repair

Completed 2026-11-15, Asia/Singapore. Scope: `mall-queue-post`, `mall-queue-short` and `mall-queue-long`, their saved Blender sources, shared generator and measured metadata. The original repair verification below preceded Git publication; release checks are recorded separately in [release-validation.json](release-validation.json). No deployment is claimed.

## Result

| Asset | Zero-area triangles before → after | Total triangles before → after | GLB bytes before → after |
| --- | ---: | ---: | ---: |
| Post | 480 → 0 | 3,344 → 2,864 | 97,912 → 71,736 |
| Short bay | 960 → 0 | 7,252 → 6,292 | 191,180 → 154,488 |
| Long bay | 960 → 0 | 7,252 → 6,292 | 192,444 → 149,808 |

The repair removes 2,400 zero-area triangles. It preserves every original nondegenerate oriented/material triangle under a 1e-6 m positional quantization comparison, all material definitions by unique name, bounds, post spacing, belt endpoints and module origins. Source objects remain separately editable: 10/23/23 parts. Existing previews and layouts are unchanged. This does not assert that every coincident seam or component must form a single printable solid.

## Cause and change

The old lathe emitted 48 coincident vertices for each radius-zero endpoint and connected them with quads. Triangulating each collapsed cap quad yielded one useless triangle. Five two-ended radial parts therefore produced `5 × 2 × 48 = 480` degenerate triangles per post.

`lathe_geometry()` now emits one axis vertex and correctly wound cap triangles. Positive-radius ring bands retain their original quads; other seams/profile geometry are unchanged. `POST_LATHE_PARTS` supplies the same dimensions to generation and the controlled migration. Export logic is shared between fresh builds and repair of saved sources.

`repair_caps.py` repaired 25 mesh datablocks in separately staged copies. It required matching legacy profile coordinates and face connectivity, smooth/material assignment, and absence of unsupported shape keys, UVs, custom normals and modifiers on those target meshes. Non-target mesh geometry, material inputs, transforms, object properties, module assignments, selection, cursor, scene units and camera assignment were fingerprinted before/after and after reopening the saved source. Original-source scene content was not rebuilt. The current source file format/tool version is Blender 5.1.2; original 4.0.2 provenance remains in metadata.

## Evidence

- [Source preservation and reopen results](source-repair.json); [measured assets](measured-assets.json).
- [Manual topology edit refusal](manual-topology-refusal.json): deleting a saved face while retaining legacy vertex coordinates is rejected before export, and the input stays unchanged. [Positive guard recheck](source-guard-recheck.json) covers all three original sources.
- [Actual final GLB comparison](final-glb-comparison.json): zero errors/warnings, zero degenerate triangles, valid normals, unchanged nondegenerate oriented/material surfaces, bounds and module pivots.
- [Native cylinder regression](lathe-regression.json): originally failed with 96 zero-area triangles; now passes with 98 vertices, 192 nondegenerate triangles, no boundary/non-manifold edges and the expected signed volume. [Actual exported-asset regression before](exports-regression-before.log) failed on all three old exports; [focused tests after](exports-regression-after.log) passed 12/12, including layout/socket alignment.
- [Build](build.log): all asset validation and Vite build passed. Output was isolated in a temporary directory; the shared `dist` directory was not replaced. The existing large-chunk advisory remains.
- [Real browser results](browser-results.json): Chromium 156.0.8078.4 / SwiftShader, actual built deployment subpath, 1440/768/390 px. All 12 discovery/viewer cases passed, including consumed GLB SHA-256, orbit, zoom, reset, reload and close/disposal checks. [Browser log](browser.log). This is viewport testing, not physical-phone or FPS acceptance.
- [Full source/delivery geometry inspection](after-inspection/execution.json), [final verification](verification.json).

Three desktop model screenshots were visually inspected: [post](screenshots/mall-queue-post-1440-initial.png), [short](screenshots/mall-queue-short-1440-initial.png), [long](screenshots/mall-queue-long-1440-initial.png). They are actual Viewer captures, not Blender-only source renders. Complete browser artifacts remain under `output/playwright/queue-cap-repair-2026-11-15` locally.

The first comparison incorrectly required the same material-array order; the new exporter reordered otherwise identical named definitions. [That failed check](initial-material-order-check.json) is retained. The corrected comparison requires unique names, identical named definitions and identical oriented surface/material assignments, so a reassigned or changed shader still fails. No expectation was relaxed for geometry, normals, pivots or dimensions.

The broader local mall audit (`docs/model-qa/shopping-mall-2026-11-15`) remains a separate pre-repair snapshot and is outside this release. Its other findings, native n-gon density limitations and source-version caveats are not claimed fixed here. The queue assets are image-texture-free, so image texel-density acceptance is N_A. No runtime retraction, physics, crowd-control certification or redistribution grant was added.

## Reproduce

Run from the repository with its installed Node dependencies and Blender 5.1.2:

```sh
blender --background --factory-startup --disable-autoexec --threads 2 --python-exit-code 23 --python models/mall-queue-stanchions/test_lathe.py
node models/mall-queue-stanchions/validate.mjs
node --test tests/mall-queue-stanchions.test.mjs tests/mall-floor-direction-sign.test.mjs
npm run build
MALL_QA_DIR=/absolute/new-browser-evidence node scripts/test-mall-queue-stanchions.mjs
```

The legacy migration requires the old saved sources and distinct output/evidence paths. It intentionally fails rather than overwrite an unfamiliar/manual source shape. The [initial generator](initial-generator.py) and baseline hashes are retained as historical evidence, not the current generation entry point.

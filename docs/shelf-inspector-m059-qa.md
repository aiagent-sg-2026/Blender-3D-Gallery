# M059 Shelf Inspector QA

Final local candidate `e124bc9f`, based on queued M058 candidate `44aaed6a` including Viewer changes. Not a CI, deployment or real-device result.

## Implementation

Fourth explicitly named fixture M059, preserving M056/M057/M058. Actual dimensions are **0.8 × 0.55 × 2.4 m**, explicitly a narrow interpretation rather than the original repeated 2.4 m width. Three shelves, five LEDs, one 0.50 × 0.36 m anchored header, four independent LOD exports, six static product anchors. Only selected fixture/LOD is loaded. No change to core parts, page, loader, geometry, catalog or CI by this runtime slice.

## Failure retained and corrected

Initial job `d09c22d5-ebb2-41cf-b12c-c351242eb774` passed 13 units/build and four relevant browser cases. Actual side-view inspection nevertheless found dense striped artifacts on inner side faces: **visual FAIL despite automated PASS**. The asset worker confirmed coincident visible pillar/lining surfaces separated by only about 1.4e-8 m, corrected them to real 4 mm lining and fitted shelf ends, and added an asset regression check. No camera, renderer or screenshot tolerance was changed to conceal the issue. Original side screenshot and automated result remain in `qa/shelf-inspector-m059/before-side-visual-fail.webp` and `initial-automated-pass-visual-fail.json`; original full PNG remains under output/shelf-inspector-m059.

## Final evidence

Job `d2135aa6-28a9-4299-9ef4-20f2dc1ff7a6` (2026-11-14 19:08:58–19:09:57 UTC) succeeded: related units, build, final Gallery1440/768/390, `narrow-controls-lods-and-ownership` and `narrow-touch-viewport`. Existing M057/M058 exact option cases passed in the initial job; no further option changes were made, so they were not redundantly repeated. All explicit four-ID equality and strict resource assertions remain.

Checks cover real four-LOD hashes, title/highlight/LED state, exact reset image, repeated four-fixture switching with strict GPU equality, delayed obsolete load superseded by a different fixture and final LOD, pending-scene clearing, reset after interruption, context loss on leaving, header source-material ownership and overlay disposal. Touch interaction and width checked at390px.

Actual final default/front/same-angle side/mobile screenshots inspected: inner-side stripes are gone, pillar/lining/shelf boundaries intact, title complete in front/default views, model fits mobile viewport. Final LOD0 hash begins `f72af2d8`; full actual four-file hashes and compact screenshots are in `qa/shelf-inspector-m059/`. Gallery final output is `models/gjh-m059-premium-wall-shelf-narrow/reports/browser-final-inspector`.

## Limits

Chromium desktop and touch emulation only, not physical Android/iOS or Safari. Manual LOD, no automatic LOD. No external product loading/auto-assembly; static anchors are not an interaction claim. LEDs are emissive material controls, not photometric simulation. README/manifest/metadata describe only verified local support, not deployment.

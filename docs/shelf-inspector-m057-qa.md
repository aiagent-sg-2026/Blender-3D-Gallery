# Shelf Inspector: bounded M056 + M057 support

## Implemented scope

The existing `?page=shelf-inspector` demo now has a native Fixture selector for exactly GJH-M056 (straight) and GJH-M057 (90-degree corner). M056 remains the initial selection. Each fixture uses its own manifest and four real GLB exports; no automatic LOD or product population is implied.

M057 UI explicitly states the implemented 1.2 × 1.2 m footprint, 0.55 m local arm depth and 2.4 m height. This is the documented corner interpretation, not a claim that its outer bounds equal the original repeated 2.4 × 0.55 m backlog footprint. M056's original dimension text is unchanged.

Shelf highlight, LED state and concept text remain consistent when comparing models/LODs. Reset clears those states and restores LOD0/default camera for the selected fixture, without silently selecting a different model. Changing fixture starts at LOD0. Loading is latest-wins across the captured `(model, LOD)` pair. Old geometry/materials/textures are disposed; one scheduled clear frame removes stale pixels while a new request is pending or failed. No continuous rendering loop was added.

M057 uses three continuous L shelves, ten LED meshes and two explicitly oriented header-surface anchors. Both header faces receive the same complete runtime text. A 0.44 × 0.36 m surface gets a matching 313 × 256 canvas, with balanced two-line words and fitted type. The shipped M056 1024 × 256 title path remains unchanged. No brand assets or baked products were introduced.

## Verification and scope of PASS

- Final relevant unit run: **11/11 PASS** (`tests/gjh-m057.test.mjs` + `tests/shelf-inspector.test.mjs`). This includes perpendicular header orientation, shared texture disposal once, rejection of missing surface descriptors, mixed model/LOD stale-result ownership and narrow-plaque text fitting.
- Final `npm run build`: **PASS**. Existing bundle advisory remains.
- Final Gallery GLB checks: **PASS** at 1440/768/390 Chromium viewport widths, with current exported hashes; see the asset's `reports/browser-front-header`.
- Final `corner-controls-lods-and-ownership`: **PASS**. Four actual corner LOD hashes, label replacement, per-model reset, repeated labeled M056/M057 swaps returning to the same GPU baseline, interrupted corner request superseded by straight LOD3, failed-load scene clearing, retry via other model and teardown are covered.
- Final `corner-touch-viewport`: **PASS**. Real corner model in Chromium touch emulation, native controls, correct states, reset and return to M056; no horizontal overflow.
- The four original M056 browser cases passed in the initial combined run and remain intact in the script. After the isolated M057 plaque changes, only the relevant two corner cases were repeated. The full six-case script remains available to the existing CI gate; this report does not claim that remote CI/deployment has passed.
- Actual images inspected: default diagonal desktop, separate front/side header views, and the touch-emulated mobile viewport. Both faces now show the complete **CORNER / COLLECTION** text, upright and without the earlier side-panel obstruction. Physical Android/iOS, Safari/WebKit and broader accessibility certification are **NOT TESTED** by this report.

## Retained failures and corrections

1. The first pending-scene pixel assertion failed because a canvas locator screenshot includes the overlapping white Loading DOM notice. The actual old model had cleared. The test now excludes only that notice's measured bounding rectangle (plus a one-pixel raster edge) and checks every other interior pixel for a uniform cleared background. It still rejects stale model pixels. The initial failed run remains linked below.
2. Programmatic tests initially passed interactions while the header was visually clipped by deep side panels. This was marked a **visual FAIL**, not accepted as quality. Narrowing a rear-mounted label alone could not satisfy visibility from both required angles. The asset author moved the header fascia forward and added actual-GLB rectangle/raycast visibility checks. Runtime text now matches the narrower surface aspect, instead of compressing a wide texture. Before and after evidence is retained. No camera change was used to hide the obstruction.
3. Failed requests now set `aria-busy=false`, while part controls remain disabled and model/LOD retry choices remain available.

## Evidence

- [Final desktop](qa/shelf-inspector-m057/desktop.webp), [front header](qa/shelf-inspector-m057/front.webp), [side header](qa/shelf-inspector-m057/side.webp), [mobile viewport](qa/shelf-inspector-m057/mobile.webp)
- Earlier clipped labels: [diagonal](qa/shelf-inspector-m057/before-headers-desktop.webp), [front](qa/shelf-inspector-m057/before-header-front.webp), [side](qa/shelf-inspector-m057/before-header-side.webp)
- [Initial runtime results including failure](qa/shelf-inspector-m057/initial-runtime-results.json)
- [Final corner desktop results](qa/shelf-inspector-m057/final-desktop-results.json), [final corner touch results](qa/shelf-inspector-m057/final-mobile-results.json), [final unit log](qa/shelf-inspector-m057/final-unit.log)
- [Validated working-tree and GLB SHA-256 values](qa/shelf-inspector-m057/validated-files.json)

## Reproduce

```sh
node --test tests/gjh-m057.test.mjs tests/shelf-inspector.test.mjs
npm run build
node scripts/test-shelf-inspector-browser.mjs
```

For targeted diagnosis, `SHELF_TEST=corner-controls-lods-and-ownership` or `SHELF_TEST=corner-touch-viewport` selects one scenario. `TEST_ARTIFACT_DIR` selects a new output directory. Tests use the local built app, not a remote production URL. Keep previous failures rather than overwriting them.

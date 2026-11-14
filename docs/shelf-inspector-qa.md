# GJH-M056 Shelf Inspector: focused runtime QA

Status: PASS for the bounded demo in desktop Chromium 156.0.8078.4 and Chromium 390×844 touch emulation. Not a physical Android/iOS or WebKit claim. No remote push or deployment is established by this report.

## Implemented
- Explicit `?page=shelf-inspector` route and independently registered demo, preserving Game, Solar System and Product Studio.
- Three independent shelf highlights, five emissive strip toggle, runtime-only original text header (32 characters), camera orbit/zoom/keyboard/reset.
- Four actual exported LODs selected manually, one active scene. Request cancellation and latest-wins ownership; stale parsed values released. No automatic LOD or loaded products.
- Scoped green/gold paper workbench, accessible native controls, visible keyboard focus and readable dark-gallery heading. Original unbranded geometry/source exports unchanged by runtime.

## Verified commands
- `node --test tests/shelf-inspector.test.mjs tests/registry.test.mjs`: 16/16 PASS.
- `npm run build`: PASS, existing bundle-size advisory retained.
- `node scripts/test-shelf-inspector-browser.mjs`: four scenarios PASS. Includes exact returned GLB SHA for each LOD; one initial selected-LOD request; actual pixel differences for selection/orbit; exact reset pixels; title texture replacement returns GPU counts to warmed baseline; idle rendering stops; all renderer contexts lost on disposal; navigation/reopen; interrupted requests; failed fetch and retry; keyboard; touch and negative gesture cases.
- `SHELF_TEST=mobile-touch node scripts/test-shelf-inspector-browser.mjs`: additional offscreen-scroll-return case PASS without changing the model or controls between screenshots.
- Typical complete focused browser duration: under 30 seconds on this VM. Build adds approximately 5 seconds. CI should run after build with the existing official Playwright Chromium installation.

## Diagnosis and retained failures
1. Initial keyboard Home screenshot differed because programmatic focus inherited pointer modality, while the first key enabled `:focus-visible`. Establishing keyboard focus with Shift before the reference gave identical full PNG hashes before/after Home. Product outline was preserved; no pixels cropped or thresholds relaxed.
2. Playwright `isDisabled()` on the fieldset itself did not describe its HTML disabled semantics. Verified `fieldset.disabled` and actual descendant button `isDisabled()`; failed-load controls cannot activate an obsolete scene.
3. Three.js WebGLState creates four default placeholder textures that are not individually deleted by renderer.dispose. Explicit renderer disposal plus forceContextLoss now invalidates all context resources. Tests assert real `gl.isContextLost()` and program disposal, not pretend every allocation had a delete call. Repeated in-session model/title resources still use exact live-count comparisons.
4. Fast canvas swipe followed by a native button tap produced pointer/touch end but no click. A separate bare HTML canvas/button reproduced it without Three.js. On the same short input, canvas-only non-passive touchstart.preventDefault restored the following native click. The demo now owns only its orbit canvas gesture; no synthetic click, pointer-up action or delay was introduced. An ineffective button touch-action candidate was removed. Tests retain the fast gesture and verify scroll-on-button cancellation, no accidental activation, two native taps, Enter/Space, two-finger canvas zoom and cancellation recovery.
5. Mobile full-page capture can show a blank offscreen WebGL surface. Normal viewport and canvas screenshots both show the model after the same swipe; scrolling to controls and back without interacting retains exact canvas pixels. Full-page images are not used as proof of model visibility. No persistent render loop or preserveDrawingBuffer workaround was added.

## Evidence
- [Desktop inspected view](qa/shelf-inspector/desktop.webp)
- [Touch-emulated viewport inspected view](qa/shelf-inspector/mobile-viewport.webp)
- [Four runtime scenarios](qa/shelf-inspector/runtime-results.json)
- [Scroll-return verification](qa/shelf-inspector/scroll-return-results.json)
- [Initial failed run](qa/shelf-inspector/initial-failure-results.json)
- [Retained touch failure before production fix](qa/shelf-inspector/touch-failure-results.json)

Original full-sized diagnostic captures remain in local `output/shelf-inspector-*` directories. These are not deployment assets. Physical-device testing, automatic LOD, external product loading, official brand/lighting/accessibility certification and full release regression are outside this focused PASS.

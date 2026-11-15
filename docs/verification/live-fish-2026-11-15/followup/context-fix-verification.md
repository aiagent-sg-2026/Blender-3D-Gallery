# Bounded model-viewer rendering resources

## Reproduced production failure

The fish rollout reached Pages in main `345f3104dad5e76bad31c86d63608820a5d65d55`, build `39f0c2cff4635194`. All 180 desktop/mobile fish cases visibly changed pose and paused correctly, but WebKit logged its native WebGL context-limit error from the seventeenth sequential model onward. Strict runtime acceptance therefore failed (136/180 accepted). The old viewer removed its canvas and disposed renderer resources, then created another native context on every open. A direct Chrome inspection also confirmed that closing removed the canvas without losing its native context.

Explicitly losing each closed context was insufficient in a held-handle WebKit stress test: native context accounting still depended on GC timing. The final solution bounds allocations rather than relying on GC or muting the error.

## Ownership and behavior

`src/model-viewer-renderer.js` lazily leases one renderer/canvas and one studio environment to the single gallery model dialog. A lease token prevents a stale asynchronous owner from releasing a newer viewer's renderer. Closing still stops animation, removes owned event listeners, and disposes the model's geometry, materials, textures, skeleton resources, lights and controls. Renderer render lists/state are reset, the canvas is detached, and its idle drawing buffer shrinks to at most 2 × 2 physical pixels (DPR capped at 2). Only the bounded renderer and its shared studio environment remain cached.

The studio environment is identical across these models; its intensity remains per-scene. Sharing it also avoids recreating its GPU integration resources for every fish. GPU handles remain constant after warm-up. Renderer tone mapping, exposure and shadow enablement are reset per lease so vehicle settings do not bleed into another model. Keyboard and context-loss handlers are explicitly removed between leases.

A genuinely lost context is discarded before retry. A non-BFCache page exit destroys the shared renderer/environment and loses its context; BFCache navigation preserves its state for restoration. The first static index still creates no WebGL context. Fish GLBs, animation clips and appearance parameters are unchanged.

## Regression enforcement and validation

`npm run test:library` now also runs `scripts/test-viewer-context-cleanup.mjs`. This test reads the fish set from the authoring registry and checks exact runtime IDs, so legitimate registry additions cannot leave another stale fixed-count gate. It deliberately holds native handles to make results independent of GC. Chromium and WebKit each open/close Pool Table, Proton Saga and all 60 fish in the same page (62 models per engine). It asserts exactly one live native context, a tiny idle drawing buffer, no context-limit errors, no page exceptions, and no post-warm-up growth in Buffer/Texture/Program/Framebuffer/Renderbuffer/VertexArray handles. Switch pacing respects WebKit's history-mutation rate limit.

Local verification on the isolated correction worktree:

- `npm run build`: PASS, including complete GLB validation; existing bundle-size advisory remains.
- `npm test`: PASS, 609 tests and zero failures.
- `npm run test:library`: PASS, full discovery/navigation/reflow suite plus both 62-model resource stress runs.
- `node scripts/test-pwa-standard.mjs`: PASS.
- `node scripts/test-shopping-cart-browser.mjs`: PASS at 1440, 768 and 390px.
- The live acceptance harness's local smoke preflight: PASS in desktop Chromium, touch/mobile Chromium and touch/mobile WebKit, including real pose changes, pause/resume and bounded renderer reuse.
- `git diff --check`: PASS.

`docs/verification/viewer-context-cleanup.json` records actual per-model GPU counts. In both engines, after the first fish and after the sixtieth fish, the retained shared resources were identical: 1 Buffer, 6 Textures, 1 Program, 39 Framebuffers, 0 Renderbuffers and 0 VertexArrays. These are handle counts, not measured VRAM sizes; the shared studio target intentionally remains cached.

A fresh 180-case production test is required after this correction is deployed. Existing native-select CSP diagnostics in WebKit and the screenshot tool's injected-style diagnostic are retained and classified separately; context-limit errors remain failures. Unrelated original-workspace changes are excluded from publication.

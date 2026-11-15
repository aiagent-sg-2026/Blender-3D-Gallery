# Approved fish deployment derivatives

The owner authorized replacing the corresponding live gallery models and pushing each passing batch to main on 2026-11-15. This directory promotes the three owner-accepted models and the first three independently reviewed upgrades. It does not claim completion of the other 54 fish.

`releases.json` owns the promoted set, source paths, acceptance level, descriptions and license summaries. `register.py` overlays only these IDs onto the fish catalog; the baseline registrar calls the same overlay. Sources and previous production GLBs are preserved.

## Reproduction

Run Blender 5.1.2 in background mode with `--python models/fish-realism-release/export.py -- SLUG` for each manifest entry, then `python3 models/fish-realism-release/register.py`. Export never saves changes to the source. Delivery copies flatten temporary skinned mesh parenting, repair n-gon cap UVs and use WebP textures at quality 95. Morph meshes retain their shape keys. Each export receipt records source and output SHA-256.

Run `npm run build`, Blender with `--python models/fish-realism-release/verify.py`, and `node models/fish-realism-release/test-browser.mjs`. Set `FISH_LIVE_URL` to the deployed gallery URL (with trailing slash) to test the actual published catalog. Browser checks use no model substitution: response bytes must match the released GLB. They check visible swim deformation, stable pause, disposal, console errors and overflow in Chromium and WebKit at desktop and mobile viewport sizes. These are emulated viewports, not physical-device performance measurements.

The accepted ray is an explicit quality-preserving exception to the proposed 5 MiB / 100k triangle candidate budget: approximately 12.4 MiB / 113k triangles including its morph targets and surface detail. It remains lazy-loaded on opening the viewer. Other five delivery models are under 5 MiB each. Betta retains the original creator's small loop endpoint difference; the verification threshold records this rather than claiming a perfectly seamless original clip.

Reference photos are not embedded. The Betta source and CC BY 4.0 links appear in the viewer, together with creator credit and modifications. Per-model metadata retains the artistic/identification limits. A previous archive-only acceptance receipt describes its historical release; this manifest describes the later live promotion.

WebKit receipts separately retain existing native-select CSP events. Screenshot-time `style-src-elem` events are accepted only inside the capture interval: the installed Playwright screenshot preparation injects `body {}` for animation synchronization, which production CSP blocks. Neither the application CSP nor the validator was weakened. Other page/console errors or CSP events fail the browser check.

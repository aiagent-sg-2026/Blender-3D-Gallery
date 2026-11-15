# Deployment follow-up and complete live animation acceptance

Status: **PASS — 180/180 production animation cases**, completed 2026-11-14T19:43:47.667Z. All three profiles observed the same stable production build `52794dce31c58652`. No HTTP failures, unexpected console errors, page exceptions, or WebGL context-limit errors occurred in the final run.

| Browser profile | Viewport | Result |
| --- | --- | --- |
| Desktop Chromium | 1440 × 900 | 60/60 |
| Mobile Chromium with touch | 390 × 844 | 60/60 |
| Mobile WebKit with touch | 390 × 844 | 60/60 |

Deployment commit: `2bf3f96100ad59043b9072fdc68341824e3ec283`. [Pages release 43629169616](https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43629169616) passed its complete build/browser gates and deployed successfully at 2026-11-14T19:29:38Z (2026-11-15 03:29:38 Singapore). See [published-deployment.json](published-deployment.json) and [live-build-info.json](live-build-info.json).

The final [animation-results.json](animation-results.json) is a full production run (`smoke: false`), with every autoplay, visible pose change, stable pause, clean close, single healthy reusable context and tiny idle framebuffer assertion true. All 120 mobile cases passed touch playback checks; four representative species passed touch orbit in Chromium. All three profiles passed reduced-motion checks. Each deployed GLB matched the original Blender fish asset SHA-256. Desktop Barramundi, mobile Stingray and mobile WebKit Betta screenshots were also visually reviewed.

The previous post-fix matrix passed all 180 fish cases but failed overall because one homepage hero request returned HTTP 503. That run is retained in [animation-results-context-fixed-hero-503.json](animation-results-context-fixed-hero-503.json) and its matching log. A fresh WebKit page and three independent GETs returned HTTP 200 for the exact hero asset ([hero-webkit-recheck.json](hero-webkit-recheck.json)). The complete matrix was then rerun without weakening error checks; that final run passed with an empty error list. This is recovery evidence, not a guarantee against future CDN interruptions.

WebKit retained 267 classified nonblocking CSP diagnostic messages from native select styling and Playwright screenshot synchronization; their sources and bounded event checks are explained below. These are warnings in the report, not hidden console output. Physical phones were not tested; mobile coverage uses actual Chromium/WebKit engines with mobile viewport and touch emulation.

See the [screenshot index](screenshots.md) for 45 final-run captures, including paired swimming poses and full desktop/mobile viewer screenshots. Historical failure captures are clearly identified there.

## Deployment and investigation history

Expected revision: `65e56ac20802cd8969fac3d9de9131e87319b96a`.
Tested deployment snapshot: `deployment-latest.json` records the deployment observed for this report, including run ID, URL and main revision. The watcher automatically follows a newer active Pages run only after GitHub comparison confirms it descends from the fish revision.

Runs 43614071268 and 43619286059 were cancelled while other main updates were being published. Monitoring moved to run 43619711865 for main revision `5a9546623d7a334e646514339de2f958def5760a`. Git ancestry confirms the fish revision is included, and the fish asset files remain unchanged. Cancellation snapshots are retained. The verifier still binds all 60 GLB hashes to the original fish release.
Site: https://yapweijun1996.github.io/Blender-3D-Gallery/

`watch-deployment.mjs` follows the existing run without modifying or bypassing release gates. `deployment-latest.json` records the latest observed state.

`test-live-swimming.mjs` defaults strictly to the HTTPS production site and the 60 fish from the exact published revision. Full acceptance requires 180 cases: all 60 fish in desktop Chromium, touch/mobile Chromium, and touch/mobile WebKit. It checks actual autoplay/resume pixel changes, stable paused pixels, the SHA-256 of the exact content-hashed GLB URL requested by each viewer, touch playback controls, representative touch orbit, overflow, close cleanup and reduced-motion preferences. GLB hashes are verified with bounded independent GETs of those same deployed URLs. A model card or a playback button alone never counts as an animation pass.

## Tool preflight (not live acceptance)

`smoke-animation-results.json` is explicitly marked `smoke: true` and uses an isolated local build of the expected revision. Its three cases passed. These local results and current preflight screenshots are not proof that Pages has deployed the revision. Final production results are in `animation-results.json` with `smoke: false`, the HTTPS site and 180 passing cases.

Harness corrections made before live testing:

- Avoid a shared mutable `dist` directory while other work is running. Use an isolated build for preflight.
- Draw-call prototype instrumentation did not reliably represent ongoing rendered motion. A separate RAF/pixel probe confirmed animation. Acceptance uses visible image changes plus stable pause images.
- Element screenshots can wait forever for a moving canvas to become position-stable. Capture the actual canvas rectangle with page screenshots instead; do not alter the model's animation to make capture pass.
- Preserve and classify WebKit CSP messages rather than blindly discarding console output. Existing native select styling emits `style-src-attr` events only on `model-theme`, `model-category`, `model-collection`, and `demo-category`. Playwright's own WebKit screenshot synchronization injects a `body {}` style, producing a `style-src-elem` event per screenshot under production CSP. The installed `playwright-core/lib/coreBundle.js` implementation of `inPagePrepareForScreenshots` shows that injection. `webkit-baseline-csp.json` reproduces four native-select events before, and one additional tool-injected event after, a screenshot of the unrelated Pool Table. Tests retain these warnings and validate their event targets/counts; unexpected CSP events still fail.

Physical phones have not been used. Mobile tests are real browser engines with mobile viewport and touch emulation.

## Release gate recovery

Run 43619711865 failed because the library test expected three Demos although Shelf Inspector made the approved registry contain four. The deploy job was skipped. Failure evidence is in `deployment-failed-43619711865.json` and `release-gate-failure.txt`.

An isolated local candidate, commit `95cc9d0e61e725d9bad749cc192ecb80ac48729f`, changed the stale index/reset expectations to the registry ID set and retained exact-ID, launch-link and no-preload checks. Build, 598 unit tests, full library browser tests and PWA-standard checks passed. Before publication, another main update `345f3104dad5e76bad31c86d63608820a5d65d55` delivered the same count/reset correction along with a Visitor byte alignment. The candidate push was rejected safely as non-fast-forward. No force push or duplicate integration was performed; monitoring switched to run 43622012501 for the already-published main correction. The unpublished candidate remains on its local branch as reviewable evidence. Fish assets are unchanged and remain bound to their original hashes.

## First production matrix and context correction

The first live run completed all 180 fish pose/pause checks successfully, but strict acceptance was **136/180**, not a pass: WebKit emitted native context-limit errors on sequential opens beginning with model 17. It also observed one hero image HTTP 503; an independent retry returned HTTP 200 with 31,350 decoded WebP bytes. The complete failed run is preserved in `animation-results-before-context-fix.json` and `online-test-before-context-fix.log`.

The old viewer created a new renderer/context on every open. Explicit context loss alone was insufficient under WebKit's native accounting. The verified correction `2bf3f96100ad59043b9072fdc68341824e3ec283` reuses one renderer and one studio target, disposes per-model resources, removes old event handlers, resets renderer options, and shrinks its detached idle drawing buffer. Local Chromium and WebKit each switched through 62 models while holding native handles: exactly one context, stable GPU object counts, and no context-limit errors. Regression checks are now part of `npm run test:library`. See `context-fix-verification.md` and `local-context-budget.json`.

The fix was pushed and the remote main SHA verified. The superseded pre-fix run 43627986567 was cancelled only after the complete descendant correction was published and its replacement run existed; all original release gates plus the new stress regression remain enforced. Run 43629169616 completed successfully and the final production matrix passed on its deployed build. The production verifier additionally requires one reusable context and a tiny idle framebuffer after each close. The propagation check requires the new renderer-owner code to be present before starting the fresh matrix.

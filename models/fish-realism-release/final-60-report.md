# All sixty fish: final release verification

## Scope and publication

All supplied FISH-001 through FISH-060 entries have upgraded gallery derivatives. Fifty-seven original, photo-informed Blender studies passed the sequential visual and technical QA loop. Barramundi R3, Betta R3 and Stingray R4 retain the owner-accepted sources. Existing source archives and previous production files are preserved. `releases.json` is the authoritative promoted set.

The final two fish were committed and pushed individually: Guppy `c4f3c48287d69ffc682e01dd42a7688f1da169b4`, then Tiger barb `08b78f384933836d5b07a06b3780ae536414d9da`. Each push was verified against GitHub main. The user's per-fish publication policy supersedes the earlier batch policy.

## Local evidence

- All 60 actual delivery GLBs: Khronos validation reports zero errors and zero warnings; source and delivery SHA-256 bindings match.
- All 57 queue entries: `qa_pass`, with inspected real-photo references, original-source renders, visual revisions, animation checks and per-fish evidence.
- All 60 current delivery files have actual-catalog Chromium/Metal and WebKit evidence at 1440 x 900 desktop and 390 x 900 touch/mobile viewports. Historical receipts are explicitly identified in `final-60-local-audit.json`; they are not presented as a new simultaneous all-sixty local run.
- Browser scenarios cover visible swimming deformation, stable pause, resume and pause, viewer disposal, no horizontal overflow and no page errors. The final fresh live run additionally checks media-preference changes.
- Source, imported source GLB and delivery contact checks cover five poses for the 57 independently reviewed upgrades. Counts and movement of designated unusual anatomy are checked where specified. Sources remain packed and reproducible; the exporter never saves delivery changes into a source.
- Delivery motion evidence is reused only when the actual GLB, profile and verifier fingerprints match; selected new models are always remeasured. `verification-cache-qa.json` documents the separate cache invalidation experiment. `motion-verification.json` labels retained evidence.
- The 79-file preservation guard passes. Previously published delivery hashes remain unchanged when each new fish is promoted.
- Final full unit suite: **720 passed, 0 failed**, recorded in `final-60-unit.log`. Final build and catalog validation passed.

`overview.png` and `overview.html` arrange all sixty actual Blender thumbnails. They are static artwork previews, separate from browser screenshots and live animation evidence.

## Deployment and fresh live evidence

The all-sixty source commit **08b78f384933836d5b07a06b3780ae536414d9da** deployed successfully in [GitHub Pages run 43734611160](https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43734611160), completed at 2026-11-15 16:59:42 UTC (2026-11-16 00:59:42 Singapore).

Fresh live verification completed at 2026-11-15 18:07:33 UTC (2026-11-16 02:07:33 Singapore): **240/240 scenarios passed**, comprising 60 fish x Chromium/Metal and WebKit x desktop and mobile. Every response matched the current delivery SHA-256. Each case passed visible deformation, stable pause, resume/pause, media-preference updates, disposal, no page errors and no horizontal overflow. Both full-manifest completion passes and the independent coverage audit passed.

- [Deployment receipt](final-60-deployment.json)
- [Chromium: 120 completed cases](live-chromium-final-60-browser-verification.json)
- [WebKit: 120 completed cases](live-webkit-final-60-browser-verification.json)
- [All 240 screenshot paths, dimensions and SHA-256 bindings](final-60-live-audit.json)
- [Local source, delivery and historical browser evidence index](final-60-local-audit.json)
- [Full unit test output: 720 passed](final-60-unit.log)
- [All sixty static Blender previews](overview.png)

The initial parallel run was interrupted after 46 passing cases when Pages returned **HTTP 429 Rate limit exceeded**. After waiting for HTTP 200, the unchanged browser assertion harness resumed serially with 25-second intervals and bounded 60-second backoff. All remaining cases passed. [The interruption record](live-final-60-initial-rate-limit.json) and [pacing events](live-final-60-pacing-events.jsonl) preserve this distinction; failed loads were not counted as passing cases.

The final evidence commit adds reports, test orchestration and screenshots. It does not change the deployed fish binaries or source files. The successful containing deployment above, combined with exact current live model hashes, establishes model availability; it does not claim that a later report-only commit has itself finished deploying.

## Limits and preserved behavior

The original studies are photo-informed artwork, not photogrammetry, taxonomic identification or measured biomechanics. Fine teeth, gill structures, fin rays and small appendages are simplified where the individual metadata records this. Generic market aliases and explicit visual-species interpretations remain documented, including the two supplied threadfin entries. Reference photographs are credited and used for inspection only; their pixels are not embedded in the original textures.

The accepted Betta retains its original licensed animation and its small inherited endpoint difference (maximum imported vertex displacement approximately 0.0005494 scene units); the other accepted sources were not regenerated. Swimming is artist-tuned. Puffer studies represent uninflated fish and do not claim a new inflation animation.

Phone coverage uses emulated mobile viewports and touch contexts, not physical handset hardware, thermal behavior or mobile performance measurements. Chromium uses the installed Google Chrome with the Metal backend. WebKit is Playwright WebKit, not a claim that physical iPhone Safari was tested. Known WebKit native-select and screenshot-preparation CSP events are scoped and recorded; the application's CSP was not weakened.

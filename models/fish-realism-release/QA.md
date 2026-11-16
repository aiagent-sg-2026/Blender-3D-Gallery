# First live promotion QA

## Scope

Replace only `fish-barramundi`, `fish-betta`, `fish-stingray`, `fish-red-snapper`, `fish-grouper` and `fish-golden-pomfret`. Keep all 60 catalog IDs, the other 54 entries, the original production GLBs and the three accepted editable sources. Release derivatives preserve source animation and use web texture encoding.

## Completed checks

- Production build: all catalog assets pass Khronos glTF validation with zero errors and warnings; Vite build succeeds.
- Existing unit suite: 685 passed, zero failed/skipped.
- Delivery artifact check: all six hashes match their source/export receipts and actual reimported motion evidence; all 79 protected-file hashes unchanged.
- Catalog comparison: exactly the six authorized entries differ, no added/removed asset IDs, overlay registrar is idempotent.
- Blender GLB reimport: actual evaluated geometry moves; five loops return within 0.0001 scene units; Betta retains its original approximately 0.00055-unit endpoint difference.
- Actual browser evidence: see per-engine local receipts and screenshots under `output/playwright/fish-realism-release/local`. Checks require the real catalog model's response SHA-256, visible swim, stable pause, close/disposal and no horizontal overflow.
- Visual inspection: neutral side views and head details of the new art, and actual browser compositions of all six in desktop/mobile layouts. These are artistic improvements, not scanned-specimen claims.

## Publication boundary

A push is not deployment evidence. After pushing, wait for a successful GitHub Pages deployment containing this commit, then run the same browser checks with `FISH_LIVE_URL=https://yapweijun1996.github.io/Blender-3D-Gallery/`. Commit the live receipts and screenshots after verification. Until those exist, online availability remains unverified. Mobile checks use emulation, not a physical handset.

## Batch 02: silver pomfret, black pomfret, Indian mackerel

This batch adds exactly three catalog replacements, bringing the manifest to nine. Rebuilt the full catalog, reimported and measured all nine delivery GLBs, checked all 79 protected hashes and confirmed registrar idempotence. Incremental browser receipts are named `local-all-batch-02-browser-verification.json`; prior six model binaries remain unchanged. These new fish retain per-item photo references, head/detail renders, animated GIFs and independent draft QA evidence. Live availability still requires the deployment and live verification described above.

Batch 02 results: all 12 incremental Chromium/WebKit desktop/mobile scenarios passed; 686 existing unit tests passed, zero failures/skips. The previous six release GLB hashes are unchanged.

## Batch 03: Spanish mackerel, yellowstripe scad, bigeye scad

Three additional entries, twelve total; the remaining 48 are not declared complete. All twelve deployment GLBs pass reimported motion and artifact/source hash checks; 79 protected files remain unchanged. All 12 incremental Chromium/WebKit desktop/mobile scenarios passed, including final post-capture/disposal error checks. All 689 existing unit tests passed with zero failures/skips. The three new delivery GLBs are 3.80, 4.09 and 3.74 MiB respectively. Model QA revised overly broad Spanish mackerel pectorals/regular bars, separated yellow scad tail pigmentation, and removed bigeye scad eye/mouth overlap before sealing the artwork.

## Live verification: initial six

GitHub Pages run [43698676117](https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43698676117) successfully deployed commit `9512937490183fc86c4aa61f7e7b8465e668a02e`. All 24 live Chromium/WebKit desktop/mobile scenarios passed against the public website, with exact release response hashes, visible motion, stable pause, reduced-motion preference changes, final disposal/error checks and the Betta creator/license links. See `live-all-release-01-browser-verification.json` and `output/playwright/fish-realism-release/live`. This establishes availability of those six only; subsequent models remain subject to later deployment verification.

## Batch 04: Crimson snapper and two threadfin variants

All twelve incremental Chromium/WebKit desktop/mobile scenarios pass, including playback preference updates and final capture/disposal error checks. Full catalog build, all fifteen GLB/source/motion bindings and 79 protected files pass. The previous twelve delivery binary hashes remain unchanged. Each threadfin source and reimported GLB has eight independently moving sensory-ray meshes, four per flank. The common-name overlap is explicit in the viewer metadata rather than presented as two certified distinct species. Delivery sizes are 4.08, 3.97 and 3.97 MiB. Initial-six live receipts and screenshots are included with this batch.

## Fin-contact follow-up 01 and ribbonfish

A geometric audit found the prior fixed pelvic-root coordinates outside the curved body despite correct bone weights. Red snapper, grouper and golden pomfret now use embedded ventrolateral root curves; ventral detail renders were inspected. Other mesh-motion measurements remain within 0.00001 of the prior source receipt. Source, reimported draft and actual delivery geometry pass contact checks at five phases. All 16 incremental Chromium/WebKit desktop/mobile scenarios pass. The other twelve release binaries, including the three owner-accepted fish, are unchanged. Seven other affected upgrades are explicitly marked for the same revision.

Ribbonfish is a distinct scaleless reconstruction with a welded open-jaw/body shell, small fang geometry, a tapered body tail, and independent dorsal-wave controls. Three actual reimported dorsal probes show different moving phases. Its modeled anatomy avoids a separate caudal/pelvic fin or broad anal membrane. Dedicated source, GLB, browser, dorsal-detail and head-detail evidence is included.

Earlier live receipts prove their recorded deployment/artifact versions and playback scope; they do not retroactively establish the later geometric contact criterion. A fresh deployment and hash-bound live check are still required for the corrected delivery files.

## Live verification: second and third batches

GitHub Pages run [43701022605](https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43701022605) successfully deployed commit `21a3fe495d9dcd8ad66cabea3537acc4f1a8eb7f`. All 24 live Chromium/WebKit desktop/mobile scenarios pass for silver pomfret, black pomfret, Indian mackerel, Spanish mackerel, yellowstripe scad and bigeye scad. Response hashes identify the exact deployed files. This is availability/playback evidence for those versions; later pelvic-contact corrections require their own deployment verification.

## Fin-contact follow-up 02 and sardine

Indian mackerel, Spanish mackerel and yellowstripe scad now pass five-phase contact checks in source, imported draft and actual delivery GLB, including their finlets. Other mesh-motion metrics remain unchanged within 0.00001. The thirteen other previous delivery binaries remain unchanged. All 16 incremental Chromium/WebKit desktop/mobile scenarios pass. Four earlier affected upgrades remain queued for correction.

Sardine follows an explicit Sardinella gibbosa visual reference, with one midbody dorsal fin, compact caudal outline, small paired fins and faster tail-driven swimming. Three visual iterations corrected the pointed snout, rectangular pectoral outline and excessive edge ripple. It is one live fish, not a claimed school/dried-goods variant. All source/export/delivery contact and playback gates pass.

## Fin-contact follow-up 03 and anchovy

The remaining four affected upgrades (bigeye scad, Crimson snapper and both threadfin entries) now have embedded pelvic bases. Other mesh-motion measurements remain within 0.00001 of the previous source/import receipts. Silver and black pomfret receive the new contact receipts without editing either packed Blender source; silver delivery was re-exported, while black delivery bytes remain identical. The eleven non-selected previous delivery hashes are unchanged. All fifteen independently reviewed upgrades now pass source, imported draft and actual delivery contact checks at five phases. The three owner-accepted sources remain unchanged.

Anchovy follows the explicitly documented Stolephorus indicus specimen, with a broad silver flank stripe, reduced eye diameter, maxillary crease extending below/behind the eye, small paired fins and a compact forked tail. One live fish is delivered, not a school or dried-goods variant. Eighteen catalog entries are upgraded; forty-two remain queued.

All 28 incremental desktop/mobile scenarios pass in native Chrome with Metal and Playwright WebKit; see the per-engine `contact-03` receipts and screenshots. All 698 unit tests pass. Earlier bundled Chromium/SwiftShader attempts timed out in screenshot preparation even though the diagnostic canvas rectangle remained 350 by 396 pixels and requestAnimationFrame advanced. A native Chrome/Metal diagnostic and the unchanged playback assertions pass. The optional fish QA runtime is recorded in the receipt; this environment change does not weaken the image-change, stable-pause, hash, disposal, CSP or overflow gates. Mobile tests are emulated viewports.

## Batch 05: rabbitfish, red seabream and croaker

Three new catalog replacements bring the total to twenty-one. The previous eighteen delivery binaries and all 79 protected files remain unchanged. All twenty-one source/output bindings and actual delivery GLB deformation gates pass; the eighteen reviewed original artworks also pass posed fin/body contact. All twelve incremental native Chrome/Metal and WebKit desktop/mobile scenarios pass with exact delivery response hashes.

Each item has its own photo references, two visual iterations, packed source, actual GLB round-trip contact/motion evidence, detail renders and swim GIF. Rabbitfish revisions reduced oversized spots and deepened dorsal spine valleys. Red seabream revisions increased scale density and reduced pale rim contrast. Croaker revisions replaced broad scale tiles, tapered the spinous dorsal outline and darkened its upper membrane. Red seabream follows Pagrus major as the explicit visual species; the supplied common-name ambiguity is stated in metadata. These are original artistic reconstructions, not scans or certified identification models.

Batch 05 also passes all 698 unit tests, with zero failures or skipped tests. Live availability of these three still requires a successful containing Pages deployment and hash-bound online checks.

## Batch 06: trevally and two tilapia forms

Three replacements bring the manifest to twenty-four; thirty-six remain queued. The previous twenty-one delivery hashes and all 79 protected files remain unchanged. All twenty-four actual delivery GLBs pass reimported deformation/source binding checks, and all twelve incremental native Chrome/Metal and WebKit desktop/mobile scenarios pass.

Trevally revisions removed an excessive yellow stripe and subdued the regular-looking scute pigment. Red tilapia revisions connected the spiny/soft dorsal silhouette and rounded the snout. Nile tilapia retains a barred caudal and muted flank bars that distinguish it from the cultivated red hybrid; its scale edge contrast was reduced after the first sample. Each passed source/GLB contact, native browser draft and independent visual review gates. These new source stills use actual Blender EEVEE for earlier inspection; packed texture resolution, geometry and acceptance assertions are retained.

Batch 06 passes all 700 unit tests after integrating the unrelated main topology repair; zero failures or skipped tests.

## Live verification: contact revisions 01/02, ribbonfish and sardine

Pages run [43708062271](https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43708062271) successfully deployed `c9968137e1c7ff670c2fc0261510d9ab391ebbe8`. All 32 live native Chrome/Metal and WebKit desktop/mobile scenarios pass for red snapper, grouper, golden pomfret, Indian mackerel, Spanish mackerel, yellowstripe scad, ribbonfish and sardine. Exact response hashes match the corresponding current delivery files. See the two `live-*-contact-01-02` receipts and live screenshots. This establishes those corrected artifact versions online; subsequent main replacements await their own containing deployment.

An initial combined attempt completed the sixteen Chromium cases, then WebKit's first page navigation exceeded the 30-second load timeout. No application change was needed: separate engine runs pass all 32 cases. The harness now saves a checkpoint after every passed scenario and records completion explicitly; optional resume requires the same harness, deployment, browser runtime and matching selected GLB hashes. This prevents a later network failure discarding already completed evidence.

## Batch 07: marble goby and two snakeheads

Three replacements bring the manifest to twenty-seven. The prior twenty-four delivery hashes and all 79 protected files remain unchanged. All twenty-seven delivery GLBs pass actual reimported deformation and source/artifact bindings, all twelve incremental native Chrome/Metal and WebKit desktop/mobile scenarios pass, and all 700 unit tests pass without failures or skipped tests.

Marble goby revisions embedded an oversized eye, sharpened its irregular camouflage and rounded the pectoral outlines. Common snakehead revisions broke up angular head mottling. Both snakeheads use stronger travelling trunk flex and a lower independent stabilizer-tip blend so their long dorsal/anal membranes follow the local body more closely. The giant snakehead is explicitly an adult blue-grey form with an irregular lower-flank band, rather than the red juvenile stage. Photo references, source detail, GLB contact/motion, browser evidence and actual EEVEE swim GIFs are included for each. Sources are normalized artistic studies, not calibrated scans.

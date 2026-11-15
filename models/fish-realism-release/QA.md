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

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

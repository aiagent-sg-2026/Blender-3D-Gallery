# Integrated M061/M062 Shelf Inspector local QA

Base31c0f593 preserves external13ef9c10 and M060. Seven fixtures explicitly enumerated M056,M057,M058,M059,M060,M061,M062; catalog559→561 preserves every old asset object and adds only M061/M062. Rebase conflicts resolved additively, no external cue/CI/package changes. `qa/shelf-inspector-m061-m062/release-base-review.json` records preserved ancestor and external file scope. This supersedes the provisional M061 integration blocker, but is not CI, deployment or physical-device evidence.

## Runtime and scope

M061 two rows: Lower/Upper, both boards selected together; valid row index retained on switching, unsupported old row3 resets0, Reset always0. Existing three-row Lower/Middle/Upper behavior preserved. M061 actual2.4×0.55×1.2m versus original2.4m height remains disclosed. M062 three horizontal single-span shelves with shallow curved fronts, fiveLEDs, single1.92×.36m header and actual2.4×.55×2.4m. No product loading or auto-assembly. Core two-row change was exercised across the entire Shelf suite.

## Tests and retained failures

Full necessary Shelf job `f732ac4d-8026-4e12-bdae-c5088ccf5e4b` passed20 relevant units (Shelf+M061/M062 assets) and build. It ran all16 Shelf browser cases;12 passed,4 failed because the newly expanded seven-fixture test loop ended on M062 but still compared with the per-case M058/M059/M060/M061 target. This was a test-sequence error, not a hidden production fix. Original failure JSON is retained.

Minimal correction explicitly selects each case target after its full seven-fixture loop, waits ready and takes a screenshot before the existing exact GPU/pixel assertions. No threshold/assertion removed, no production change. Only those4 cases rerun in job `356448d7-8f8c-4559-bc10-f26f72ebd966` (20:44:28–20:46:00UTC), allPASS. Combined evidence covers16/16, not a claim that the original full run was green. Other passed cases were not redundantly rerun.

Coverage includes all original keyboard/touch/cancel/pinch/scroll, rapid stale loading, GPU lifetime checks, every model's four actual LOD hashes, seven explicit unique IDs, model-aware row buttons/status, both row meshes and source-material ownership, reset, context disposal, and390px touch views.

## Visual review

Actual final M061 desktop/mobile and M062 desktop/side/mobile screenshots inspected. Labels are complete/upright, cabinet/row shapes intact, no observed striping or horizontal cropping. M061's0.16m header is physically smaller; zoom available. Compact evidence and actual eight GLB hashes in qa/shelf-inspector-m061-m062.

## Limits

Local Chromium desktop and touch emulation, not physical Android/iOS or Safari. Manual fourLOD only, no automatic selection. LED emissive controls are not photometric simulation. Static anchors not loaded products. READMEs/manifests/nested metadata updated only to locally verified support. No remote push or publication queue changes.

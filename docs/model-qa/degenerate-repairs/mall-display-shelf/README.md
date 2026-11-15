# Display shelf topology repair

Status: PASS. Exact-zero triangles: 164 → 0. Total triangles: 5,712 → 5,548. No positive-area source precision residues were removed. The canonical GLB remains 172,420 bytes because its original vertex/normal/material payloads and buffer capacity are retained; only triangle index streams change.

The saved source retains all 31 authored parts and scene/collection semantics, with cleanup on six reviewed parts: the jade header, four brass front nosings and COLLECTION text. Authored mesh/text/curve data remain editable. Native reopen and actual delivered GLB reimport are clean. Existing previews remain applicable. A new fresh-generation regression validates the complete saved shelf source and real GLB without preview rendering; cleanup regressions also cover the other three essentials.

- [Delivery comparison](delivery-comparison.json), [index receipt](index-repair.json)
- [Native source preservation](source-repair.json), [source export comparison](source-geometry-comparison.json), [delivery reimport](delivery-reimport.json)
- [Pre-fix failure](regression-before.log), [generator regression](generator-regression.log)
- [Verification](verification.json), [browser results](browser-results.json)

687 tests and the build passed. All fifteen essentials browser cases passed at 1440/768/390 pixels, including consumed-byte SHA checks, discovery, orbit, zoom, reset, reload, close/reopen, focus restoration and render-loop cleanup. The actual desktop shelf Viewer image was inspected; four open shelves, supports, header and COLLECTION text are intact. No physical-device/FPS or deployment claim is made.

After integrating main `95129374` (another model release with optional Viewer attribution links), all 687 tests, the build and all fifteen essentials browser cases passed again. Asset hashes were unchanged; see [integration browser results](integration-browser-results.json).

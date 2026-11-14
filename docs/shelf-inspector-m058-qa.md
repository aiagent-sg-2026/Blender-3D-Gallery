# M058 Shelf Inspector QA

Local candidate based on `f596561e` (integrated main `f466c66f`). No release or physical-device result is claimed.

## Implementation

Adds only M058 as a third explicitly named fixture, preserving M056/M057. Uses its actual 2.4 × 0.55 × 2.4 m dimensions, three shelf nodes, five LED nodes and one anchored 2.04 × 0.36 m header surface. Core parts and loader implementation unchanged. Header label text now follows actual surface count. Imported URLs do not eagerly load all GLBs; only selected model/LOD is requested. Original concepts only, no official brand claims.

## Evidence

Job `548ebfbb-95b1-4a50-9a2a-1c305141308c`, 2026-11-14 18:30:22–18:31:17 UTC, succeeded: 12 relevant unit tests, build, affected existing `corner-controls-lods-and-ownership`, new `endcap-controls-lods-and-ownership` and `endcap-touch-viewport`. No unrelated full-suite repetition. Existing assertions retained; fixture options assertion explicitly enumerates unique M056/M057/M058 IDs rather than only counting.

New evidence checks actual four exported GLB hashes; title/highlight/LED state across LODs; exact reset image; three cycles through all three fixtures with strict GPU resource equality; delayed obsolete M058 LOD response superseded by M057 then M058 LOD3; pending-scene clearing; reset after interrupted load; context loss on leaving; single-face source-material ownership and overlay disposal; touch controls and viewport width at 390px. No tolerance was loosened.

Actual diagonal, front, side-angle and mobile viewport screenshots were inspected: ENDCAP COLLECTION is complete, upright and not mirrored/occluded; open sides and shelf shape visible; mobile model is not clipped and heading is readable. Saved compact evidence is in `qa/shelf-inspector-m058/`.

## Limits

Chromium desktop and touch viewport emulation only, not real Android/iOS or Safari. Manual four-LOD selection only, no automatic LOD. Product/docking anchors remain static metadata, not product loading or auto assembly. LED emissive control is not photometric simulation. No geometry, catalog, CI or unrelated billiards changes in this runtime slice. Manifest/README support claims were updated only after these tests and visual review.

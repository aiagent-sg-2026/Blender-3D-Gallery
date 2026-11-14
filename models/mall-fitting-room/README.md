# Mall Fitting Room
Original Shopping Mall031, not global500 ID031. Independent modular opaque partitions, floor, bench, clothing hooks, shelf and two-handled outward-opening door. No mirror or fake reflection. No building-code/accessibility/privacy/safety certification.
Frozen target: 1.60m shell width, 1.50m shell depth, 2.20m height; closed depth including outer pull1.627m. Door leaf0.90m wide,105degree opening. Metres, Blender+Z up/-Y front; glTF+Y up/+Z front.

## Verified local evidence (2026-11-14)
- PASS source generation and saved-source edit/re-export; original source preserved. See `reports/sources.json` and `reports/verify-source.log`.
- PASS GLB structure/Khronos: 0 errors, 0 warnings; 4,900 triangles, 256,908 bytes, 35 primitives, 5 materials, no external textures. See `reports/assets.json`.
- PASS 60-frame conservative OBB door/handle clearance, 105-degree opening and closed reset. Intentional hinge contact is excluded. The test suite executes the actual validator, and exact moving/fixed component counts are asserted to prevent vacuous sweeps.
- PASS six Blender views inspected by parent reviewer: hero, front, rear, side, open and interior. These show opaque modular panels and usable interior furnishings, without claiming building-code certification.
- PASS focused tests 3/3 and build; `reports/focused-test.log`, `reports/build.log`.
- PASS Gallery loading, actual GLB hash, orbit/zoom/reset, close/reopen lifecycle and error/overflow checks at 1440/768/390 widths. See `reports/browser/results.json` and screenshots.
- PASS isolated Three.js door animation visible change and exact closed reset; `reports/animation-browser/results.json` and screenshots. The existing Gallery does not expose animation controls; this is not a claim that it does.
- PASS all 486 existing catalog asset objects unchanged; one independent asset added. See `reports/catalog-preservation.json`.
- Physical Android/iOS NOT TESTED. Local viewport emulation is not physical-device evidence. NOT DEPLOYED.

## Commands
- Blender4.0.2 --background --python models/mall-fitting-room/generate.py (or -- --skip-render for source/export only)
- Blender --background --python models/mall-fitting-room/inspect_sources.py
- node models/mall-fitting-room/validate.mjs
- node models/mall-fitting-room/verify_source_edit.mjs
- node --test tests/mall-fitting-room.test.mjs
- npm run build
- node scripts/test-mall-fitting-room-browser.mjs
- node scripts/test-mall-fitting-room-animation.mjs

Animation validation resets and plays the action for every sampled time so the sweep cannot remain paused at the terminal frame. Conservative oriented boxes cover the leaf and both handles against wall/frame/floor/furniture at60frames, excluding intentional hinge joints. Preview images must be inspected before claiming visual quality.

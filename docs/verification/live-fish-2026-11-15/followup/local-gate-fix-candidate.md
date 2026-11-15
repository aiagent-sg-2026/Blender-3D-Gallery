# Fish publication blocker: registry-aware Demo discovery checks

The Pages run for main `5a9546623d7a334e646514339de2f958def5760a` failed at `scripts/test-library-browser.mjs:67`: the UI correctly displayed four registered Demos after Shelf Inspector was added, but the release test still asserted three. The same stale count and ID list also appeared in the filter-reset check. The failure prevented the deploy job from running; it did not establish a fish-animation defect.

Evidence: https://github.com/yapweijun1996/Blender-3D-Gallery/actions/runs/43619711865

The focused correction reads the authoritative `data/demos.json` registry, requires a nonempty unique ID set, and compares exact displayed counts and sorted IDs against it. Every card launch link is checked against its registered route at all seven existing viewport sizes. Filter reset restores the exact registered set. Existing zero-canvas/zero-GLB static-index checks, filtering, navigation, model fallback, keyboard, mobile and reflow checks remain intact. No website feature, asset, workflow gate or CSP was changed.

Verified in an isolated worktree based on that main revision:

- `npm run build`: PASS, including complete GLB validation; existing bundle-size advisory remains.
- `npm test`: PASS, 598 tests, zero failures.
- `TEST_ARTIFACT_DIR=/tmp/fish-demo-gate-library node scripts/test-library-browser.mjs`: PASS, complete suite including Demo index and filter reset, seven viewports, legacy demo transitions and reduced-motion/reflow.
- `TEST_ARTIFACT_DIR=/tmp/fish-demo-gate-standard node scripts/test-pwa-standard.mjs`: PASS.
- `git diff --check`: PASS.

This correction restores an accurate release gate. Actual fish production playback acceptance remains separate and must follow successful Pages deployment. Other working-tree changes are excluded from this fix.

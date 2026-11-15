> Historical initial check: superseded by the successful deployment and 180/180 production verification in [the follow-up report](followup/README.md).

# Live fish acceptance check — 2026-11-15

Verdict: BLOCKED_RELEASE_NOT_PUBLISHED. The live site does not yet expose the 60 requested fish; animation playback cannot be accepted on either desktop or mobile.

Target: https://yapweijun1996.github.io/Blender-3D-Gallery/

Expected fish revision: 65e56ac20802cd8969fac3d9de9131e87319b96a.

## Observed evidence

- Fresh Chrome DevTools isolated-context inspection: the Barramundi deep link shows “This model could not be found.” No open viewer, fish canvas or swimming controls. Mobile emulation: 390 × 844 CSS pixels, DPR 2, touch enabled.
- Separate Chromium automation against the actual HTTPS production site: 60 model routes at 1440 × 900 and the same 60 at 390 × 844 with touch/mobile emulation. All 120 route checks returned model-not-found; none reached a viewer. Each viewport starts with a full navigation; remaining IDs exercise the production SPA popstate route handler.
- The expected ID list comes from the exact published Git commit, not from the mutable working-tree catalog.
- Both production contexts contain 489 cards, zero fish cards and no `singapore-fish` collection option. Build identity: `a58ed7efd61ad7f4`. No horizontal document overflow; no page exceptions or HTTP failures were captured by the automation. This does not imply that unavailable fish animations passed.
- GitHub Pages' latest successful deployment record is `0feaf347ac5309d9b2705f8fc07a8ca097bb1017` (deployment 7790048743), before the fish revision.
- Fish deployment run 43614071268 is pending, with no jobs yet. The previous run 43610633528 remains in its browser release gates. Workflow concurrency is `pages` with `cancel-in-progress: false`, explaining the queued run. These observations do not establish a workflow failure or an animation defect.

The automation began at 2026-11-15 00:13:52 SGT. JSON files capture the live observations and deployment status at the check time. Deployment may subsequently change.

## Files

- `results.json`: all 120 model-route outcomes and live build/card state.
- `desktop-live.png`, `mobile-live.png`: actual production screenshots.
- `deployment-status.json`, `latest-pages-deployment.json`: GitHub deployment evidence.
- `check-live.mjs`: repeatable availability gate. It deliberately reports `needs_animation_testing` if models become available; availability alone is never promoted to a playback pass.

## Remaining acceptance

After the expected revision is successfully deployed, repeat the live check and verify visible tail/fin motion, default playback, pause/resume stability, reduced-motion handling and touch interactions for all 60 fish. Current results are availability failures, not 120 successful animation tests. No physical phone or Safari/WebKit playback has been verified. No website, model, workflow or deployment state was changed by this review, and no additional commit or push was performed.

# Chibi Mall Guide v5 — plan and concept mockup

Status: proposal only. No Blender model, GLB or catalog entry exists for v5. Nothing here is validated.

## Concept

A chibi shopping-mall concierge for the Virtual Mall Foundation v1 scene (jade green, ivory, champagne-brass palette; see `docs/virtual-mall-foundation-v1-scope.md`). Role: stands at the atrium or a shop entrance holding a direction sign.

## Concept mockup

`mockup/guide-sheet-a.png` (1774 x 887): four views (front, three-quarter, side, back), generated with Codex CLI built-in image generation. The prompt described the style in words only; no owner reference sheet was uploaded. It is an AI concept image, not a rights-cleared or production reference.

Review of the mockup (author's own reading, not an independent review):

- Good: clear silhouette, pillbox cap, vest, neckerchief, gloves, sign; palette matches the mall.
- Inconsistent across views: the sign is held in the opposite hand in the back view; the brass name badge is hidden in side and back views; the cap floats above the hair with no visible fit.
- Risk: the hair (swept locks plus cowlick) is the same hard problem that left Chibi Visitor v4 at REWORK (G5). Do not copy it as-is.

### Revision B: `mockup/guide-sheet-b.png`

Regenerated with the three fixes below (author's own reading, not an independent review):

- Hair: about 7 thick, blunt, rounded locks, no pointed tips and no cowlick; the cap sits on the hair. Fixed.
- Sign: always in the character's right hand; front and back views agree. Fixed.
- Badge: on the character's left chest, visible in the front, three-quarter and side views. Fixed.
- Remaining: the hair lobes are scalloped and fairly regular (acceptable, and easy to model); the shoes' lace detail differs slightly between views; the face is simpler than the v4 sheet. Still an AI concept image with unconfirmed rights.

Reference decision (2026-11-15): sheet B is locked as the v5 reference and copied to `models/chibi-mall-guide-v5/reference/turnaround-b.png`. Modelling rules follow [the chibi standard](../chibi-character-standard.md).

## Design decisions (resolved 2026-11-15)

1. Reference: sheet B.
2. Sign in the right hand, badge on the left chest.
3. Hair: a few thick, blunt locks fitted under the cap.

Budgets, mandatory rig, reviewer and rights decisions are recorded in the [standard](../chibi-character-standard.md) section 8.

## Build plan

| Step | Work | Done when |
| --- | --- | --- |
| 0 | Lock the reference: corrected front, side and back images with the decisions above | Reference files committed locally; rights note written |
| 1 | Proportion blockout in Blender via the MCP: head-to-body about 1:2.5, eyes in the lower third of the head | Orthographic overlay on the reference within a stated tolerance |
| 2 | Body, uniform, cap, sign as separate named parts (as in v4) | Parts listed in README; no intersections |
| 3 | Head with face texture; thick-lock hair that fits under the cap | Passes the v4 silhouette gate, plus an independent visual review |
| 4 | Materials: flat colours plus brass; keep one small face texture | Texture at most 1024 px; 25 or fewer draw calls |
| 5 | Required by the standard: simple armature and 3 shape keys (neutral, smile, surprised) | Rig loads in Three.js with no console errors |
| 6 | Export GLB; QA gate run 001 (validator, byte-identical headless rebuild, Three.js load, silhouette, review) | Gate table with evidence, same format as `models/chibi-visitor-v4/qa/` |
| 7 | Register in `models/catalog.json` only after the gate passes | `npm run validate:assets` and `npm test` pass |

## Out of scope for this proposal

Publishing, catalog registration, gallery viewer acceptance and device performance testing.

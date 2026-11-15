# Chibi Mall Guide v5 — full build plan (for owner review)

Status: **proposal for review, 2026-11-15**. No Blender source, GLB, rig or catalog entry exists for v5. Everything below is a plan. Numbers marked *proposed* are starting values to be fitted against the reference during the build; numbers marked *evidence* come from files in this repository. Related: [standard](../chibi-character-standard.md), [framework design](../chibi-framework-design.md), [concept plan](plan.md).

## 0. What exists today and what does not

Exists (evidence): reference sheet B (`models/chibi-mall-guide-v5/reference/turnaround-b.png`), expression and pose references (`mockup/`), the draft standard, the framework proposal, a morph-target smoke test (shape keys, skinned mesh and morph animation load in Three.js 0.187.0 in Node; skinned mesh must not be parented under the armature), Blender 5.1.2, the Blender MCP bridge, Codex image generation, the v4 QA gate scripts, and nine or more older character generators.

Does not exist: any v5 geometry, rig, animation, texture, GLB, framework code, browser test of morph targets, or approval of the standard.

## 1. Deliverables

| Deliverable | Path (proposed) | Notes |
| --- | --- | --- |
| Character spec | `models/chibi-mall-guide-v5/config.py` | single source of numbers |
| Build modules | `models/chibi-mall-guide-v5/*.py` (head, hair, garments, limbs, rig, shapekeys, anim, export) | split by responsibility |
| Editable source | `sources/chibi-mall-guide-v5.blend` | |
| Full GLB | `exports/chibi-mall-guide-v5.glb` | body + base uniform, rig, shape keys, clips |
| Low-detail GLB | `exports/chibi-mall-guide-v5-low.glb` | for distant NPCs |
| Sign prop GLB | `exports/guide-sign.glb` | separate prop with icon atlas |
| Festive accessories | `exports/accessory-*.glb` | later, one per festival |
| Avatar stills | `previews/avatar-{neutral,smile,surprised}.png` | rendered from the final GLB in Three.js |
| Previews | `previews/` | orthographic views, turnaround vs reference |
| QA evidence | `qa/run-001/` | gate table, validator JSON, hashes, screenshots, review notes |
| README | `README.md` | parts, rebuild, gates, differences, rights |

## 2. Target specification (all *proposed* unless noted)

### 2.1 Size and proportion
- Style: glossy vinyl toy, about 2.5 heads tall, as in sheet B.
- Height: **1.00 m** (owner decision 2026-11-15; v4's scale, *evidence*). The GJH visitor is 1.72 m (*evidence*), so the guide will be visibly smaller than that visitor in the mall; confirm collision and camera heights in the mall runtime later. Rest pose, feet on y = 0, glTF +Y up, front +Z (v4 convention, *evidence*).
- Starting split at 1.00 m: head including cap about 0.40 m (head about 0.36 m plus cap about 0.06 m, overlapping the hair), torso about 0.24 m, legs and shoes about 0.36 m. Head width about equal to head height. Fit to sheet B by overlay; these are not measurements of the sheet.
- Face: eyes centred in the lower third of the head height, wide-set, large (about a fifth of head width each), nose and mouth small, cheeks rosy.

### 2.2 Parts and triangle budget
Budget limit 40,000 triangles and 20 draw calls for the full model (owner decision, *evidence in standard*). Proposed allocation, to be measured:

| Part | Tris | Part | Tris |
| --- | --- | --- | --- |
| Head and ears | 8,000 | Arms | 2,000 |
| Hair (6 to 8 locks) | 5,000 | Gloves | 2,000 |
| Cap with pin | 1,000 | Legs, socks | 2,500 |
| Vest, shirt, sleeves | 6,000 | Shoes | 3,000 |
| Neckerchief | 800 | Eyes | 1,200 |
| Shorts | 1,500 | Badge | 500 |
| Sign (separate prop, not in body count) | 2,000 | **Total body** | **about 33,500** |

For comparison the GJH visitor is 10,356 triangles and 25 primitives; v4 is 113,428 and 25. If the measured total is far above GJH's, trim before polishing.

### 2.3 Materials and textures
- Flat colour materials: skin, hair, jade, ivory, charcoal, white glove, shoe green, shoe sole, brass, eye white, iris. Sample colours from sheet B during the build rather than inventing hex values here.
- One face texture at 1024 px (cheeks, eye details, mouth interior) on the head. No other body textures.
- The sign prop has a small icon atlas (256 or 512 px) with direction arrows, facility icons, welcome and open/closed symbols, shop icons; symbols only, no text. The New Moon mark needs rights confirmation.
- Distinct material primitives kept to about 12 so the 20 draw-call limit has headroom.

### 2.4 Rig (about 17 bones, limit 20)
Root, hips, spine, head; per side upper arm, forearm, hand, thigh, shin, foot (12). That is 16; add one spare (neck or chest) if needed. Sockets: right hand (sign), head top (hat), neck (scarf). Owner decision 2026-11-15: sockets are **plain nodes parented under bones**, so they do not count against the 20-bone limit; attachment must still be tested in Three.js (gate G9). Binding: rigid single-bone, each part 100% to one bone; no weight painting. Skinned meshes are exported as scene roots.

### 2.5 Shape keys
Basis = neutral. Keys: `smile`, `surprised`, `blink`, with brows and cheeks moving inside smile and surprised (owner decision). Blink design is **unresolved and must be prototyped first**: either an eyelid loop on the head that closes over the eye mesh, or per-eye morph targets. The head mesh needs edge loops around the brows, eyes, mouth and cheeks.

### 2.6 Animation clips
Idle (breathing, about 2.0 s loop), blink (shape key, about 0.2 s), walk bouncy (about 0.8 s loop), walk calm (about 1.0 s loop), wave (left hand), hold and point (right hand raises the sign), put sign down (one shot). GJH numbers for reference (*evidence*): idle 2.008 s, walk 1.008 s, 33 tracks, sole floor error about 0.0002 m, horizontal drift 0, baked at 120 Hz. Proposed acceptance: zero horizontal drift for in-place loops and sole floor error at most 0.002 m.

## 3. Work breakdown

Effort is labelled S/M/L because a reliable time estimate does not exist yet.

| # | Step | Effort | Depends on | Done when |
| --- | --- | --- | --- | --- |
| 0 | Resolve open decisions (section 6) | S | owner | decisions recorded in the standard |
| 1 | Inventory duplicated helpers in `models/*/*.py` | S | none | table of helpers and their best version |
| 2 | Create `tools/chibi-framework/kit` from that inventory; golden test rebuilds one older character in a scratch folder | M | 1 | output hash identical or differences explained |
| 3 | Blink and head-topology prototype: small head with eye, lid and brow loops, three shape keys, load test in Three.js | M | none | blink reads correctly; validator 0/0 |
| 4 | Proportion blockout, overlay on sheet B | M | 0 | overlay within a threshold set before the run |
| 5 | Body, garments, cap, shoes, gloves as named parts | L | 4 | no intersections; budget on track |
| 6 | Head with face loops, face texture, eyes | L | 3, 4 | face matches sheet B by eye; loops present |
| 7 | Hair: 6 to 8 blunt locks fitted under the cap | M | 6 | silhouette gate on hair rows; no pointed tips |
| 8 | Materials and face texture | S | 5, 6 | at most 20 draw calls |
| 9 | Rig, rigid binding, sockets | M | 5, 6, 7 | bone count within limit; skinned meshes at scene root |
| 10 | Shape keys finalised | M | 6, 9 | three keys drive in Three.js |
| 11 | Animation clips and foot-contact baking | L | 9 | drift and floor-error checks pass |
| 12 | Sign prop GLB and icon atlas; socket attach test | M | 9 | attaches to the hand socket in Three.js |
| 13 | Export full and low-detail GLBs | M | 8 to 12 | budgets met |
| 14 | QA run 001: gates G1 to G6 plus G7 to G10 (section 4) | M | 13 | gate table with evidence |
| 15 | Fresh-agent review, then owner review | S | 14 | no P0 or P1 findings open |
| 16 | Render avatar stills from the final GLB | S | 15 | three images |
| 17 | Register in `models/catalog.json`, run asset validation and tests | S | 15 | `npm run validate:assets`, `npm test` pass |

Steps 3 and 1 can start immediately and do not depend on each other. Owner decision 2026-11-15: build v5 first and let `kit` grow from v5's needs (steps 1 and 2 follow v5's needs rather than blocking it); the framework's validation therefore comes later. Step 3 (the blink and head-topology prototype) is done first, before steps 4 and later.

## 4. Quality gates

G1 to G6 are the standard's gates (validator 0/0 and budgets; byte-identical headless rebuild; independent Three.js load; silhouette rows against sheet B; fresh-agent review then owner; `validate:assets` and `npm test`). Additional gates proposed for v5:

| Gate | Check | Pass |
| --- | --- | --- |
| G7 | Animation: each clip's drift and sole-floor error; loops close | within the thresholds in section 2.6 |
| G8 | Morph targets: each key changes the intended vertices; brow and cheek move; blink closes the eye | verified in Three.js, with screenshots |
| G9 | Sockets: sign, hat attach at the right place and scale; put-down pose releases the sign | verified in Three.js |
| G10 | Low-detail GLB: triangle target met, silhouette close to the full model at the intended distance | measured |

Results use PASS, FAIL, REWORK, NOT_RUN. Evidence goes in `qa/run-001/`.

## 5. What is needed outside the model

- Viewer or mall code that sets morph influences and plays clips; the gallery viewer currently shows models at rest (*evidence*) and uses no morph code.
- A browser test of morph targets (the smoke test ran only in Node).
- Loader code that attaches prop GLBs to sockets.
- Avatar stills rendered from the final GLB.
These are not part of "model done"; without them the model must not be described as interactive.

## 6. Decisions

Resolved by the owner on 2026-11-15:
1. Height: 1.00 m.
2. Order: v5 first, `kit` grows from v5's needs.
3. Sockets: plain nodes under bones.
4. Step 3 prototype (blink and head topology) first; the blink method is decided by its result. Result: eyes sink behind the skin (key on a separate `Eyes` mesh); see standard section 15 and `prototype/blink/README.md`.

Still open:
5. Blender version for the build (5.1.2 installed; GJH README names 5.2.3).
6. Which festivals the festive uniform covers.
7. Formal approval of the standard.
8. Rights position for the AI reference sheets (currently internal reference only).

## 7. Risks

- Hair is the proven risk (v4 stayed in REWORK on it): mitigated by 6 to 8 blunt locks and an early silhouette check.
- Face quality (v4's face was faint): mitigated by face loops and a face texture, checked in step 6.
- Morph targets untested in a browser or the mall runtime.
- Budget: allocation is a guess; measure after step 5.
- Blender version differences can break byte-identical rebuilds.
- Framework scope creep; keep the first version small.
- Reference rights are not cleared.

## 8. Not verified

No geometry, rig, animation, browser behaviour, performance on phones, deployment or catalog behaviour has been verified for v5. The numbers in sections 2.1 to 2.6 are proposals.

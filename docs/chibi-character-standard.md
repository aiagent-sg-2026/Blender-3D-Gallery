# Chibi Character Standard (draft v0.1)

Status: **draft; owner answers recorded 2026-11-15 (section 8)**. It is derived from the Chibi Visitor v4 build and its QA run (`models/chibi-visitor-v4/`) plus the v5 Mall Guide concept ([plan](chibi-mall-guide-v5/plan.md)). The owner has not approved it. Numbers marked *proposed* are starting points to be tuned on the first v5 build; numbers marked *v4* are measured values from the v4 README.

## 1. Purpose

Make every chibi character in the gallery look like one family, load cheaply, and pass the same checks, so that a new character is a fill-in-the-blanks job rather than a new design problem.

## 2. Style definition

| Item | Rule |
| --- | --- |
| Look | Glossy vinyl-toy figure, smooth rounded forms, flat-colour materials, no PBR surface detail |
| Proportion | Total height about 2.5 heads (v4 is about 1.00 m tall) |
| Eyes | Large, glossy, in the lower third of the head; face is a single painted texture plus a few geometry features (brow ridge, nose, mouth cavity) |
| Hair | 6 to 8 thick, blunt, rounded locks. No pointed tips, no thin shingles, no ahoge. Reason: v4's pointed shingles failed independent review (G5) and could not be fixed by tip tuning |
| Hands and feet | Mitten or fist hands, simplified sneaker or boot; no individual finger rigging |
| Palette | Per scene. The mall uses jade, ivory, champagne-brass (see `virtual-mall-foundation-v1-scope.md`) |
| Background in references | Solid pale lavender-grey, so silhouettes can be traced |

## 3. Reference pack (required before modelling)

Folder `models/<name>/reference/` holds:

1. A turnaround sheet with front, three-quarter, side and back at the same scale and pose.
2. A consistency check: handedness of props, badge side and colours agree across views (v4's sheet had a strap colour and bag position conflict; those cost review time).
3. A provenance note: how the image was made (tool, date, prompt file) and the rights status. AI concept images are *not* rights-cleared by default.

The reference is not embedded in the GLB.

## 4. Model contract

- Coordinates: glTF +Y up, front +Z, feet on y = 0 (*v4*).
- One placement root named `<Name>` containing named parts: `Head`, `Hair`, body garments, `Arm.L/R`, `Leg.L/R`, `Shoe.L/R`, props (*v4* uses 13 parts).
- Parts are separate meshes grouped so a rig can be added later.
- Materials: flat colour; at most one face texture of 1024 px (*v4*); everything else solid.
- Budgets (*owner-approved 2026-11-15*; v4 measured 113,428 triangles and 25 draw calls, which is heavier than a gallery card wants): at most 40,000 triangles and 20 draw calls. Raise only with a written reason.
- Required rig layer (owner decision 2026-11-15): armature of 20 bones or fewer and three shape keys (neutral, smile, surprised). v4 had none, so v4 does not meet this standard.

## 5. Build pipeline

1. Reference pack (section 3).
2. Proportion blockout; overlay against the reference.
3. Parts, then head, then hair (thick locks, fitted under any headwear).
4. Materials.
5. Export GLB and preview renders.
6. QA gate run.
7. Register in `models/catalog.json` only after the gate passes.

All Blender work goes through the Blender MCP server or headless Blender; the generating script is committed so the model can be rebuilt (v4 pattern: `generate.py`).

## 6. Quality gate (reuse v4's structure)

| Gate | Check | Pass |
| --- | --- | --- |
| G1 | glTF Validator, triangles, draw calls | 0 errors, 0 warnings; within budget |
| G2 | Headless rebuild is byte-identical to the MCP build | Same SHA-256 |
| G3 | Independent Three.js load of the exact GLB | No console errors; front, three-quarter, back checked |
| G4 | Silhouette rows against the reference | Mean and maximum offset within a threshold set before the run (v4: mean 8 px, max 15 px at 645 px per metre) |
| G5 | Visual review by a reviewer who did not build it | No P0/P1; author's own pass is not enough (v4 lesson) |
| G6 | `npm run validate:assets` and `npm test` | Pass |

Status words: PASS, FAIL, REWORK, NOT_RUN. Record evidence in `qa/run-NNN/`. Do not call a model interactive or catalogued before G1 to G6 pass and the viewer has been tested.

## 7. Deliverables per character

`README.md` (parts, rebuild, gate table, known differences, rights), `generate.py`, `sources/*.blend`, `exports/*.glb`, `previews/`, `verification/`, `qa/`, `reference/`.

## 8. Owner decisions (2026-11-15)

- Budget: at most 40,000 triangles and 20 draw calls.
- Rig and shape keys are mandatory: armature of 20 bones or fewer plus neutral, smile, surprised.
- G5 review: a fresh agent reviews against the reference first, then the owner makes the final check.
- Rights: AI-generated references are internal references only; the model is original modelling and the reference is not embedded in the GLB. State the source in the README and re-check before public release.

## 9. Mall Guide v5 decisions (2026-11-15)

- Animations: idle breathing with blink, walk cycle, wave / point. The armature must support an arm-raise for the sign pose.
- Sign: a separate prop part with a swappable icon (texture or material switch, so the arrow can point in different directions); it is not part of the body mesh.
- Expressions: the three shape keys also drive eyebrows and cheeks. The head topology needs edge loops around the brows, eyes, mouth and cheeks.
- Look: keep the boy character of sheet B.
- Budget impact: the 40,000 triangle / 20 draw call budget still applies; the swappable icon must not add a second large texture (use a small atlas).

## 10. Mall Guide v5 detail decisions (2026-11-15)

- Sign icons (small atlas, symbols only, no readable text): four direction arrows; facility icons (restroom, lift, escalator, service desk); welcome and open/closed status; shop icons. The New Moon brand mark needs rights confirmation before use; use a neutral icon for Sample Store.
- Walk: two loops, a bouncy small-step walk and a calm normal walk, plus a slower and a faster variant is *not* required unless the first two are accepted.
- Gestures: three clips, wave (left hand), hold-and-point (right hand, sign raised), put sign down. Because the sign can be put down, it must be a separate prop that can attach to and detach from the right-hand bone.
- Use cases: NPC in the mall scene, display model on gallery cards, assistant avatar in dialogs.
- Consequences (to verify during the build, not yet tested): many NPCs at once make the triangle and draw-call budget the critical limit, so a lower-detail variant for distant NPCs should be planned; the dialog avatar shows the upper body, so the face and expression quality gate applies to the head close-up views; the card model needs the face and hair to hold up close.

## 11. Mall Guide v5 further decisions (2026-11-15)

- Distant NPCs: export an extra low-detail GLB (target about 8,000 triangles, no shape keys; *proposed* figure, to be measured). The full model keeps the 40,000 triangle budget.
- Dialog assistant avatar: pre-rendered still images, one per expression (neutral, smile, surprised), so a dialog does not need WebGL. Render them from the final GLB, not from the concept images.
- Variants: one standard uniform plus a festive uniform (e.g. Christmas hat, Chinese New Year accessories). Festive items are separate swappable parts or material switches so the base body is shared. Which festivals are covered is still open; tie it to the festival model plan.
- Supplementary references (generated 2026-11-15, AI concept images, same rights status as sheet B): `docs/chibi-mall-guide-v5/mockup/expressions-b.png` (three expressions, front and three-quarter) and `poses-b.png` (wave, hold-and-point, put sign down).
- Reference caveats: the brow difference between neutral and smile is subtle, so exaggerate it in the shape keys.
- Put-down pose: `pose-put-down-b2.png` (front three-quarter and side) replaces the third pose of `poses-b.png`, where the hand still touched the sign. The right hand is open and clear of the handle and the sign stands against the right shin. In the model, place the sign by position, not physics; the hand only needs a relaxed pose.

## 12. Morph-target smoke test (2026-11-15)

Test in `models/chibi-mall-guide-v5/qa/morph-smoke/` (Blender 5.1.2, Three.js 0.187.0 in Node): shape keys export as named morph targets, a morph animation track plays through `AnimationMixer`, and a rigid single-bone skinned mesh loads. Findings that change the standard:

- A skinned mesh parented under the armature gives the validator warning NODE_SKINNED_MESH_NON_ROOT, which fails G1 (0 warnings). Keep skinned meshes as scene roots (unparented) when exporting.
- The head mesh's shape keys must be the only source of expression morphs; add a `blink` key (the idle animation needs it).
- Not tested: rendering, the gallery's `src/viewer.js` in a browser, and the mall runtime. The viewer shows models at rest, so a consumer must drive influences itself.

## 13. Modular build and attachment sockets (proposal, 2026-11-15)

Status: proposal; the owner chose to record it, not yet to adopt it as final. Nothing here is implemented or tested.

### 13.1 Build scripts (layer 1)

Each character splits its generator by responsibility instead of one monolith (v4's `generate.py` is 1,060 lines; the GJH Mall Visitor's is 207). Suggested files inside `models/<name>/`:

| File | Responsibility |
| --- | --- |
| `config.py` | Single source of truth: proportions, colours, part sizes, budgets |
| `head.py` | Head topology and face edge loops |
| `hair.py` | 6 to 8 blunt locks fitted under headwear |
| `garments.py` | Vest, shirt, shorts, cap, socks, shoes |
| `limbs.py` | Arms, legs, gloves |
| `rig.py` | Armature (20 bones or fewer), rigid single-bone binding, sockets |
| `shapekeys.py` | smile, surprised, blink (brows and cheeks included) |
| `anim.py` | Clips and foot-contact baking |
| `export.py` | Full and low-detail GLB |
| `qa/` | Gate scripts, as in v4 |

Rules: numbers live only in `config.py`; modules read config and do not duplicate values; the build stays deterministic and headless (no interactive sculpt, which v4 could not rebuild headlessly). Do not extract a shared library until a second character shows which parts really repeat.

### 13.2 Runtime modules (layer 2)

- Body plus base uniform: one GLB.
- Sign: a separate prop GLB attached to the right-hand socket (supports swappable icons and put-sign-down).
- Festive accessories (hat, decorations): separate small GLBs attached to head or body sockets; the base body is not duplicated.
- Low-detail variant: same scripts, different parameters.
- Cost: the consumer code must attach props, and every prop needs its own gate run.

### 13.3 Socket convention (to be validated)

- Sockets are empty bones or nodes named `SOCKET_<Name>`, e.g. `SOCKET_Hand_R`, `SOCKET_Head_Top`, `SOCKET_Chest_L`.
- Each socket has unit scale and an agreed local axis (proposal: +Y up, +Z forward in rest pose); a prop is modelled with its attachment point at its own origin and the same axis.
- Props are scene roots (the skinned-mesh rule from section 12 applies to skinned props).
- Open: whether sockets are bones inside the armature (counted against the 20-bone limit) or plain nodes parented to bones; whether the mall runtime and the gallery viewer attach props the same way. Both need a test before this section is accepted.

## 14. Framework

The plan to extract a general build framework is in [chibi-framework-design.md](chibi-framework-design.md) (proposal; nothing implemented).

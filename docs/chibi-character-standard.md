# Chibi Character Standard (draft v0.1)

Status: **proposed**. It is derived from the Chibi Visitor v4 build and its QA run (`models/chibi-visitor-v4/`) plus the v5 Mall Guide concept ([plan](chibi-mall-guide-v5/plan.md)). The owner has not approved it. Numbers marked *proposed* are starting points to be tuned on the first v5 build; numbers marked *v4* are measured values from the v4 README.

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
- Budgets (*proposed*, v4 measured 113,428 triangles and 25 draw calls, which is heavier than a gallery card wants): at most 40,000 triangles and 20 draw calls. Raise only with a written reason.
- Optional layers, only if scoped: armature of 20 bones or fewer; shape keys neutral, smile, surprised.

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

## 8. Open questions for the owner

- Approve or change the triangle and draw-call budgets.
- Is rig and shape-key work mandatory for the standard, or optional per character?
- Who counts as the independent reviewer for G5 (another agent, Codex, or the owner)?
- Rights position for AI-generated references.

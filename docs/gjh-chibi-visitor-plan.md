# GJH Chibi Visitor (Male, 18) — One-Shot Build Plan

Status: built 2026-11-15 (development preview). Results, deviations and open gates are in section 9.
Reference: owner character sheet "GJH Virtual Mall – Chibi Visitor (Male, 18) v1.0".

## 1. Context and hard constraints

The owner wants this character built as a real Blender model, in one continuous run, from the character sheet.

- **Fresh code only.** Do not import, copy or adapt any existing repository script, including the v4/v5 `kit.py`, `rig_base.py` or `hair_gate.py`, and the GJH v2/v3 `generate.py`, `export.py` or `rig.py`. Write every module new.
- **No RunPod, no TRELLIS and no Hunyuan3D.** Generated meshes are not used, not even as reference. Geometry comes only from local headless Blender Python.
- **Allowed reuse is limited to repo-wide acceptance gates.** These are `npm run validate:assets`, `npm test` and the catalog rules in `scripts/catalog.mjs`. They judge the result; they do not build it.
- Blender 5.1.2 at `/Applications/Blender.app/Contents/MacOS/Blender`, run headless with `--background --factory-startup --python-exit-code 1`.
- Every number lives in `config.py`; no magic numbers in other modules.

## 2. Target spec (from the sheet)

| Item | Value |
|---|---|
| Height | 1.30 m, feet on ground (z = 0), +Z up in Blender, faces −Y (exports as glTF +Z front) |
| Proportion | 2.5 heads: head unit H = 0.52 m (hair crown to chin) |
| Triangles | 3,000–8,000 total (target ≈ 7,000) |
| Draw calls | ≤ 10 (one material per colour group, face decal atlas) |
| Rig | Humanoid, 20 deform bones + 3 socket bones |
| Format | single GLB, textures embedded, glTF 2.0 |
| Expressions | Default, Happy, Wink, Surprised, Thinking, Excited (+ Blink) |
| Clips | Idle, Walk, Run, Sit, Wave, Talk, Shop/Browse, Pick Up, Inspect, Point, Nod, Cheer |

### 2.1 Key landmarks (first estimate, front view ≈ 346 px/m; step 1 re-measures)

| Landmark | Height (m) | Notes |
|---|---|---|
| Hair crown | 1.30 | messy volume adds ≈ 0.06 above skull |
| Skull top | 1.22 | |
| Eye centre | 0.98 | eyes ≈ 0.13 tall, centres x = ±0.10 |
| Chin | 0.81 | |
| Shoulder | 0.74 | shoulder width ≈ 0.40 |
| Tee hem | 0.42 | loose, slightly flared |
| Crotch | 0.38 | |
| Jeans hem (cuffed) | 0.10 | wide straight legs, rolled cuff |
| Shoe top | 0.08 | shoe length ≈ 0.22, chunky sole |

Head width (hair) ≈ 0.56, face width ≈ 0.39. Hands reach ≈ 0.45.

### 2.2 Colour palette (flat PBR, roughness listed)

| Group | Hex | Roughness | Notes |
|---|---|---|---|
| Skin | `#F3D2B5` | 0.6 | soft subsurface look faked with blush in face atlas |
| Hair | `#2E2420` | 0.55 | darker AO baked into vertex colour at lock roots |
| T-shirt | `#F6F6F4` | 0.85 | |
| Jeans | `#4A6FB0` | 0.9 | 256 px denim noise + seam lines texture |
| Shoes | `#EDEDED` sole `#FFFFFF` | 0.7 | |
| Backpack | `#2C2E33` | 0.75 | |
| Watch | `#26272B` | 0.4 | |
| Eyes / face | atlas | 0.5 | iris dark brown `#3A2418`, white highlights |

## 3. File layout (all new)

```
models/gjh-chibi-visitor/
  README.md
  metadata.json
  reference/character-sheet-v1.webp     # owner sheet (copied in)
  reference/front.png side.png back.png  # crops used by QA
  src/
    config.py      # every dimension, colour, budget, bone position, clip timing
    mesh.py        # new primitive builders: rounded box, loft along profile, tube, lock, shell
    materials.py   # palette materials, denim texture, face atlas painter (numpy -> image)
    body.py        # torso core, neck, arms, hands (mitten + thumb), legs
    clothes.py     # tee (sleeves, collar), jeans (wide legs, cuffs, seams), shoes
    head.py        # skull, ears, face decals (eyes, brows, mouth) + shape keys
    hair.py        # hair shell, 6–8 blunt locks, 3–4 tufts, root AO
    props.py       # backpack (body, straps, pocket, zip), watch (strap, face)
    rig.py         # armature, weights, sockets
    anim.py        # 12 clips as NLA actions + expression keys
    export.py      # GLB export, turntable renders, previews
    build.py       # entry point: runs every module in order, writes all outputs
  qa/
    measure.py     # landmark heights, widths, tri count, draw calls -> JSON
    silhouette.py  # render orthographic masks, compare with reference crops
    overlap.py     # BVH overlap check between parts (allow list in config)
    deform.py      # pose stress test: stretch/collapse detection per bone
    check-glb.mjs  # three.js load, clips, morphs, skin, bounds
  exports/gjh-chibi-visitor.glb
  sources/gjh-chibi-visitor.blend
  previews/ (thumbnail.webp, turntable-000..315.png, expressions.png, clips/*.png)
  qa/run-001/ (report.json, renders, logs)
tests/gjh-chibi-visitor.test.mjs
```

Single build command:

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python models/gjh-chibi-visitor/src/build.py -- --out models/gjh-chibi-visitor
```

## 4. Build stages (run in one shot by `build.py`, each stage gated)

Each stage writes a JSON report. `build.py` stops with a non-zero exit if a gate fails, so the run either finishes clean or names the exact failing stage.

### Stage 0 — Reference
- Copy the sheet into `reference/`, crop front, side and back views to matching pixel scale (feet line and crown line aligned).
- Extract binary silhouette masks from the crops (background is a flat lavender; threshold on distance from it).
- Gate: masks exist; measured crown-to-feet height in each crop agrees within 2 %.

### Stage 1 — Blockout
- Build simple volumes from `config.py` landmarks: head sphere, torso box, leg and arm tubes, shoe boxes, backpack box.
- `qa/measure.py` checks every landmark in section 2.1 within ±2 cm.
- `qa/silhouette.py` front and side: IoU ≥ 0.85 against the reference masks (blockout tolerance).
- Purpose: lock proportion before any detail.

### Stage 2 — Body and clothes (budget ≈ 3,000 tris)
- **Body under clothes is not modelled** except exposed parts: neck, forearms, hands. This saves triangles and removes clipping.
- **Tee:** lofted torso shell (8 radial segments × 6 rings), short sleeves as flared tubes, rounded collar band, slight hem flare. ≈ 700 tris.
- **Arms/hands:** forearm tube from sleeve to wrist, mitten hand with separate thumb, 4 slight finger grooves via shape only. ≈ 500 tris both.
- **Jeans:** two wide straight legs lofted from a waist ring, crotch bridge, rolled cuff ring, back pockets and side seams in the texture, not geometry. ≈ 900 tris.
- **Shoes:** chunky sneaker loft (rounded toe, thick sole as second loop), laces in texture. ≈ 600 tris both.
- Gates: tri budget; `qa/overlap.py` finds no unintended intersections (allowed: neck into collar, wrist into sleeve, leg into shoe); silhouette IoU front/side ≥ 0.88.

### Stage 3 — Head and face (budget ≈ 1,300 tris)
- **Skull:** subdivided rounded shape with a soft jaw and cheeks, small ears; ≈ 900 tris.
- **Face decals** are thin meshes lying 1 mm above the skin, using one 1024 px atlas:
  - eye (white, large dark iris, two highlights) ×2, brows ×2, mouth.
  - Expressions are glTF morph targets on the decal meshes, so they work natively in three.js without runtime texture code.
- Shape keys: `blink`, `wink_L`, `happy` (eye arcs and open smile), `surprised` (round eyes, "o" mouth, brows up), `thinking` (one brow up, flat mouth), `excited` (wide eyes, big open smile), `talk_open` (mouth only).
- Gates: front face render compared side by side with the sheet "Default" crop; eye-centre height and spacing within ±1 cm; each key renders without the decal crossing the skin.

### Stage 4 — Hair (budget ≈ 1,500 tris)
- **Shell first:** one closed hair volume fitted to the reference silhouette in all three views. This alone must pass the silhouette gate.
- **Locks second:** cut the shell into 6–8 thick, blunt, rounded locks (fringe left, fringe right, top swirl, two sides, two back) plus 3–4 small tufts for the messy outline. Locks are lofted strips with thickness and rounded ends; no pointed tips.
- Root darkening via vertex colour for depth.
- Gates: hair-included silhouettes vs reference masks, front/side/back each mean error ≤ 8 px and max ≤ 15 px at reference scale; no hair through the face or ears.

### Stage 5 — Props (budget ≈ 1,000 tris)
- **Backpack:** rounded body, front pocket, top handle, two straps that follow the shoulders and chest; zip line in texture. ≈ 800 tris.
- **Watch:** strap ring around the left wrist, rectangular face. ≈ 200 tris.
- Attach with socket bones `SOCKET_Back`, `SOCKET_Wrist_L`, and add `SOCKET_Hand_R` for held items.
- Gates: straps do not cut into the tee in rest pose or in arm-raise stress pose.

### Stage 6 — Rig and skin
- 20 deform bones: `root, hips, spine, chest, neck, head, shoulder.L/R, upper_arm.L/R, forearm.L/R, hand.L/R, thigh.L/R, shin.L/R, foot.L/R`.
- Socket bones (non-deforming): `SOCKET_Back` (chest), `SOCKET_Wrist_L` (forearm.L), `SOCKET_Hand_R` (hand.R).
- Rest pose: A-pose 30° arms, matching the sheet rig panel.
- Weights: written by code per vertex from distance along bone segments with smooth blending zones at joints (no bone heat). Head, hair and face decals are rigidly bound to `head`. The backpack is bound to `chest` and the watch to `forearm.L`.
- Gates: `qa/deform.py` poses each joint to its limit, then checks no triangle area collapses below 20 % or stretches above 300 %, and no vertex is unweighted or has more than 4 influences.

### Stage 7 — Animation (12 clips, 30 fps, in place)
| Clip | Frames | Notes |
|---|---|---|
| Idle | 90 loop | breathing, small sway, blink at frame 60 |
| Walk | 32 loop | contact/pass/contact, foot contact on ground |
| Run | 20 loop | forward lean, bigger arm swing |
| Sit | 40 + hold | lowers hips to seat height 0.30 m |
| Wave | 48 | right arm up, 3 waves, happy face |
| Talk | 60 loop | head nods, `talk_open` cycles |
| Shop/Browse | 90 loop | head turns left/right, slight lean |
| Pick Up | 50 | crouch, right hand to ground, rise |
| Inspect | 70 | raise held item to face, thinking face |
| Point | 40 | right arm forward, index pose via hand bend |
| Nod | 30 | two head nods |
| Cheer | 40 | both arms up, excited face |
- Expressions are keyed inside the clips that need them, and also exported as separate morph targets for runtime use.
- Gates: looping clips match first/last frames; feet stay ≥ 0 and ≤ 1 cm sliding during contact in Walk/Run; no mesh below ground in any frame.

### Stage 8 — Export and previews
- Export GLB with skins, morph targets, NLA clips as named animations, embedded textures, +Y up glTF, Apply modifiers.
- Save `sources/gjh-chibi-visitor.blend`.
- Renders (Eevee, fixed 3-point studio light, lavender background like the sheet): 8 turntable angles, expressions strip, one frame per clip, thumbnail.

### Stage 9 — QA and gallery integration
- `npm run validate:assets`: glTF validator 0 errors, 0 warnings.
- `qa/check-glb.mjs` in three.js: loads, 12 named clips, 7 morph targets, all meshes skinned, bounds height 1.30 ± 0.02 m, tris 3,000–8,000.
- `tests/gjh-chibi-visitor.test.mjs` (new, written from scratch) runs those checks under `npm test`.
- Add the catalog entry to `models/catalog.json` (category `Characters`, browse `People & Characters`, no `root` field because the mesh is skinned, embedded textures).
- Run the gallery dev server and check that the model loads, plays clips and shows the fallback on error.
- Independent review: a fresh reviewer compares the turntable and expression renders with the sheet and lists defects. P0/P1 defects are fixed before handing to the owner.

## 5. Triangle budget

| Part | Tris |
|---|---|
| Skull + ears | 900 |
| Face decals | 400 |
| Hair | 1,500 |
| Tee | 700 |
| Arms + hands | 500 |
| Jeans | 900 |
| Shoes | 600 |
| Backpack | 800 |
| Watch | 200 |
| Reserve | 500 |
| **Total** | **7,000** |

## 6. Acceptance (definition of done)

1. One command builds everything from scratch with exit code 0.
2. All stage gates pass, with reports in `qa/run-001/`.
3. GLB validates clean; three.js test passes in `npm test`.
4. Turntable, expressions and clip renders exist in `previews/`.
5. Independent review has no open P0/P1.
6. Catalog entry added; gallery loads the model.
7. Owner reviews the final package once.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hair silhouette misses (past failure) | Fit a single shell first; locks are cut from the passing shell, so the outline is preserved |
| Face looks flat or "sticker-like" | Decals follow skull curvature (projected), slight inset shading in atlas, highlight sparkle |
| 8k budget too tight for the hair look | Reserve 500 tris; tufts can drop before locks |
| Shoulder/elbow deformation at low poly | Extra edge loops only at joints; deform gate catches collapse |
| Wink and blink look wrong on decals | Eye decal keys scale to a lid arc instead of hiding geometry |
| Sheet views are not perfectly orthographic | Use mean error gates plus a manual reviewer pass, not pixel-perfect matching |

## 8. Out of scope

- Outfit variants, LODs, lip sync, and game state machines.
- Publishing or deployment beyond the local gallery and catalog entry.

## 9. Results (2026-11-15 build)

Built by `models/gjh-chibi-visitor/src/build.py` in about 30 seconds (Blender 5.1.2, headless).
Gate report: `models/gjh-chibi-visitor/qa/run-001/report.json`. Browser check:
`models/gjh-chibi-visitor/qa/run-001/browser.json`.

| Stage | Gate | Result |
|---|---|---|
| 0 | Reference views agree on height (spread <= 2 %) | Pass (0.9 %) |
| 1 | Height 1.30 +/- 0.02 m, feet on the floor, body outline IoU >= 0.85 | Pass |
| 2 | 3,000-8,000 triangles, <= 10 draw calls, no forbidden overlaps, no inside-out parts, IoU >= 0.88 | Pass (7,964 triangles, 10 draw calls) |
| 3 | Seven expression keys, each moving the face; no decal crossing the skin in any expression | Pass |
| 4 | Head outline mean <= 8 px **and max <= 15 px** per view | **Fail**: means pass (about 5-7 px); the worst rows miss by about 22 px |
| 5 | Backpack and straps do not cut into the tee | Pass |
| 6 | Weights complete, <= 4 influences, **no triangle below 20 % or above 300 % of its rest area in any clip** | **Fail**: weights pass; 358 triangle-frames (sampled every 4th frame) compress below 20 % |
| 7 | 12 clips, seamless loops, every part above the floor, stance ankle on its track (<= 3 mm), no arm through hair or face and no jeans through the visible tee hem in any sampled frame | Pass |
| 8 | GLB exported | Pass |

Because stages 4 and 6 fail, the build command exits with code 1 (by design; `--keep-going` still
runs and writes everything). The head outline worst rows are 22.5 px (front), 22.0 px (side) and
21.7 px (back) against 15 px (front 21.5, side 22.0); the means are 6.1, 6.7 and 5.6 px against 8 px.
The GLB is 820,152 bytes.

Outside Blender: glTF validator 0 errors and 0 warnings; the three.js browser check loads all
8 skinned meshes, the 7 morph targets and the 3 sockets, and plays every clip with finite bounds
above the floor; `tests/gjh-chibi-visitor.test.mjs` passes; the gallery dev server shows the
model (rest pose) with no console errors.

### Open items

- **Hair outline (stage 4).** The sheet's crown is an irregular, asymmetric peak and its side
  flicks are sharper than this lock system makes. The remaining misses are the top 2-3 cm of the
  crown and the right-side flick. The gate threshold was not changed.
- **Deep-bend compression (stage 6).** Triangles on the inner side of the knee (Sit, Pick Up,
  Walk/Run) and the inner elbow (Wave, Run) compress below 20 % of their rest area, which is normal
  for linear blend skinning at 90-100 degree bends. Close-up renders show no visible tearing, but
  the gate threshold was not changed and the gate is reported as failed.
- The gallery viewer shows only the rest pose. Clips and expressions need a runtime player,
  which was out of scope because the viewer is shared code.

### Independent review (round 1) and what changed

A fresh reviewer compared the renders with the sheet and scored the likeness at about 55 %, with
2 P0 and 11 P1 findings. Each was checked against the model before changing anything:

| Finding | Check | Result |
|---|---|---|
| P0 Thinking reads as neutral | Render | Fixed: squinting, sideways eyes; one brow up; slanted mouth |
| P0 ShopBrowse looks like Idle | Preview frame was a mid-turn frame | Fixed: 35-degree head turns, reach for a shelf, preview at the reach |
| P1 Hair: thin shards, sparse fringe, nape gaps | Render | Improved: blunter wider locks, 2 more fringe locks, 2 more nape locks |
| P1 Eyes light/small, brows thin | Render | Fixed: near-black iris, eyes 14 % larger, heavy lash with a wing, thicker shorter brows |
| P1 Head a rounded box, no nose | Render | Fixed: rounder skull profile, small nose bump |
| P1 Head too small (2.85 vs 2.6 heads) | Measured | Not changed: crown 1.29 m and chin 0.79 m give 2.6 heads, as on the sheet; sleeves were narrowed slightly |
| P1 Jeans hips read as briefs | Render | Improved: longer tee hem over the waistband, softer crotch, continuous denim weave |
| P1 Shoes hidden blocks | Render | Fixed: cuffs raised, taller toe, darker sole line, laces |
| P1 Straps stepped | Render | Improved: denser, smoothed path; a small corner remains under the arm |
| P1 Paddle hands | Render | Improved: rounder mitten hand and bigger thumb (no finger bones in the 20-bone rig) |
| P1 Hands possibly through head/hips | Overlap test per frame | Not reproduced; the test instead found blush and mouth decals crossing the skin, now fixed and gated |
| P1 Surprised/Excited weak | Render | Fixed: bigger eyes and O mouth; Excited uses "> <" eyes |
| P1 Walk/Run/Inspect/PickUp poses weak | Render | Fixed: longer strides and lean, item at chest height, deeper squat; clip previews use a side-on camera |

Also found during the checks: the right ear was built inside-out (fixed, and stage 2 now fails on
any inside-out part).

### Independent review (round 2)

A second fresh reviewer scored the likeness at about 60 % and raised 4 P0 findings:

| Finding | Check | Result |
|---|---|---|
| P0 Wink_L broken (arc at brow height, brow gone) | Zoomed render vs Happy | Not reproduced: the arc sits at eye height like Happy and the brow is present; a fringe lock hid the brow's outer half, so the fringe tips were raised |
| P0 Sit: jeans poke through the tee hem | Browser frame and overlap count | Confirmed and fixed: the front hem now follows the thighs (lap weights), the hem flares slightly, the jeans waist sits lower; a new stage-7 check covers every clip |
| P0 Run reads as walk | Render | Fixed: 20-degree lean (mostly in the chest), pumping arms, preview at a mid-stride frame |
| P0 Pick Up reads as a bow, chin into chest | Render and head-vs-torso overlap | Pose fixed (deeper squat, head up); no extra chin overlap was found |
| P1 Wave/Cheer hands in the hair | Overlap count | Confirmed for the new poses and fixed (hand in front of the hair; Cheer is a wide V). Chibi arms (0.37 m) cannot clear the 0.52 m-wide hair straight overhead, so Cheer stays a V |
| P1 Hair/fringe style, straps, shoes | Render | Partly addressed (fringe raised, strap denser, hair less glossy); the sheet's parted fringe and a fully smooth strap turn remain open |


### Deviations from this plan

- No separate blockout mesh; stage 1 measures the detailed model.
- The rest pose keeps the arms hanging as on the sheet instead of a 30-degree A-pose.
- The sheet mask is unreliable for the white sneakers (same colour as the background), so
  silhouettes ignore rows below 0.10 m.
- Hair was built as a thick cap with feather locks in rows, not "shell first, then cut into
  6-8 locks": that approach read as a helmet in early renders.
- The cuffs use their own plain material, giving 10 draw calls (the limit).
- The mouth-open shape key is named `talk` (the plan said `talk_open`).

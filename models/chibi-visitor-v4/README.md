# Chibi Visitor v4

A static, full-body chibi character modelled in Blender 5.1.2 from the owner's "Chibi Visitor v4.0" character sheet (`reference/character-sheet.webp`, kept local, not committed). It was built through the Blender MCP server (official Blender Lab extension 1.0.3). No image-to-3D service, downloaded mesh, add-on asset or downloaded texture is used, and the sheet is not embedded in the model.

- `exports/chibi-visitor-v4.glb`: character only, one placement root `ChibiVisitorV4`, glTF +Y up, front +Z, feet on y = 0, about 1.00 m tall (1.0024 m including the top tuft). No armature, animation or morph target. The head carries one 1024 px face texture with UVs.
- `sources/chibi-visitor-v4.blend`: editable copy of the Blender session (scene "Chibi Visitor v4", collections `CV4 Model` and `CV4 Studio`).
- `sources/head-sculpt.json`: the skull baked from `sculpt_head.py`; `generate.py` loads it.
- `previews/`: orthographic Blender renders (front, side, back, three-quarter), `reference-comparison.png` (sheet on top, renders below) and `head-study/` (sculpt passes and head close-ups against the sheet).
- `verification/`: an independent Three.js load page (add `&perf=1` for frame timing) and its browser screenshots (front, three-quarter, back).
- `qa/`: the quality gate, `check-glb.mjs` (structural GLB checks), `silhouette-rows.py` + `silhouette-gate.py` (these two need the local, uncommitted character sheet) and the evidence of run 001 (`qa/run-001/` and `qa/run-002/`).

## How the head is made

1. `sculpt_head.py` (interactive Blender only): an even quad sphere is blocked out with the same silhouette formula as the generator's parametric skull, relaxed at the jaw/nape, then worked with real Blender sculpt brushes (Draw, Clay Strips, Inflate/Deflate, Smooth, Pinch/Magnify) for cheeks, eye sockets, brow, nose, mouth and chin. Strokes use the VIEW_3D area of the connected Blender; the Grab brush does not respond to scripted strokes.
2. The result is baked to `sources/head-sculpt.json`.
3. `generate.py` fuses that skull with the ears, nose and neck (voxel remesh, smooth, decimate), paints the face texture and builds the hair.

Measured contribution of the sculpt: the baked skull is a mean 1.25 mm, 95th percentile 6.5 mm, maximum 16.8 mm from the parametric skull (nearest-surface distance over 6,146 vertices). It is shallow relief on the same silhouette, plus the jaw/nape relax; most of the facial character comes from the painted texture. Cheek relief is faint.

## Parts

Thirteen mesh objects, grouped so a rig can be added later: `Head` (skin, ears, nose, neck, face texture), `Hair` (fused scalp cap, fringe and ahoge, plus 17 separate shingled back locks kept un-remeshed so the creases survive, with ambient occlusion baked into vertex colours), `Hoodie`, `Shorts`, `Arm.L/R` (arm and a fist with four fingers and a thumb), `Leg.L/R` (leg and sock), `Shoe.L/R`, `Watch` (left wrist) and `Bag` (satchel and strap).

## Rebuild

- Sculpt (optional): `sculpt_head.py` needs an interactive Blender with a 3D viewport and the Blender MCP bridge; it cannot run headless. Re-run it only to change the skull.
- Build: in the connected Blender send `generate.py` through `execute_blender_code` and call `build()` then `write_outputs()`. It only replaces the scene "Chibi Visitor v4" and data it tagged itself.
- Headless, from the repository root (consumes the baked `sources/head-sculpt.json`; falls back to the parametric skull when that file is missing):

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-visitor-v4/generate.py
```

This rewrites the blend, GLB and four previews in this directory. Set `CV4_OUT` to write somewhere else.

## Quality gate and verification (2026-11-15, run `qa/run-002`; run 001 is kept for history)

Status: **REWORK**. Every tool-checked gate passes; three independent visual reviews (a fresh reviewer each time, given only the sheet and the renders) still rank hair-surface defects P1.

| Gate | Skill gate | Criterion | Result (run 002) |
| --- | --- | --- | --- |
| G1 | G1/G5/G7 | glTF Validator 0 errors/warnings; at most 150,000 triangles, 30 draw calls | PASS: 0/0/0/0, 127,240 triangles, 25 draw calls, 2,865,168 bytes |
| G2 | G8 | headless rebuild is byte-identical to the MCP build | PASS: `2a2c9791ef2c2102c484bead47d68ff6caf15392e41f4bd24cbe2b8a1d5c98b6` |
| G3 | G6 | Three.js loads the exact GLB, no console errors | PASS: 25 meshes, no errors |
| G4 | G4 | head rows (z >= 0.60 m): mean <= 8 px, no row beyond 15 px, flick/tuft tip rows (z > 0.94 m) excluded | PASS: front 6.0 / 11, side 7.2 / 13, back 6.3 / 15 px (645 px = 1 m) |
| G5 | G4 | independent visual review: no P1 | FAIL: see below |
| G6 | G8 | `npm run validate:assets`, `npm test` | PASS: 678 tests (run on the previous geometry; the model is not in the catalog) |

Not run: frame time for this build (the browser pane was hidden, so animation frames were throttled; run 001 measured p50 16.7 ms and p95 18.4 ms on an earlier build only), physical-device performance, a frozen golden render, release approval.

One crop artefact is excluded from G4: in the side view the sheet crop at z = 0.74-0.78 m catches the tip of the neighbouring back view's hair wing (x 757-760; `qa/run-001/screenshots/side-gate-crop-ref.png`). Silhouette numbers taken earlier in this session from stale renders were discarded; the table above uses fresh renders (`qa/run-002/silhouette-rows.txt`). Whole-body rows are in `silhouette-rows-whole-body.txt`: body rows are mostly within 15 px, the hoodie is about 1.5 cm wide, the side torso is 12-22 px deep, and the jaw is about 1 cm higher and 14 px narrower than the sheet's (rows below z = 0.04 m are contaminated by the sheet's ground shadow).

Hair colour against the sheet (back view, brown pixels): mean luminance 0.298 against 0.293, standard deviation 0.062 against 0.077. Ambient occlusion is baked into the hair's vertex colours so the creases between locks stay dark in any viewer.

## Known differences from the sheet

- Open P1 from the independent reviews (run 002): the rear hair still reads as overlapping plates with hard creases rather than long swept locks with a parting; the wing flicks at the temples are cone-like (horns from behind); the ahoge is a thin stalk; a dark wedge sits in front of each ear and slits beside the cheeks. Tip bluntings by width floor or rounder profile made the hair fuller and failed the silhouette gate, so a real fix needs a different lock model (long, tapered, comb-flowing cards merged into larger shells), not tip tuning.

- Hair now reads as layered shingles with creases and lifted tips, and the back is a fan of locks off the crown. It is still more regular than the sheet's, whose locks vary more in length and curl; the tips of the wing flicks and the top tuft deviate from the sheet by up to about 40 px in the silhouette rows.
- P2: a small dark gap remains at the front of each ear where the sideburn, skull and ear meet; lengthening the sideburns did not remove it, so that change was reverted.
- The hood on the back is flatter than the sheet's, the hands are simple fists and the shoes are a simplified sneaker (toe cap, three laces, two side stripes).
- The sheet is inconsistent in two places. The strap is dark brown in the front and three-quarter views but tan in the side and back views: dark brown is used throughout. The bag hangs at the front right hip in three views but is drawn behind the hip in the back view: the front right hip is used.
- Not done: rig, animation, facial shapes, level of detail, registration in `models/catalog.json`, gallery viewer acceptance and physical-device performance (QA-32 is NOT_RUN).

Rights: original asset for the owner's projects. The character sheet is the owner's supplied reference; public redistribution terms for it have not been specified.

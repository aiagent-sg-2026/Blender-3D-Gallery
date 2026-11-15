# Chibi Visitor v4

A static, full-body chibi character modelled in Blender 5.1.2 from the owner's "Chibi Visitor v4.0" character sheet (`reference/character-sheet.webp`, kept local, not committed). It was built through the Blender MCP server (official Blender Lab extension 1.0.3). No image-to-3D service, downloaded mesh, add-on asset or downloaded texture is used, and the sheet is not embedded in the model.

- `exports/chibi-visitor-v4.glb`: character only, one placement root `ChibiVisitorV4`, glTF +Y up, front +Z, feet on y = 0, about 1.00 m tall (1.0024 m including the top tuft). No armature, animation or morph target. The head carries one 1024 px face texture with UVs.
- `sources/chibi-visitor-v4.blend`: editable copy of the Blender session (scene "Chibi Visitor v4", collections `CV4 Model` and `CV4 Studio`).
- `sources/head-sculpt.json`: the skull baked from `sculpt_head.py`; `generate.py` loads it.
- `previews/`: orthographic Blender renders (front, side, back, three-quarter), `reference-comparison.png` (sheet on top, renders below) and `head-study/` (sculpt passes and head close-ups against the sheet).
- `verification/`: an independent Three.js load page and its browser screenshots (front, three-quarter, back).

## How the head is made

1. `sculpt_head.py` (interactive Blender only): an even quad sphere is blocked out with the same silhouette formula as the generator's parametric skull, relaxed at the jaw/nape, then worked with real Blender sculpt brushes (Draw, Clay Strips, Inflate/Deflate, Smooth, Pinch/Magnify) for cheeks, eye sockets, brow, nose, mouth and chin. Strokes use the VIEW_3D area of the connected Blender; the Grab brush does not respond to scripted strokes.
2. The result is baked to `sources/head-sculpt.json`.
3. `generate.py` fuses that skull with the ears, nose and neck (voxel remesh, smooth, decimate), paints the face texture and builds the hair.

Measured contribution of the sculpt: the baked skull is a mean 1.25 mm, 95th percentile 6.5 mm, maximum 16.8 mm from the parametric skull (nearest-surface distance over 6,146 vertices). It is shallow relief on the same silhouette, plus the jaw/nape relax; most of the facial character comes from the painted texture. Cheek relief is faint.

## Parts

Thirteen mesh objects, grouped so a rig can be added later: `Head` (skin, ears, nose, neck, face texture), `Hair` (scalp cap plus layered locks and tufts), `Hoodie`, `Shorts`, `Arm.L/R` (arm and a fist with four fingers and a thumb), `Leg.L/R` (leg and sock), `Shoe.L/R`, `Watch` (left wrist) and `Bag` (satchel and strap).

## Rebuild

- Sculpt (optional): `sculpt_head.py` needs an interactive Blender with a 3D viewport and the Blender MCP bridge; it cannot run headless. Re-run it only to change the skull.
- Build: in the connected Blender send `generate.py` through `execute_blender_code` and call `build()` then `write_outputs()`. It only replaces the scene "Chibi Visitor v4" and data it tagged itself.
- Headless, from the repository root (consumes the baked `sources/head-sculpt.json`; falls back to the parametric skull when that file is missing):

```sh
blender --background --factory-startup --python-exit-code 1 --python models/chibi-visitor-v4/generate.py
```

This rewrites the blend, GLB and four previews in this directory. Set `CV4_OUT` to write somewhere else.

## Verification (2026-11-15)

- Khronos glTF Validator 2.0.0-dev.3.10: 0 errors, 0 warnings, 0 infos, 0 hints. 109,083 triangles, 54,929 vertices, 19 materials, 25 draw calls, 2,140,140 bytes. SHA-256 `cf000321b7ddf3cdf5b6b4e9e00379c27c7c958a9b453406eaab5046f1992a01`.
- The headless rebuild (with `CV4_OUT` set to a scratch folder) produced a byte-identical GLB to the MCP build, which also shows the baked skull is read outside MCP.
- Three.js 0.187 loaded the GLB in the app's browser through the Vite dev server: 25 meshes, 109,083 triangles, 0 animations, 1.0024 m tall, no console errors; the face texture (eyes, brows, mouth, blush) renders correctly in the front, three-quarter and back views (`verification/`).
- `npm run validate:assets` and `npm test` (670 tests) pass. The model is not in `models/catalog.json`, so these do not exercise it directly.
- Silhouette rows compared with the sheet (645 px = 1.00 m): the head and torso rows are mostly within about 14 px (2 cm); hair flicks and the top tuft deviate more, with outliers of up to about 40 px. The hair at the crown is up to about 13 px wider than the sheet in the front and back views.

## Known differences from the sheet

- Hair follows the sheet's outline, parting, flicks and tuft, but is built from ridged locks and is busier and less smoothly layered than the sheet; it needs a redesign of the lock flow to match.
- A small dark gap remains at the front of each ear where the sideburn, skull and ear meet; lengthening the sideburns did not remove it, so that change was reverted.
- The hood on the back is flatter than the sheet's, the hands are simple fists and the shoes are a simplified sneaker (toe cap, three laces, two side stripes).
- The sheet is inconsistent in two places. The strap is dark brown in the front and three-quarter views but tan in the side and back views: dark brown is used throughout. The bag hangs at the front right hip in three views but is drawn behind the hip in the back view: the front right hip is used.
- Not done: rig, animation, facial shapes, level of detail, registration in `models/catalog.json`, gallery viewer acceptance and device performance.

Rights: original asset for the owner's projects. The character sheet is the owner's supplied reference; public redistribution terms for it have not been specified.

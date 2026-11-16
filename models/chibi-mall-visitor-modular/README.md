# GJH Chibi Mall Visitor

Open [the offline preview](delivery/preview.html) to orbit the actual exported character, change its expression, play a motion or remove either accessory. The [editable Blender master](delivery/visitor.blend), [runtime GLB](delivery/visitor.glb) and [rebuild kit](delivery/visitor-kit.zip) accompany the preview.

The release-specific visual review, technical measurements and reference comparison are in `delivery/qa/`. The [original rejected export](review/reference-match-20261115/before/) and subsequent independent reviews are retained under `review/`.

The character has a white crewneck, cuffed jeans, white low-top sneakers, a removable dark pack and a character-left watch. The preview embeds its actual GLB and renderer. Orbit and zoom, choose expressions, play/pause clips, or switch equipment independently. The default is the explicitly requested small closed smile; the separate studio portrait uses an open-eyed smiling expression.

The Blender master contains nine character collections, editable UVs, normalized weights, named shape keys and Actions on muted NLA tracks. The shallow A-pose is the rest state. Unmute the corresponding rig and shape-key tracks to audition an Action. Expand **Editable hair guides** to move existing construction handles. Guide evaluation affects runtime hair during export-only and saved-collection assembly. A hidden `sourceOnly` high-resolution hair object preserves the sculpt used for tangent-normal baking; it is excluded from the GLB and follows the head when enabled. The game mesh shares the head rig. The source sculpt, art-directed guide positions and runtime topology are editable in their own collections.

There are six runtime materials and two shared, packed 1024 × 1024 PNGs: base color and tangent normal. The hair occupies a 512 × 512 chart in both shared atlases. Its normals and stationary pigment are baked from the fitted high-resolution sculpt. Eye/face and denim charts retain their main resolution. Tongue, eyelet/lace and sole details have dedicated charts. Exact triangles, dimensions, mesh counts, guide counts and source/export measurements belong to the bound JSON reports, rather than an unverified target in this README.

## Rebuild and preserve edits

Use Blender 5.1.2, Python 3, Node.js and the repository lockfile dependencies. NumPy ships with Blender. Browser checks use Playwright Chromium; install repository dependencies with `npm ci` and, when necessary, `npx playwright install chromium`.

From the repository root:

```sh
python3 models/chibi-mall-visitor-modular/build.py \
  --blender /Applications/Blender.app/Contents/MacOS/Blender \
  --reference "$HOME/Downloads/Chibi Mall Visitor Character Sheet.png" \
  --all
```

Subsequent builds use new timestamped `builds/` folders. `--output PATH` chooses a new destination. With `--all`, `--compare-before PATH` creates hash-bound comparison figures from an earlier delivery with capture manifests. Supply the original 1536 × 1024 sheet for the front landmark overlay. Its cropped panels appear in local comparison figures. Surface pigment and tangent normals live on the character's own UVs.

The full build saves the blockout, head, wardrobe and animated master. It rebuilds the character from the procedural inputs, reassembles the saved collections and re-exports the master. It also checks an isolated guide edit, validates the glTF, rig and weights, plays all twelve clips through the preview controls and compares portraits from Blender and the re-imported GLB. `delivery/qa/build.json` identifies the tested files. The release's independent appearance review is in `delivery/qa/acceptance.md`.

For an edited native master:

```sh
python3 models/chibi-mall-visitor-modular/build.py --export-only PATH/visitor.blend
python3 models/chibi-mall-visitor-modular/build.py --from-master PATH/visitor.blend
```

These export/validate/build the preview in a new directory. They preserve native mesh/guide edits, weights, textures and Actions; the procedural route reconstructs the authoring inputs in `authoring/`. Small guide deformations retain the baked texture; a substantially changed sculpt requires rebaking.

`authoring/config.py` owns dimensions, swatches, atlas regions, bones, sockets and clip/preset contracts. Geometry modules own their shapes. `hair_bake.py` owns selected-to-active tangent baking. `preview/` owns the standalone viewer. `qa/` owns binary, native and runtime checks. No external service or generated image substitutes for the GLB captures.

## Runtime contract

- glTF uses +Y up, +Z forward and a sole-midpoint origin. Blender uses metres, +Z up and −Y forward.
- One 20-joint humanoid skeleton binds seventeen runtime meshes. Every `extras.partSlot === 'Backpack'` mesh toggles together, including straps. `Watch` toggles independently.
- Scene `extras.expressionPresets` contains `default`, `happy`, `wink`, `surprised`, `thinking`, `excited`. Resolve participating mesh morph targets by name. Static Thinking also uses `extras.thinkingPose` for hand-to-chin contact.
- Loops: `idle`, `walk`, `run`, `talk`, `browse`. One-shots: `sit`, `wave`, `pick_up`, `inspect`, `point`, `nod`, `cheer`. Sit holds its final pose. `extras.clipInfo` records 30-fps timing, loop policy, gait speeds and interaction markers.
- Locomotion is in place; the application supplies displacement. Attach a product at `Socket_Palm_R` on pickup frame 36. `Socket_Palm_L`, `Socket_Back`, `Socket_Wrist_L` are additional sockets. The review seat/product are QA fixtures.

## Refinement inputs

`authoring/hair-sculpt.npz` stores the refined rooted scalp and the separate swept sections in rest space. Each closed section has a measured upper surface, a rolled underside, two poles, pigment and shading normals. `swept_locks.py` samples them at sculpt and runtime resolution. `hair_temple_fit.py` fits the temple to the registered quarter view. The base color and normal atlases are baked in the same UV chart as the game mesh. `hair-measurements.npz` and `hair-lock-mattes.npz` retain the original reference measurements.

In Blender, select `Swept_hair`, enter Edit Mode and use a `Lock | …` vertex group to select one complete lock. Each inner and outer guide has handles bound to that lock. Exact released-file hashes, the registered four-angle comparison and the independent tip review are recorded under `delivery/qa/`.

The intermediate native files are `checkpoints/01-blockout.blend`, `checkpoints/02-head.blend` and `checkpoints/03-wardrobe.blend`. The rigged and animated checkpoint is the editable `visitor.blend` master.

## Acceptance evidence

A full build captures the eight-angle turntable, six facial expressions, four accessory combinations, the actual default UI, shoe and face details, motion timelines, contact poses and all twelve playback runs. `qa/captures.json` records the export, preview, reference and image hashes. `qa/face-closure.json` tests visibility of the teeth and tongue at the neutral smile and open expressions.

The pickup uses an open insertion pose and a closed right-hand grasp. In `qa/pickup-grasp.png`, the QA product starts at the target, meets the thumb, index and lower fingers at frame 36, and then follows the palm socket. `qa/runtime.json` measures each contact in metres and checks the posed hand triangles against the product every half frame. A client supplies its own product.

`qa/geometry.json`, `qa/runtime.json`, `qa/native.json` and `qa/build.json` record the technical checks, including source topology, saved-master re-export and procedural regeneration. The visual verdict is bound separately to exact reviewed bytes. The orthographic comparison uses the 451 px standing height from the sheet. The three-quarter camera is estimated.


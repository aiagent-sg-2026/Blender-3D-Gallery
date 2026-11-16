# GJH Chibi Mall Visitor — modular Blender build plan

**For design review.** Build the 18-year-old male shopper in the supplied character sheet as an editable Blender character and a single, self-contained glTF 2.0 binary. The proposed default is 1.30 m tall, fully dressed at about 7,000 triangles, with one humanoid rig. The first review deliverable is a neutral full-body blockout and a detailed head turntable. Confirm the likeness while the face and hair are still cheap to change.

## 1. What to take from the sheet

| Read from the artwork | How it guides the build |
| --- | --- |
| Large rounded head, full cheeks, shallow chin, small nose, large dark brown eyes, heavy upper lids and brows | Establish these features in neutral light. The main front view supplies spacing and a small closed smile. The open-mouth three-quarter view supplies cheek volume and smile shape. |
| Off-centre part, dark warm hair, heavy swept fringe, exposed ears and overlapping locks down the back | Trace the part and the largest locks by hand. Preserve the forehead opening and the direction of the rear sweep. Check the silhouette above and behind each ear. |
| Plain white crew-neck tee, medium-blue straight jeans with turned-up cuffs and rear pockets, low white lace-up sneakers | Give the sleeves, hem, cuffs, soles and toes real thickness. Paint the pocket stitching, fly and lace details where they do not change the outline. |
| Compact dark backpack with two shoulder straps, top handle and front zip pocket. Dark rounded-square watch | The front view shows both straps and the watch on the character's **left** wrist. Use the side view for backpack depth and the back view for width and pocket placement. |
| Six example expressions, eight-angle strip and twelve recommended actions | Use the faces as visual targets. Render the finished model at eight real 45° intervals. Stage animation work after likeness and deformation reviews. |

**Proportion guides.** On the 1536 × 1024 sheet, the large front figure runs approximately from image row 54 at the hair crown to row 505 at the soles. Setting that span to 1.30 m gives these initial guides. They are estimates from a rendered drawing. Use the large side view to refine depth and the three-quarter views to check volume. Align by sole and crown before overlaying the relaxed reference pose.

| Front landmark | Approximate row, top down | Height above sole |
| --- | ---: | ---: |
| Hair crown | 54 | 1.30 m |
| Eye centres | 173 | 0.96 m |
| Chin | 228 | 0.80 m |
| Tee hem | 349 | 0.45 m |
| Top of denim turn-up | 459 | 0.13 m |
| Sole | 505 | 0.00 m |

The annotated 2.5-head proportion gives a nominal 0.52 m head. The main drawing gives about 0.50 m from hair crown to chin. Start with the drawing's silhouette and leave that small difference visible in the review. It matters more to preserve the low eye line and cheek outline than to hit an exact ratio.

## 2. Modular parts and triangle allocation

Targets below count both sides, all visible layers and the default accessories in the triangulated export. All modules share the same world scale, rest pose and skeleton definition. Blender collections keep every part editable. The default GLB contains only the selected assembly.

| Module | Construction and attachment | Tris |
| --- | --- | ---: |
| Head, neck transition, ears | Loft a symmetric quad cage from jaw, cheek, brow and crown sections. Shape the skull and ear rims in profile. Keep loops around the mouth and eye openings. The head follows the head bone with a short blended neck transition. | 1,200 |
| Eyes, lids, brows, mouth interior | Shallow curved eye surfaces fitted to the face, shaped lids, a separate brow pair and a small mouth cavity with a tooth strip and tongue. Paint iris, pupil and catchlight. Give each lid enough travel for a clean wink. | 750 |
| Hair | Fit a low-poly scalp shell, then sweep variable-width cross-sections along individually drawn guide curves. Start with 3–4 fringe masses and 5–7 side, crown and nape masses. Overlap the roots, round the crests and taper the ends. Bind to the head. | 1,450 |
| Exposed body, arms and hands | Use short tapered limbs, joint loops and a continuous palm. Separate thumb and index silhouettes. Group the other fingers so point, grip and hand-to-chin poses read at this scale. | 750 |
| T-shirt | Fit a separate shell to chest, shoulders and upper arms. Model collar, sleeves and hem with a small stand-off. Weight it to the same joints as the underlying body. | 550 |
| Jeans | Join the leg tubes through a deformable crotch. Model the loose straight leg, ankle break and cuff returns. Place seams, fly and pockets in UV space. Share hip and knee weights across the join. | 900 |
| Sneakers, pair | Use stepped cross-sections for heel, low upper, toe box and outsole. Model tongue and sole lip. Put lace crossings and panel seams in the atlas. Bind each shoe to its own foot. | 700 |
| Backpack and straps | Bevel the main body and front pocket. Shape the handle and two shoulder ribbons around the dressed torso. Pack follows the upper chest. Blend the straps near the shoulders. Toggle pack, handle, pocket and straps together. | 550 |
| Watch | Fit a rounded case and face to a wrist band. Attach to a left forearm socket, clear of the hand joint. Toggle as one part. | 150 |
| **Dressed target** | **Includes both shoes, both eyes, bag, straps and watch.** | **7,000** |

Keep 1,000 triangles in reserve under the sheet's 8,000 ceiling. Spend them first on eyelid closure, the cheek profile or a visible gap between hair masses. Simplify hidden hair intersections and accessory bevels first if the build runs over. The sheet's 3,000–8,000 range applies to this dressed character. A separate crowd LOD would need its own visual and performance target.

**Modularity check.** Show four assemblies on the same rig: fully dressed, bag removed, watch removed, both removed. The back of the tee must be complete, the bare wrist closed, and both shoulder straps must disappear with the pack. Keep covered-body face masks associated with the fitted garment so future clothing swaps can restore the correct skin. The pack and watch require no body mask. An alternate haircut or second outfit can later use the same attachment and weighting contracts.

## 3. How Python and Blender divide the work

| Proposed source | Responsibility |
| --- | --- |
| `config.py` | Single definition of landmarks in metres, anatomical sides, named slots, palette, budgets, active parts and stable bone/socket names. |
| `body.py`, `head.py`, `hair.py` | Generate the body cage, facial topology and swept hair sections from landmarks and guide curves. Mirror paired anatomy before asymmetric styling. Keep the guides editable. |
| `wardrobe.py`, `accessories.py` | Build tee, denim, shoes, pack and watch against fitted body surfaces. Each builder returns its named objects, material assignments and intended binding. |
| `materials.py` | Assign shared UV layouts, atlas regions and PBR materials. Keep seams and pocket details with the garment that owns them. |
| `rig.py`, `expressions.py`, `actions.py` | Build one armature and rest pose, bind all modules, create facial and hand shapes, and author named Blender Actions. |
| `build.py`, `export.py`, `qa/` | Assemble active parts in a fresh scene, export the approved assembly and generate repeatable geometry, turntable, pose and runtime checks. |

Use Blender Python (`bpy` and mesh data or `bmesh`) for section lofts, mirrored limbs, sweeps, naming, material assignment, rig creation, rendering and export. In Blender, an artist tunes the face cage, eyelid arcs, hair guides, shoulder fit, skin weights and key poses under the review cameras. Lock topology before UV finalization and shape keys.

**Preserve hand edits.** The blockout generator writes to a build directory. Approved guides and topology, painted maps, corrective weights, shapes and edited Actions become versioned authoring inputs in `sources/`. The assembly step reads those named collections or datablocks. An export-only command opens the approved master directly. A fresh assembly from the saved inputs must reproduce landmarks, named parts, triangle counts, expressions and clip list. Record the Blender version, inputs, settings and tested GLB hash. This makes the build repeatable without asking an artist to repeat a sculpt.

**Proposed entry points**, run from the future asset folder. The first command produces review geometry in isolation. The second delivers the artist-approved source. Both scripts are future implementation work.

```sh
blender --background --factory-startup --python-exit-code 1 --python build.py -- --stage blockout --out build/blockout
blender --background sources/visitor-master.blend --python-exit-code 1 --python export.py -- --out build/visitor.glb
```

For example, build the bag against the shirt in rest space. Return the shell and straps under one logical `Backpack` slot, with separate bindings for the rigid shell and flexible straps. Store that slot ID on both exported nodes. A viewer can hide both by slot, while the artist can still change strap curvature independently. Use the same mechanism for the watch. Merge detail only within a slot when binding, material and facial controls are compatible.

Existing repo code provides starting points for the fringe sweep, a face patch on a curved surface, and GLB playback tests. The earlier chibi visitor used a different outfit. Its QA also records rear locks reading as plates and gaps at the ears. Reuse the construction ideas and tests, then fit the geometry to this sheet. [Fringe construction](../models/chibi-mall-visitor/hair_sculpt.py) · [Chibi visitor QA](../models/chibi-visitor-v4/qa/run-002/issues.json) · [Existing visitor playback](../src/visitor-v3/demo.js)

## 4. Colour, surface and texture

Median RGB samples from the printed colour swatches give these sRGB starting points. Convert palette inputs into Blender's linear working space when assigning numeric shader values. Judge the result next to the sheet under soft neutral illumination.

| Skin | Hair | Tee | Jeans | Shoes | Backpack | Watch |
| --- | --- | --- | --- | --- | --- | --- |
| `#FACFAA` | `#3A2F2B` | `#FEFEFE` | `#5D73B1` | `#EDE8E9` | `#3D3A42` | `#323038` |

Start with one 1024² base-colour atlas, with extra space for the face, iris edges and denim seams. Use UV padding and check mipmapped edges at gallery size. Separate materials where the light response changes visibly: soft skin and cloth, satin hair, glossy eyes/watch face and rubber soles. A packed roughness map can share the atlas UVs if it saves material splits. Keep broad highlights on the curved hair masses, stronger highlights on eyes, matte cotton, subtle denim variation and a slightly warmer off-white sole. Inspect the hair, pack and watch under side lighting so all three dark surfaces remain distinguishable.

## 5. Rig, expressions and movement

**Coordinates.** Author in metres, Z up, character facing Blender −Y, sole midpoint at the origin. Export glTF +Y up and front +Z. Left and right always mean the character's own sides. Bind in a shallow A-pose with enough clearance to weight the armpits. Save a separate relaxed display pose matching the reference. Use in-place locomotion so the mall controls world movement.

**Skeleton.** A 20-bone starting layout is root, pelvis, spine, chest, neck and head, plus left/right clavicle, upper arm, forearm, hand, thigh, shin and foot. Add non-deforming attachment nodes for the back, left wrist and palms where required. Bind skin, tee and jeans smoothly, normalize weights and cap them at four influences per vertex. Give shoes, watch case, pack shell and hair rigid follow. Use hand morphs for grip and index extension. Check the rig with a seated bend, raised arm, full blink and a hand at the chin before producing the clip library.

| Expression from sheet | Proposed controls and review cue |
| --- | --- |
| Default | Neutral basis with soft brows, open eyes and a small closed smile. |
| Happy | Both lids curve shut, cheeks lift and the mouth opens into a smile. |
| Wink | Close one eye independently. Keep the other iris visible and the smile small. |
| Surprised | Raise brows, open the eyes wider and form a small round mouth. |
| Thinking | Angle brows gently and offset the mouth. Add a separate hand-to-chin pose so the expression also works in a portrait. |
| Excited | Higher cheek lift, tightly smiling eyes and a wider open mouth. Keep it recognizably different from Happy at thumbnail size. |

Author a small set of blendable shape keys on fixed topology, including independent left/right blink, cheek lift, brow raise/tilt, smile, mouth open and mouth round. Store the six named weight presets in one source table, copy it to the exported scene's glTF `extras`, and render the pose sheet from those values. The viewer reads this table and applies weights to the matching morph names on each participating mesh. Check intermediate weights, teeth at full opening and the closed-eye outline from three-quarter view.

**Animation scope proposed for review.** The sheet labels these actions as recommendations. Each row can be reviewed and delivered on its own.

| Batch | Clips | What to inspect |
| --- | --- | --- |
| Rig proof | `idle`, `walk`, `wave` | Breathing and blink, planted walk contacts and loop seam, sleeve/strap clearance during arm lift. |
| Locomotion and conversation | `run`, `sit`, `talk`, `nod` | Faster contact timing, hip and knee bends against a known seat height, jaw motion, chin clearance. |
| Shopping and gestures | `browse`, `pick_up`, `inspect`, `point`, `cheer` | Readable gaze, palm contact at a marked frame, grip and index silhouette, both arms clear of hair and bag. |

Bake Blender controls and constraints into portable bone or morph animation on export. Define each clip's loop or one-shot policy and contact frames. Seat position, item attachment and world navigation belong to the mall application. Use a simple test seat and item to judge the poses locally. The interchange format supports skinned meshes and named animations targeting transforms and morph weights. [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)

## 6. Production order and review evidence

| Stage | Deliverable for review | Acceptance before continuing |
| --- | --- | --- |
| 1. Reference and blockout | Landmark sheet, grey relaxed body with head, hair mass, rough garments and pack. Front, side, back and three-quarter orthographic renders. | Feet and hair crown register to the source. In a 451 px tall front overlay, propose ±9 px for the eye line, chin and tee hem. Use side and back views to judge skull depth, pack projection and shoulder fit. |
| 2. Head likeness | Neutral head plus hair, large front, side, back and three-quarter crops. Include a hair-off view of the face. | The same character reads with the hair on and off. Eye spacing, cheek taper, forehead opening, ear clearance and rear locks survive the turn. Owner reviews these images before detailed wardrobe work. |
| 3. Complete static character | Dressed colour turntable at 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°. Detail strip for watch, shoe, pocket, pack and eyes. Four accessory combinations. | Front/back garments read correctly, cuffs sit over shoes, straps belong to the bag, and removing accessories exposes finished surfaces. Check exported triangles at this stage. |
| 4. Deformation and face | Six expression portraits at the same camera and lighting, a seated pose, a hand-to-chin pose, a wave and a walk loop. | Both eyes close cleanly, Happy and Excited read differently, clothing follows joints, shoes plant, the pack stays against the back, and the watch stays on the left wrist. |
| 5. Motion and GLB handoff | Approved action batches, editable master, production GLB and runtime evidence. | Confirm the exact exported asset meets the technical checks below. Record clip coverage and any visual issues against the reference. |

**Export acceptance**

- Select character meshes, armature and required attachment nodes. Exclude cameras, lights, floor, source guides, reference planes and inactive variants. Verify embedded images and buffers, front direction and ground placement by reopening the GLB in a clean scene.
- Count evaluated triangles for the full dressed assembly, including mirrored parts and accessories. Require 3,000–8,000, targeting 7,000. Measure rest height at 1.30 m ±0.01 m and sole height within 2 mm of ground. Record bytes, materials, primitives, draw calls and texture sizes.
- Run Khronos glTF Validator, aiming for zero errors and zero warnings. Load the same file in a Three.js test viewer. Check four accessory states, every approved clip, all six face presets and combinations such as a wink during a wave. Compare the exported turntable with the Blender source.
- Sample heel and toe contact during walk and run, plus loop joins. Play the seated and pickup motions against the test seat and item. Inspect skinning and intersections through the motion as well as in still frames.
- Handoff includes the editable master, authored inputs, generator and export entry points, GLB, preset definitions, turntable, expression sheet, action/contact list, measured QA report and instructions to reproduce the reviewed result. Record the supplied sheet as design provenance. Gallery registration and publication are separate decisions. [Repository asset handoff contract](blender/asset-contract.md) · [Character animation checks](blender/characters-animation.md)

## Review decision

The first decision is whether the neutral face, swept fringe and rear hair volume capture this visitor. The proposed first build covers stages 1–2 and produces those comparisons. The second decision, after seeing the rig proof, is whether the mall needs all twelve suggested actions or a smaller first delivery. Neither decision requires changing the proportions, default outfit or shared rig.

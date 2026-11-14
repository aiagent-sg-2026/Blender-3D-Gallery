# GJH Mall Visitor v2: design and delivery plan

Status: development preview. The gallery has a skinned v2 asset, customization controls and prototype clips; the deployed mall uses v2 by default and retains an explicit v1 fallback, with two floors connected by a lift. Physical product pickup/return, contact-calibrated cart/seating and geometry LOD are implemented and verified locally; production checks are recorded in the consuming repository, while physical-device acceptance remains outstanding. The supplied showcase is a visual concept and its numerical specifications are targets, not verified measurements.

## Goal and visual direction

Create a new male mall visitor in the same friendly, rounded style, with more natural body proportions, hair, facial features, clothing and footwear. Use the reference's green polo, white collar, jeans, white-and-green shoes, glasses, backpack and watch as the default design direction. Keep the original visitor and its existing URLs and model files intact. Review the design from front, side and back before committing to the final geometry.

The intended performance scenario is one player character plus a small number of visitors. Use one player plus four additional visible characters as an initial test scenario, not a guaranteed crowd limit; record actual device, viewport, scene, effects and character counts with every performance result.

The reference also illustrates business-casual, shopping and event-staff outfits. Treat those as possible variants, not pre-existing assets; establish an explicit, testable initial variant set during design. Avoid claiming any endorsement or public redistribution license from the reference's branding.

The concept gives useful facial, clothing and accessory cues, but it is a rendered collage rather than an asset specification: the turnaround poses have arms lowered, not an actual T-pose or neutral A-pose; the backpack is prominent in the hero image but its construction and placement are not consistently clear in the turnaround. Perspective, proportions and details vary across panels. Resolve these ambiguities in a true orthographic model review. The listed mesh counts, material maps, rig, animations and frame rate cannot be verified from the image alone.

## Current baseline

- `models/gjh-mall-visitor` contains an editable Blender source and a texture-free GLB with rigid articulated nodes, not a skinned humanoid armature. Its documented rest height is 1.72 m, glTF +Y up, floor Y=0, front +Z; `idle`, `walk`, and `sprint` stay in place. The recorded GLB has 10,356 triangles, 25 primitives and 369,976 bytes. These are historical asset receipts, not a new benchmark.
- The gallery shows the current visitor at rest. The mall consumes the animation clips separately.
- In Webpage-Design-Gallery v11 at commit `42c49e3067cfcca367e01b838d72a5b5d5e82bf1`, `assets/character.js` loads the pinned visitor and requires `idle`, `walk`, `sprint`. Its separate cart, seated and collection modules apply procedural poses to specifically named nodes. The seated pose has no authored sit clip; collection is a simplified gesture, not an IK shelf-pickup simulation. The cart pose is also simplified and explicitly reports no IK or wheel physics. A new skeleton cannot be assumed to be a drop-in replacement.
- Blender 5.1.2 is available locally; the current visitor's recorded source was generated with Blender 5.2.3. A read-only open in 5.1.2 warned that the newer file could lose data; do not save it in that version without a safe compatibility procedure. Check export compatibility and record the actual authoring version.
- The gallery viewer currently creates a plain `GLTFLoader` without a KTX2 loader or meshopt decoder, and the v1 asset validator rejects required extensions and images. Compressed v2 textures therefore require explicit viewer and validator work or a compatible uncompressed fallback; packaging alone is insufficient.

## Proposed boundaries

1. **Asset authoring:** editable `.blend`, modular geometry, humanoid armature, skin weights, animation clips, textures, export and provenance belong to Blender-3D-Gallery.
2. **Mall runtime:** locomotion and collisions, interaction targeting, prop ownership, attachment and release, seat/elevator state, controls and animation orchestration belong to the consuming mall. Do not claim that an animation clip alone implements an interaction.
3. **Compatibility:** add a separate v2 asset and adapter; retain the v1 fallback until the v2 consumer has passed its own tests. Preserve metre scale, floor and facing conventions; preserve `idle`, `walk`, `sprint` as compatibility clip names or map them explicitly in the adapter.

## Work plan

1. **Design and contracts.** Establish turnaround and reference proportions, visual details, supported outfits, body/hair/skin/accessory slots, naming, joint hierarchy, coordinate system and clip map. Define shared attachment points for both hands, backpack and cart handle. Identify mall interaction targets and their ownership before authoring contact poses.
2. **Model and rig.** Build independently editable hair, glasses, clothing, fingers, shoes and backpack; provide a real skinned humanoid skeleton with weighted deformation. Author a neutral A-pose, natural facial features and consistent scale. Keep components modular in the source; optimize runtime draw calls without losing source editability.
3. **Core movement.** Produce looping in-place `idle`, `walk` and `sprint` with clean cross-fades, grounded feet and stable root orientation. Check loop boundaries, foot sliding, self-intersection and backpack/clothing deformation in the exported GLB, not just Blender.
4. **Interaction motion and integration.** Add sit/stand, reach/grasp/release and cart-push poses/clips; define hand and prop anchors. Connect them to the mall's state machine and collision controller. Define cancellation, interrupted transitions, reduced motion and recovery. Design elevator interaction against an actual elevator implementation; verify shelf-to-hand and hand-to-shelf object state rather than simulating an action with a gesture alone.
5. **Customization.** Implement compatible swappable hair, outfits and accessories against the shared skeleton, plus skin-tone materials. Test combinations, clipping and resource disposal. Preserve selection state in an explicitly defined owner; do not assume the current mall already stores customization.
6. **Performance and packaging.** Measure a high-detail model and create reduced LODs only where measured benefit justifies them. Reuse meshes, materials and compatible animation data across instances while keeping each skeleton independent. Evaluate texture atlases and KTX2/Basis with compatible loaders and a tested fallback; retain editable source textures. The reference's ~18,420 triangles, 2K textures and 60 FPS are provisional design targets, not acceptance evidence.
7. **Gallery and mall validation.** Register a distinct catalog entry, thumbnail, metadata and rights; verify build-time validation, viewer fallback and current navigation. In the mall, validate actual GLB bytes, motion transitions, each supported interaction, customization, collision/contact, touch and desktop input, and rollback to v1. Record draw calls, GPU memory, loading time and frame-time distributions on representative real iPhone, Android and desktop devices with stated scene and crowd sizes.

## Acceptance

- New source and export are distinct from v1, reproducible, self-contained or explicitly documented, and pass the glTF validator; all required clips and a real skin/skeleton are present and playable.
- Turnaround and motion renders show the agreed appearance, separate components and acceptable deformations. Verify animated contact and loop continuity from the exported model.
- Customization works across supported combinations without broken skinning, obvious clipping or leaked resources.
- Each advertised interaction completes, cancels and recovers correctly in the real mall, with correct object ownership and collision behavior. A clip or mock is not proof of the complete flow.
- Record performance against an agreed device/scene matrix and budget; do not claim 60 FPS or VRM compatibility until verified. VRM requires its own compatible metadata and validation beyond a humanoid glTF skeleton.
- Gallery and mall regression results, provenance, texture rights, remaining device limitations and actual sizes are documented before release.

## Sources

- Existing visitor: `models/gjh-mall-visitor/README.md`, `verification.md`, `generate.py`, `validate.mjs` and `reports/assets.json`.
- Mall integration at the pinned revision: [character controller](https://github.com/yapweijun1996/Webpage-Design-Gallery/blob/42c49e3067cfcca367e01b838d72a5b5d5e82bf1/demos/corporate/gjh/v11/assets/character.js), [seated pose](https://github.com/yapweijun1996/Webpage-Design-Gallery/blob/42c49e3067cfcca367e01b838d72a5b5d5e82bf1/demos/corporate/gjh/v11/assets/seated-pose.js), and [collection gesture](https://github.com/yapweijun1996/Webpage-Design-Gallery/blob/42c49e3067cfcca367e01b838d72a5b5d5e82bf1/demos/corporate/gjh/v11/assets/collection-gesture.js).
- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) and [Three.js GLTFLoader documentation](https://threejs.org/docs/pages/GLTFLoader.html).

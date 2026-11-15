# Characters, rigs and portable animation

<!-- KB-SUMMARY-START -->
Separate character mesh, clothing, armature, skin weights and animation clips. Document rest pose, hierarchy, units, facing and root-motion ownership. Weighted vertex groups must match intended deform bones and meet the consumer's influence/normalization rules. Inspect joint bends, clothing intersections and extremes after export; a valid skin is not proof of good deformation. Blender 5.1 Actions use slots; avoid assuming legacy direct F-Curve access works unchanged. Keyframe insertion is a useful version-aware entry point, followed by inspection of the created Action/slot. glTF transports supported transforms, skinning and morph animation; runtime input, collision and business states remain application responsibilities. Bake constraints where the selected export path requires it. Read actual sampler times instead of assuming every clip starts at zero. The calibration verifies one translated object clip, not a humanoid rig.
<!-- KB-SUMMARY-END -->

## Authoring contract

Choose a rest pose and stable bone/clip names before adding motion. State whether the application moves an in-place walking character or consumes clip displacement; applying both can double movement. This is a design choice, not a glTF requirement.

The [Armature modifier](https://docs.blender.org/manual/en/5.1/modeling/modifiers/deform/armature.html) uses matching bone and vertex-group names when that binding method is selected. Inspect weights and motion rather than relying on automatic binding alone. Define an influence cap supported by the target viewer; do not turn one viewer's convention into a universal format limit.

## Actions and time

The [5.1 Actions manual](https://docs.blender.org/manual/en/5.1/animation/actions.html) documents slots. Scripts should inspect installed APIs and explicitly associate the intended animation data. Avoid copying old `action.fcurves` recipes without checking the current Action representation.

The [glTF animation manual](https://docs.blender.org/manual/nl/5.1/addons/import_export/scene_gltf2.html) explains supported channels and export modes. Record the selected mode, action range, FPS, sampling and clip names. In the local fixture, frames 1–11 at 10 FPS export samples from approximately 0.1 to 1.1 seconds. Sampling at 0.5 seconds is not the midpoint of those keys.

## Acceptance

Check rest pose, idle, transition boundaries and representative joint extremes in Blender and the target loader. Verify clip names/durations and observable motion. Test root motion, looping, controller states and collision separately. Facial shapes and material animation need their own export/consumer checks; a walking clip does not prove them.

No new skinning, IK, facial or humanoid-deformation experiment is claimed by this research. The native calibration covers Action creation and object-translation playback only.

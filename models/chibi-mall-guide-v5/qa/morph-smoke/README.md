# Morph-target smoke test (2026-11-15)

Question: do a Blender shape key, a rigid-bound skinned mesh and an animation survive glTF export and load in the repository's Three.js (0.187.0) `GLTFLoader` + `AnimationMixer`?

```sh
blender --background --factory-startup --python models/chibi-mall-guide-v5/qa/morph-smoke/make.py -- /tmp/morph-test.glb
node models/chibi-mall-guide-v5/qa/morph-smoke/check.mjs /tmp/morph-test.glb
```

Result with Blender 5.1.2 (see `docs/chibi-character-standard.md` section 12): validator 0 errors / 0 warnings; shape keys `smile`, `surprised`, `blink` become named morph targets; the key animation becomes a `morphTargetInfluences` track and the mixer drives it. A first export with the skinned mesh parented under the armature produced the validator warning NODE_SKINNED_MESH_NON_ROOT; leaving the mesh unparented removed it.

Limits: Node only, no rendering and no browser; the gallery's own `src/viewer.js` was not run; the viewer shows models at rest, so nothing in it plays morph animation today.

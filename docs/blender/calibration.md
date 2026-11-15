# Blender 5.1.2 calibration: observed behavior

This is a generic experiment, not a production asset or a certification of all Blender versions. Its source and output assertions are in [knowledge-probe.py](verification/knowledge-probe.py) and [check-probe.mjs](verification/check-probe.mjs). The [result receipt](verification/probe-results.json) records versions, hashes and measured values.

## Experiment boundaries

Run a separate factory-startup background process with automatic script execution disabled. Only temporary fixture files are created; the connected interactive scene, installed extension preferences and project models are not modified. An independent Node loader and Khronos validator inspect the emitted GLBs.

## Observations

- Background `view3d.view_selected.poll()` is false, while adding a mesh primitive can poll true. A valid object/selection is not a replacement for a real viewport context.
- `Object.copy()` shares the original mesh. An edit through the shared copy changes the original; assigning a separate `Mesh.copy()` isolates subsequent edits.
- A smooth cube with eight authoring vertices and six faces exports 14 vertices with the fixture's UV seams and eight after those UVs are removed. Both exports have 12 triangles. This is an example, not a fixed expansion multiplier.
- Blender centre `(4,-5,6)` and dimensions `(1,2,3)` export with +Y up to glTF centre `(4,6,5)` and dimensions `(1,3,2)`.
- Changing only `scene.unit_settings.scale_length` to 0.01 leaves the exported geometry size unchanged in this 5.1.2 fixture. Author to an explicit metre contract and measure output; do not infer conversion from display settings alone.
- Unconnected Principled roughness 0.42 and metallic 0.15 survive as glTF material factors, within floating-point tolerance. Texture/image appearance is not part of this experiment.
- Keyframes at frames 1 and 11 with 10 FPS export one object-translation clip with an Action slot. The sampled time range is approximately 0.1–1.1 seconds, and sampling its midpoint gives X≈4.5.
- A deliberately raised command-line Python exception returns the requested process exit code 23.

## Corrected harness assumption

The first harness assumed that 0.5 seconds was the midpoint of this clip. The actual exported samples start at 0.1 seconds; the observed X at 0.5 is about 4.352. The [diagnostic failed attempt](verification/animation-time-assumption.json) is retained with its original FAIL status.

The corrected check reads the actual first/last sample timestamps and samples their midpoint uniformly. It still requires X≈4.5. This changes the timing instrument, not the source animation or the expected midpoint position. Do not reinterpret the earlier failure as a Blender exporter defect or a successful original test.

## Reproduce and limitations

```sh
node docs/blender/verification/check-probe.mjs
```

Set `BLENDER_BIN` to select another executable. Reassess version-specific expectations when changing it. The fixture tests structural/numeric behavior and one translated object, not textured browser appearance, humanoid skinning, add-on registration, physics, real phones, frame rate or all export settings. Temporary exports are removed after inspection; their hashes and observations remain in the receipt.

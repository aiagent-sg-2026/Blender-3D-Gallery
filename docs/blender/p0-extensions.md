# P0 extensions: installation and Python verification

Verified 2026-11-15 on macOS, Blender 5.1.2 / Python 3.13.9. This follow-up advances the two P0 candidates beyond the [initial listing-only catalog](extensions.md). Other candidates retain their earlier status.

Both exact official packages are installed in the existing local `user_default` repository and enabled. Preferences were saved. A fresh background process loaded those preferences and found both enabled/loaded without calling an enable/register function. Existing enabled add-ons, including Blender MCP, were retained. See [installation](verification/p0-extensions/installation.json) and [persistence](verification/p0-extensions/persistence.json).

| Extension | Version | Actual Python module | Verified Python workflow |
| --- | --- | --- | --- |
| [Texel Density Checker](https://extensions.blender.org/add-ons/texel-density-checker/) | 2026.1.1 | `bl_ext.user_default.texel_density_checker` | Calculate in background/UI; set using a real editor |
| [3D Print Toolbox](https://extensions.blender.org/add-ons/print3d-toolbox/versions/) | 1.5.0 | `bl_ext.user_default.print3d_toolbox` | Analyze, solid/degenerate checks, volume, area and structured report in background/UI |

[Package provenance](verification/p0-extensions/packages.json) records official archive URLs, SHA-256 and all 33 packaged file hashes. Installed files match; vendor code was not patched. Review covered manifests, registration, local I/O and exercised operator paths, not every feature or a complete security audit. Texel Density writes JSON preferences; Print Toolbox generates a translation cache. Bundled geometry-node assets and export/edit tools were not exercised.

## Texel Density calls and context

For a known selected target, establish mode, meaningful UVs, units and texture resolution explicitly:

```python
import bpy

obj = bpy.context.active_object
assert obj and obj.type == 'MESH' and obj.mode == 'OBJECT'
assert obj.data.uv_layers.active and len(obj.data.polygons)
td = bpy.context.scene.td
td.units = '1'                 # px/m
td.texture_size = '1024'
td.selected_faces = False
assert bpy.ops.object.texel_density_check() == {'FINISHED'}
print(float(td.density))
```

The unmodified setter accesses `context.area.spaces`, changes editor type and runs UV transforms. Pure background execution has no area and raises AttributeError. The test records this as `EXPECTED_CONTEXT_FAILURE`, not background setter support. The MCP callback initially has no area either; use an actual window, `VIEW_3D` area and `WINDOW` region:

```python
window, area = next((w, a) for w in bpy.context.window_manager.windows
                    for a in w.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')
with bpy.context.temp_override(window=window, area=area, region=region):
    td = bpy.context.scene.td
    td.units, td.texture_size = '1', '1024'
    td.selected_faces, td.set_method = False, 'AVERAGE'
    td.rescale_anchor, td.density_set = 'UV_CENTER', '512'
    assert bpy.ops.object.texel_density_set() == {'FINISHED'}
    assert bpy.ops.object.texel_density_check() == {'FINISHED'}
    print(td.density)
```

This changes UVs on selected meshes in that window's scene. Verification used a disposable scene. An operator's `FINISHED` status is insufficient; inspect the numeric result. With no active object the calculator returned `CANCELLED`.

Independent expectations for a 1 m² square with a full 1 UV² patch:

| Controlled input | Observed px/m |
| --- | --- |
| 1024² texture, object/scene scale 1 | 1024 |
| Object scale 2 along both surface axes | 512 |
| 1024 × 2048 texture, scale 1 | 1448.155 |
| Scene `scale_length=0.01`, original other inputs | 102400 |
| UI setter target 512, 1024² texture | 512; UV coordinates span 0.25–0.75 |

Texel Density includes scene unit scale in its calculation. The earlier GLB calibration found no exported resize from changing scene scale alone. Keep an explicit physical-dimension contract and measure exports; these are different operations.

## 3D Print Toolbox calls and scope

```python
assert bpy.context.active_object.type == 'MESH'
assert bpy.ops.mesh.print3d_check_all() == {'FINISHED'}
for row in bpy.context.scene.print3d_toolbox.get_report():
    print(row.name, row.value, list(row.indices) if row.indices is not None else None)
```

`mesh.print3d_check_all`, `mesh.print3d_check_solid` and `mesh.print3d_check_degenerate` inspect the active object, even with multiple objects selected. Iterate explicit targets for batch QA. In 1.5.0, `mesh.print3d_info_volume` and `mesh.print3d_info_area` instead aggregate selected objects; only single-cube totals were numerically exercised here.

The closed 1 m cube had zero non-manifold/degenerate elements, one shell, volume 1 m³ and area 6 m². An open-top cube had four non-manifold edges. With both selected, changing the active object switched that result between four and zero. A collinear triangle had one zero-area face. The closed cube also had one printing-overhang face: printing criteria are not automatic GLB failures. Choose topology rules by asset role.

## Evidence and reproduction

- [Background](verification/p0-extensions/background.json): isolated profile, registration, density calculations, geometric reports and the expected unsupported setter context.
- [UI](verification/p0-extensions/ui.json): actual Python/MCP calls, including successful 1024→512 px/m adjustment. Original geometry/selection/editor-type hashes, counts and dirty flag matched after cleanup.
- [Independent GLB](verification/p0-extensions/background.json): one scene, one mesh, 12 triangles, dimensions 1×1×1 m; zero Khronos errors/warnings/infos; actual bytes loaded by Three.js.
- [Retained export-scope failure](verification/p0-extensions/initial-export-scope.json): selection alone also encoded the default scene. Default-scene-only loader inspection missed it. The fixture now specifies `use_active_scene=True` and checks raw GLB scene/mesh counts.

With repository Node dependencies present, pass the reviewed official ZIP files in this order:

```sh
node docs/blender/verification/p0-extensions/check-background.mjs \
  /absolute/path/texel-2026.1.1.zip /absolute/path/print3d-1.5.0.zip
```

The runner enforces package hashes and removes its temporary profile. Set `BLENDER_BIN` for another executable; a new version needs reassessment. [probe.py](verification/p0-extensions/probe.py) owns the numeric fixtures. [check-ui.py](verification/p0-extensions/check-ui.py) exposes `run(output_path)` through Blender MCP with `__file__` set to its path; it removes the temporary scene and verifies preservation.

The preference backup remains outside the repository at the Blender 5.1 config path `backups/p0-extensions-2026-11-15/userpref.blend`. Disable extensions in Preferences to roll back enablement. Restoring the entire backup would also restore other preferences from that point in time.

These checks supplement the existing GLB acceptance pipeline. No production asset was rescaled, repaired or published. Asset-library QA, textured appearance, FPS, physical devices and untested extension features are outside the evidence. No commit or push is part of this installation task.

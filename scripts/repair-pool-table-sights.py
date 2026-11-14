"""Apply TABLE-001 only; preserve every other source object and export.

Run against scene.blend with --disable-autoexec, after preserving originals.
"""
import bpy
from pathlib import Path

folder = Path(bpy.data.filepath).parent
table = bpy.data.objects['ASSET_Table']
sights = [o for o in table.children_recursive if o.name.startswith('Rail sight')]
assert len(sights) == 12
for ob in sights:
    assert abs(ob.location.z - .856) < 1e-6, 'Unexpected source revision'
    ob.location.z = .8526
bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'scene.blend'))

def select_roots(roots):
    bpy.ops.object.select_all(action='DESELECT')
    for root in roots:
        root.select_set(True)
        for ob in root.children_recursive:
            ob.select_set(True)

select_roots([table])
bpy.ops.export_scene.gltf(filepath=str(folder / 'exports/table.glb'), export_format='GLB', use_selection=True, export_apply=True)
# The assembled scene embeds this same table, so it is a required dependent
# artifact. Sibling independent asset GLBs are deliberately not re-exported.
select_roots([o for o in bpy.context.scene.objects if o.name.startswith('ASSET_')])
bpy.ops.export_scene.gltf(filepath=str(folder / 'exports/billiards-scene.glb'), export_format='GLB', use_selection=True, export_apply=True)
print('TABLE_001_REPAIRED', len(sights))

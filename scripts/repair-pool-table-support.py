"""Repair TABLE-002 from the saved 25 mm slab, preserving its top and footprint.

Preserve the original source before running with --disable-autoexec and
--python-exit-code 1. Only table and dependent assembly GLBs are exported.
"""
import bpy
from pathlib import Path
from mathutils import Vector

folder = Path(bpy.data.filepath).parent
table = bpy.data.objects['ASSET_Table']
slate = bpy.data.objects['Table | slate and green cloth']
cabinet = bpy.data.objects['Table | solid walnut cabinet']
bpy.context.view_layer.update()
assert abs(slate.location.z - .766) < 1e-6, 'Unexpected source revision'
assert abs(slate.dimensions.z - .025) < 1e-6, 'Expected original 25 mm slab'
assert all(abs(v-1) < 1e-6 for v in slate.matrix_world.to_scale())
assert all(abs(v) < 1e-6 for v in slate.rotation_euler)
top = max((slate.matrix_world @ Vector(c)).z for c in slate.bound_box)
cabinet_top = max((cabinet.matrix_world @ Vector(c)).z for c in cabinet.bound_box)
bottom = cabinet_top - .0001
old_half = slate.dimensions.z / 2
new_half = (top-bottom) / 2
extension = new_half - old_half
assert 0 < extension < .002, 'Only the measured support gap may be closed'
flat_half = old_half - .002  # Preserve the generator's 2 mm edge bevels.
for vertex in slate.data.vertices:
    z = vertex.co.z
    if z >= flat_half:
        vertex.co.z = z + extension
    elif z <= -flat_half:
        vertex.co.z = z - extension
    else:
        vertex.co.z = z * (flat_half + extension) / flat_half
slate.location.z = (top+bottom) / 2
slate.data.update()
bpy.context.view_layer.update()
coords = [slate.matrix_world @ Vector(c) for c in slate.bound_box]
assert abs(max(c.z for c in coords)-top) < 1e-6
assert abs(min(c.z for c in coords)-bottom) < 1e-6
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'scene.blend'))

def export(name, roots):
    bpy.ops.object.select_all(action='DESELECT')
    for root in roots:
        root.select_set(True)
        for ob in root.children_recursive:
            ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(folder / 'exports' / name), export_format='GLB', use_selection=True, export_apply=True)

export('table.glb', [table])
export('billiards-scene.glb', [o for o in bpy.context.scene.objects if o.name.startswith('ASSET_')])
print('TABLE_002_REPAIRED', {'playing_top': top, 'slate_bottom': bottom, 'cabinet_top': cabinet_top})

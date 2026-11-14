"""Record and render the slate/cabinet interface without saving the source.

blender --background --disable-autoexec --python-exit-code 1 scene.blend \
    --python scripts/render-pool-table-contact.py -- /absolute/evidence/folder
"""
import bpy
import hashlib
import json
import sys
from pathlib import Path
from mathutils import Vector

out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
table = bpy.data.objects['ASSET_Table']
slate = bpy.data.objects['Table | slate and green cloth']
cabinet = bpy.data.objects['Table | solid walnut cabinet']
bpy.context.view_layer.update()
bed = [slate.matrix_world @ Vector(c) for c in slate.bound_box]
base = [cabinet.matrix_world @ Vector(c) for c in cabinet.bound_box]
report = {'source_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    'cabinet_top_m': max(v.z for v in base), 'slate_bottom_m': min(v.z for v in bed),
    'playing_top_m': max(v.z for v in bed)}
report['support_gap_m'] = report['slate_bottom_m'] - report['cabinet_top_m']
(out / 'contact.json').write_text(json.dumps(report, indent=2) + '\n')
meshes = [o for o in table.children_recursive if o.type == 'MESH']
for ob in scene.objects:
    if ob.type == 'MESH':
        ob.hide_render = ob not in meshes
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 800
scene.render.resolution_y = 650
scene.render.resolution_percentage = 100
camera = scene.camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = .08
camera.data.clip_start = .0001
camera.location = (-.5, -.95, .752)
target = Vector((-.5, -.59, .752))
camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath = str(out / 'slate-cabinet-contact.png')
bpy.ops.render.render(write_still=True)
print('TABLE_CONTACT', json.dumps(report))

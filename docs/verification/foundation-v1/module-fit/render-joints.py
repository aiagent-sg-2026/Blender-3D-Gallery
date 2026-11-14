"""Inspection-light closeups from the saved fitted assembly; never saves it."""
from pathlib import Path
import bpy
import hashlib
import json
import os
import tempfile
from mathutils import Vector

here = Path(__file__).resolve().parent
source = here / 'foundation-fitted.blend'
before = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
camera = scene.camera
camera.data.type = 'ORTHO'
scene.render.resolution_x = 1000
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.cycles.samples = 12
bpy.ops.object.light_add(type='AREA')
light = bpy.context.object
light.name = 'Temporary joint inspection light'
light.data.energy = 250
light.data.size = 2
views = [
    ('collar-junction.png', (-1.8, -12.6, 1.7), (-3, -13.8, 3), 1.8),
    ('fascia-junction.png', (-.3, -1.05, 1.5), (-2.4, -1.05, 2.5), 2.1),
]
for filename, position, target, scale in views:
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = scale
    light.location = Vector(position) + Vector((0, 0, .3))
    light.rotation_euler = (Vector(target) - light.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(here / filename)
    bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
data = {'status': 'PASS', 'sourceSha256': before, 'sourceUnchanged': True,
        'note': 'Inspection area light added only in memory; not production lighting.',
        'files': [{'path': filename, 'sha256': hashlib.sha256((here / filename).read_bytes()).hexdigest()}
                  for filename, *_ in views]}
target = here / 'reports/joint-renders.json'
assert not target.is_symlink()
fd, temporary = tempfile.mkstemp(prefix='.render-', dir=target.parent)
with os.fdopen(fd, 'w') as handle:
    json.dump(data, handle, indent=2)
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
os.replace(temporary, target)
print('PASS: two joint inspection renders; saved assembly unchanged')

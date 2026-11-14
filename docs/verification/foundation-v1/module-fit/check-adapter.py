"""Reopen the new standalone fascia source and verify unscaled sections."""
from pathlib import Path
import bpy
import hashlib
import json
import os
import tempfile
from mathutils import Vector

here = Path(__file__).resolve().parent
source = here / 'sources/fascia-run-348.blend'
before = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
root = bpy.data.objects['ASSET_foundation_fascia_run_348']
meshes = [o for o in root.children_recursive if o.type == 'MESH']
assert len(meshes) == 6
points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
dimensions = [max(v[i] for v in points) - min(v[i] for v in points) for i in range(3)]
assert all(abs(a - b) < .00001 for a, b in zip(dimensions, (3.48, .06, .6)))
for name in ('FRAME_Left', 'FRAME_Right'):
    assert abs(bpy.data.objects[name].dimensions.x - .03) < .00001
for name in ('FRAME_Bottom', 'FRAME_Top'):
    assert abs(bpy.data.objects[name].dimensions.z - .03) < .00001
assert all(all(abs(v - 1) < .00001 for v in o.scale) for o in [root, *meshes])
assert len([o for o in meshes if o.name == 'SIGN_ReplaceableFace']) == 1
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
data = {'status': 'PASS', 'sourceSha256': before, 'editableMeshes': len(meshes),
        'dimensionsBlenderMetres': dimensions, 'railSectionMetres': .03,
        'objectScales': 'unit', 'separateSignFace': True, 'sourceUnchanged': True}
target = here / 'reports/adapter-source.json'
assert not target.is_symlink()
fd, temporary = tempfile.mkstemp(prefix='.adapter-', dir=target.parent)
with os.fdopen(fd, 'w') as handle:
    json.dump(data, handle, indent=2)
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
os.replace(temporary, target)
print('PASS: standalone adapter source, six editable components, original 30 mm sections')

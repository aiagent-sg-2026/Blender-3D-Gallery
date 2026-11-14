"""Verify the saved editable source in a fresh Blender process."""
import bpy
import json
import os
from pathlib import Path
import tempfile

here = Path(__file__).resolve().parent
layout = json.loads((here / 'whitebox/layout.json').read_text())
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
assert len(meshes) == len(layout['parts']) == 43
for part in layout['parts']:
    obj = next(obj for obj in meshes if obj.get('layout_id') == part['id'])
    x, y, z = part['center']
    w, h, d = part['size']
    assert all(abs(a - b) < .00001 for a, b in zip(obj.location, (x, -z, y))), part['id']
    assert all(abs(a - b) < .00001 for a, b in zip(obj.dimensions, (w, d, h))), part['id']
    assert obj.mode == 'OBJECT' and obj.data.is_editmode is False
assert bpy.context.scene.unit_settings.scale_length == 1
result = {'status': 'PASS', 'blender': bpy.app.version_string, 'editable_meshes': len(meshes),
          'source_reopened': True, 'coordinate_mapping': 'Three (x,y,z) -> Blender (x,-z,y)',
          'tolerance_metres': .00001}
target = here / 'reports/blender-source.json'
assert not target.is_symlink()
fd, name = tempfile.mkstemp(prefix='.source-check-', dir=target.parent)
with os.fdopen(fd, 'w') as handle:
    json.dump(result, handle, indent=2)
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
os.replace(name, target)
print('PASS: saved source reopened; 43 editable parts match layout')

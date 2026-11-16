"""Reopen native source and export a controlled edit to a temporary directory."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import tempfile
import bpy
import bmesh

HERE = Path(__file__).resolve().parent
source = HERE / 'sources/tv-wall-mounted.blend'
original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
root = bpy.data.objects['ASSET_TVWallMounted']
assert tuple(root.location) == (0, 0, 0)
assert bpy.context.scene.unit_settings.system == 'METRIC'
assert bpy.context.scene.unit_settings.scale_length == 1
meshes = [obj for obj in root.children_recursive if obj.type == 'MESH']
for obj in meshes:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in mesh.edges), obj.name
    assert mesh.calc_volume() > 0, obj.name
    mesh.free()
target = bpy.data.objects['MOUNT_VESAWallBracket']
edited_name = target.name
for vertex in target.data.vertices:
    vertex.co.x *= .92
target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .77
out = Path(tempfile.gettempdir()) / 'tv-wall-mounted-source-edit'
out.mkdir(exist_ok=True)
edited_source = out / 'edited.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(edited_source), compress=True)
bpy.ops.wm.open_mainfile(filepath=str(edited_source))
assert bpy.data.objects[edited_name].data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value > .769
spec = importlib.util.spec_from_file_location('tv_generator', HERE / 'generate.py')
generator = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(generator)
generator.export(out / 'edited.glb')
assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
report = {
    'result': 'PASS', 'source_reopened': True, 'editable_mesh_parts': len(meshes),
    'closed_manifold_meshes': len(meshes), 'units': 'metres',
    'blender_version': bpy.app.version_string, 'source_sha256': original_hash,
    'edited_mesh': 'MOUNT_VESAWallBracket', 'edit': 'Scale local X vertices by 0.92; roughness to 0.77',
    'original_source_unchanged': True,
    'edited_glb_sha256': hashlib.sha256((out / 'edited.glb').read_bytes()).hexdigest(),
}
(HERE / 'reports/sources.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))

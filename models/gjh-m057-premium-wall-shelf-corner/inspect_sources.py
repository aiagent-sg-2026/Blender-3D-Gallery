"""Test a saved-source edit against an unchanged export from the same toolchain."""
from pathlib import Path
import bpy, bmesh, hashlib, importlib.util, json, sys
p = Path(__file__).resolve().parent
sys.path.insert(0, str(p.parents[1] / 'scripts'))
from blender_degenerate_cleanup import geometry_counts
source = p / 'sources' / (p.name + '.blend')
originals = [source, *sorted((p / 'exports').glob('*.glb')), *sorted((p / 'textures').glob('*.png'))]
digest = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
before = {str(f.relative_to(p)): digest(f) for f in originals}
bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False, load_ui=False)
bpy.context.preferences.filepaths.save_version = 0
root = bpy.data.objects['ASSET_GJHM057']
meshes = [o for o in root.children_recursive if o.type == 'MESH']
assert len(meshes) == 42
assert bpy.context.scene.unit_settings.system == 'METRIC'
assert bpy.context.scene.unit_settings.scale_length == 1
for obj in meshes:
    bm = bmesh.new(); bm.from_mesh(obj.data)
    assert bm.calc_volume() > 0, obj.name
    bm.free()
spec = importlib.util.spec_from_file_location('m057_generator', p / 'generate.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
out = p / 'reports' / 'source-edit-current'; out.mkdir(exist_ok=True)
mod.export(out / 'control.glb')
target = sorted(meshes, key=lambda o: o.name)[0]
target_name = target.name
assert target.data.users == 1
for vertex in target.data.vertices:
    vertex.co.x *= .97
target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .71
edited = out / 'edited.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(edited), compress=True, relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(edited), use_scripts=False, load_ui=False)
mod.export(out / 'edited.glb')
counts = geometry_counts(list(bpy.data.objects['ASSET_GJHM057'].children_recursive))
assert sum(row['zero_area_triangles'] for row in counts) == 0, counts
assert before == {str(f.relative_to(p)): digest(f) for f in originals}
report = {'source_sha256': before[str(source.relative_to(p))], 'editable_mesh_parts': len(meshes),
          'edited_mesh': target_name, 'saved_reopened': True, 'export_without_regeneration': True,
          'original_source_unchanged': True, 'all_original_assets_unchanged': True,
          'blender_version': bpy.app.version_string, 'zero_area_triangles': 0,
          'comparison_basis': 'same-toolchain unchanged source control',
          'control_glb': str((out / 'control.glb').relative_to(p)),
          'edited_glb': str((out / 'edited.glb').relative_to(p)), 'original_asset_hashes': before}
(p / 'reports' / 'sources.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS saved source edit, unchanged same-toolchain control, original assets unchanged')

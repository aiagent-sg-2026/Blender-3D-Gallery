"""Save/reopen a real edit without changing the canonical source or clips."""
from pathlib import Path
import bpy,bmesh,json,hashlib,importlib.util,sys
p=Path(__file__).resolve().parent;source=p/'sources/atm-kiosk.blend'
sys.path.insert(0,str(p.parents[1]/'scripts'))
from blender_degenerate_cleanup import geometry_counts
from blender_animation_snapshot import animation_snapshot
files=[source,p/'exports/optimized.glb']
digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before={str(f.relative_to(p)):digest(f) for f in files}
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False)
bpy.context.preferences.filepaths.save_version=0
root=bpy.data.objects['ASSET_ATMKiosk'];root_name=root.name;meshes=[o for o in root.children_recursive if o.type=='MESH'];assert len(meshes)==14
assert bpy.context.scene.unit_settings.scale_length==1 and bpy.context.scene.unit_settings.system=='METRIC'
for obj in meshes:
 bm=bmesh.new();bm.from_mesh(obj.data);assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume()>0,obj.name;bm.free()
actions=animation_snapshot()
spec=importlib.util.spec_from_file_location('edit_generator',p/'generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
out=p/'reports/source-edit-current';out.mkdir(exist_ok=True)
g.export(out/'control.glb')
target=sorted(meshes,key=lambda o:o.name)[0];name=target.name;assert name=='BODY_Front' and target.data.users==1
for vertex in target.data.vertices:vertex.co.x*=.92
material=target.data.materials[0];material_name=material.name
material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.77
edited=out/'edited.blend';bpy.ops.wm.save_as_mainfile(filepath=str(edited),compress=True,relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(edited),use_scripts=False,load_ui=False);g.export(out/'edited.glb')
assert animation_snapshot()==actions,'Editing a static mesh must preserve all original action data'
assert sum(r['zero_area_triangles'] for r in geometry_counts(bpy.data.objects[root_name].children_recursive))==0
assert before=={str(f.relative_to(p)):digest(f) for f in files}
report={'source_reopened':'PASS','blender_version':bpy.app.version_string,'source_sha256':before['sources/atm-kiosk.blend'],
 'editable_mesh_parts':14,'closed_manifold_meshes':14,'edited_mesh':name,'edited_material':material_name,
 'edit':'Local X vertices scaled by 0.92; shared material roughness changed to 0.77',
 'original_source_unchanged':True,'original_assets_unchanged':before,'animation_snapshot':actions,
 'comparison_basis':'same-toolchain unchanged saved-source control',
 'control_glb':str((out/'control.glb').relative_to(p)),'edited_glb':str((out/'edited.glb').relative_to(p))}
(p/'reports/sources.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS saved source edit, source action unchanged, original assets unchanged')

"""Prove the existing wall-position/material edit against a native control."""
from pathlib import Path
import bpy,json,hashlib,importlib.util,sys,struct
p=Path(__file__).resolve().parent;source=p/'sources/passenger-lift.blend'
sys.path.insert(0,str(p.parents[1]/'scripts'))
from blender_degenerate_cleanup import geometry_counts
from blender_animation_snapshot import animation_snapshot
files=[source,p/'exports/passenger-lift.glb'];digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();before={str(f.relative_to(p)):digest(f) for f in files}
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False);bpy.context.preferences.filepaths.save_version=0
root_name='ASSET_PassengerLift';objects=list(bpy.data.objects[root_name].children_recursive);assert len(objects)==90
assert sum(o.type=='MESH' for o in objects)==77 and sum(o.type=='FONT' for o in objects)==3
actions=animation_snapshot();spec=importlib.util.spec_from_file_location('edit_generator',p/'generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
out=p/'reports/source-edit-current';out.mkdir(exist_ok=True);g.export(bpy.data.objects[root_name],out/'control.glb')
target=bpy.data.objects['Cab_BackWall'];position=list(target.location);target.location.x+=.123;edited_position=list(target.location)
mat=target.data.materials[0];material_name=mat.name;rough_before=mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.73
edited=out/'edited.blend';bpy.ops.wm.save_as_mainfile(filepath=str(edited),compress=True,relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(edited),use_scripts=False,load_ui=False);g.export(bpy.data.objects[root_name],out/'edited.glb')
assert animation_snapshot()==actions;assert before=={str(f.relative_to(p)):digest(f) for f in files}
assert sum(r['zero_area_triangles'] for r in geometry_counts(bpy.data.objects[root_name].children_recursive))==0
def read_json(file):
 data=file.read_bytes();size=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+size])
control_json=read_json(out/'control.glb');edited_json=read_json(out/'edited.glb')
node_x=lambda data:next((n.get('matrix',[0]*16)[12] if 'matrix' in n else n.get('translation',[0,0,0])[0]) for n in data['nodes'] if n.get('name')=='Cab_BackWall')
exported_delta=node_x(edited_json)-node_x(control_json);assert abs(exported_delta-.123)<1e-6
exported_roughness=next(m['pbrMetallicRoughness']['roughnessFactor'] for m in edited_json['materials'] if m.get('name')==material_name)
assert abs(exported_roughness-.73)<1e-6
report={'source_sha256':before['sources/passenger-lift.blend'],'source_reopened':'PASS','units':'metres','scale_length':1,'meshes':77,'fonts':3,
 'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None} for o in bpy.data.objects[root_name].children_recursive],
 'blender_version':bpy.app.version_string,'original_assets_unchanged':before,'animation_snapshot':actions,
 'comparison_basis':'same-toolchain unchanged saved-source control','control_glb':str((out/'control.glb').relative_to(p)),'edited_glb':str((out/'edited.glb').relative_to(p)),
 'edit_proof':{'node':'Cab_BackWall','before':position,'after':edited_position,'delta_x':.123,'material':material_name,'roughness_before':rough_before,'roughness_after':.73,'output':str((out/'edited.glb').relative_to(p)),'saved_copy':str(edited.relative_to(p)),'copy_sha256':digest(edited),'glb_node_delta_x':exported_delta,'material_roughness_survived_save_reopen_export':True,'result':'PASS'}}
(p/'reports/source.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS saved lift wall edit, five source actions and canonical files unchanged')

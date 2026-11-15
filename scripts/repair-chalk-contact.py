"""Guarded MODEL-0005 placement-only repair; preserve the baseline first."""
import bpy,hashlib,json,sys
from pathlib import Path

source=Path(bpy.data.filepath)
expected='907f2038d32c0ded1906d89d7f14bc6b2364cde22002c337d8187c5d3431c287'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected,'Unexpected source revision'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
standalone=source.parent/'exports/chalk.glb';original_standalone=standalone.read_bytes()
assert hashlib.sha256(original_standalone).hexdigest()=='218bb66d9eb918e0d6131800e5f3446e5820e5c74a2ba4c56840faccdbe25915'
root=bpy.data.objects['ASSET_Chalk'];meshes=[o for o in root.children_recursive if o.type=='MESH'];assert len(meshes)==2
def fingerprints():
    result={}
    for ob in bpy.data.objects:
        transform=dict(type=ob.type,parent=ob.parent.name if ob.parent else None,matrix_world=[list(row) for row in ob.matrix_world]);geometry={}
        if ob.type=='MESH':
            m=ob.data;geometry=dict(vertices=[list(v.co) for v in m.vertices],faces=[(list(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],sharp=[e.use_edge_sharp for e in m.edges],uv=[(u.name,[list(v.uv) for v in u.data]) for u in m.uv_layers],materials=[mat.name if mat else None for mat in m.materials],normals=[list(n.vector) for n in m.corner_normals])
        result[ob.name]={key:hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest() for key,value in [('transform',transform),('geometry',geometry)]}
    return result
bpy.context.view_layer.update();before=fingerprints()
root.location.z-=.0016
bpy.context.view_layer.update();after=fingerprints();assert before.keys()==after.keys()
assert all(before[name]['geometry']==after[name]['geometry'] for name in before),'Mesh data, UVs, materials or normals changed'
changed=[name for name in before if before[name]['transform']!=after[name]['transform']]
assert set(changed)=={root.name,*[o.name for o in meshes]},'Unrelated object transform changed'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(source))
def export(name,roots):
    bpy.ops.object.select_all(action='DESELECT')
    for asset in roots:
        asset.select_set(True)
        for ob in asset.children_recursive:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(source.parent/'exports'/name),export_format='GLB',use_selection=True,export_apply=True)
location=root.location.copy()
try:
    root.location=(0,0,0);export('chalk.glb',[root])
finally:root.location=location
reexported=standalone.read_bytes()
def semantic_glb(data):
    length=int.from_bytes(data[12:16],'little');document=json.loads(data[20:20+length])
    # Historical standalone mesh datablocks have older generic Cube names.
    # They are labels only; asset-root/node identity and all payloads must match.
    for mesh in document['meshes']:mesh.pop('name',None)
    return document,data[28+length:]
assert semantic_glb(reexported)==semantic_glb(original_standalone),'Normalized standalone changed beyond generic mesh labels'
standalone.write_bytes(original_standalone)
export('billiards-scene.glb',[o for o in bpy.context.scene.objects if o.name.startswith('ASSET_')])
report=dict(defect='CHALK-001',input_sha256=expected,output_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),root_lowered_m=.0016,expected_rail_overlap_m=.0001,changed_transform_objects=changed,all_geometry_uv_material_assignments_and_normals_unchanged=True,unrelated_transforms_unchanged=True,normalized_standalone_semantically_identical=True,standalone_reexport_sha256=hashlib.sha256(reexported).hexdigest(),standalone_preserved_sha256=hashlib.sha256(original_standalone).hexdigest(),before=before,after=after)
(out/'source-migration.json').write_text(json.dumps(report,indent=2)+'\n');print('CHALK_CONTACT_REPAIRED',json.dumps({k:report[k] for k in ['output_sha256','changed_transform_objects']}))

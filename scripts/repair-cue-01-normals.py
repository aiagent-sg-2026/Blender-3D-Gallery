"""Guarded CUE-001 migration; only Cue 01 shading and its two exports change.

Run after preserving scene.blend and GLBs. Never run the full pack generator
for this migration: all other model files must remain unchanged.
"""
import bpy
import hashlib
import json
import sys
from pathlib import Path

source=Path(bpy.data.filepath)
expected='95f940fe5f10fb8d2dcd9d5ca6db04eaaf1690017e3b69929bfea1af110c97bf'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected, 'Unexpected source revision'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
root=bpy.data.objects['ASSET_Cue_01']
meshes=[o for o in root.children_recursive if o.type=='MESH']
assert len(meshes)==4

def fingerprints():
    rows={}
    for ob in bpy.data.objects:
        geometry={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix_world':[list(row) for row in ob.matrix_world]}
        shading={}
        if ob.type=='MESH':
            mesh=ob.data
            geometry.update(vertices=[list(v.co) for v in mesh.vertices],polygons=[(list(p.vertices),p.material_index) for p in mesh.polygons],uv=[(uv.name,[list(v.uv) for v in uv.data]) for uv in mesh.uv_layers],materials=[m.name if m else None for m in mesh.materials])
            shading={'smooth_faces':[p.use_smooth for p in mesh.polygons],'sharp_edges':[e.use_edge_sharp for e in mesh.edges]}
        rows[ob.name]={key:hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest() for key,value in [('geometry',geometry),('shading',shading)]}
    return rows

bpy.context.view_layer.update()
before=fingerprints();cap_count=0;edge_count=0
for ob in meshes:
    mesh=ob.data;caps=[p for p in mesh.polygons if len(p.vertices)>4]
    assert len(caps)==2 and all(p.use_smooth for p in mesh.polygons)
    edges={mesh.loops[li].edge_index for p in caps for li in p.loop_indices}
    assert all(not mesh.edges[i].use_edge_sharp for i in edges)
    for p in caps:p.use_smooth=False
    for i in edges:mesh.edges[i].use_edge_sharp=True
    cap_count+=len(caps);edge_count+=len(edges)
    mesh.update()
assert (cap_count,edge_count)==(8,144)
bpy.context.view_layer.update();after=fingerprints()
assert before.keys()==after.keys()
assert all(before[name]['geometry']==after[name]['geometry'] for name in before), 'Geometry, UV, material ownership or transform changed'
changed=[name for name in before if before[name]['shading']!=after[name]['shading']]
assert set(changed)=={ob.name for ob in meshes}, 'Unrelated model shading changed'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(source))

def export(name,roots):
    bpy.ops.object.select_all(action='DESELECT')
    for asset in roots:
        asset.select_set(True)
        for ob in asset.children_recursive:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(source.parent/'exports'/name),export_format='GLB',use_selection=True,export_apply=True)

location=root.location.copy()
try:
    root.location=(0,0,0)
    export('cue_01.glb',[root])
finally:
    root.location=location
export('billiards-scene.glb',[o for o in bpy.context.scene.objects if o.name.startswith('ASSET_')])
report={'defect':'CUE-001','input_sha256':expected,'output_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changed_shading_objects':changed,'planar_caps':cap_count,'sharp_boundary_edges':edge_count,'all_geometry_uv_material_assignments_and_transforms_unchanged':True,'unrelated_source_shading_unchanged':True,'before':before,'after':after}
(out/'source-migration.json').write_text(json.dumps(report,indent=2)+'\n')
print('CUE_001_REPAIRED',json.dumps({k:report[k] for k in ['changed_shading_objects','planar_caps','sharp_boundary_edges']}),flush=True)

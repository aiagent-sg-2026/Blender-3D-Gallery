"""Revision-guarded MODEL-0004 capacity follow-up; preserve the baseline first."""
import bpy, hashlib, json, runpy, sys
from pathlib import Path

source=Path(bpy.data.filepath)
expected='efaf70ef5c6071813edd0a869ca5f143cc83c58d82253123df1752b54dccff56'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected,'Unexpected source revision'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
root=bpy.data.objects['ASSET_Triangle_Rack'];bars=sorted(root.children,key=lambda ob:ob.name)
assert len(bars)==3 and all(ob.type=='MESH' for ob in bars)
bpy.context.view_layer.update()

def fingerprints():
    rows={}
    for ob in bpy.data.objects:
        data=dict(type=ob.type,parent=ob.parent.name if ob.parent else None,matrix=[list(row) for row in ob.matrix_world])
        if ob.type=='MESH':
            m=ob.data
            data.update(vertices=[list(v.co) for v in m.vertices],faces=[(list(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],sharp=[e.use_edge_sharp for e in m.edges],uv=[(u.name,[list(v.uv) for v in u.data]) for u in m.uv_layers],materials=[mat.name if mat else None for mat in m.materials],normals=[list(n.vector) for n in m.corner_normals])
        rows[ob.name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    return rows

before=fingerprints()
original={ob.name:dict(vertices=[list(v.co) for v in ob.data.vertices],uv=[(u.name,[list(v.uv) for v in u.data]) for u in ob.data.uv_layers],faces=[(list(p.vertices),p.material_index) for p in ob.data.polygons],matrix=[list(row) for row in ob.matrix_world]) for ob in bars}
runpy.run_path(str(source.parent/'rack_geometry.py'))['fit_rack_bars'](bars,root.matrix_world.translation.z)
for ob in bars:
    old=original[ob.name];m=ob.data
    assert all(tuple(v.co[:2])==tuple(p[:2]) for v,p in zip(m.vertices,old['vertices']))
    assert old['uv']==[(u.name,[list(v.uv) for v in u.data]) for u in m.uv_layers]
    assert old['faces']==[(list(p.vertices),p.material_index) for p in m.polygons]
bpy.context.view_layer.update();after=fingerprints()
allowed={ob.name for ob in bars}
assert before.keys()==after.keys()
changed=[name for name in before if before[name]!=after[name]]
assert set(changed)==allowed,'Unrelated source object changed'
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
    root.location=(0,0,0);export('triangle_rack.glb',[root])
finally:
    root.location=location
export('billiards-scene.glb',[ob for ob in bpy.context.scene.objects if ob.name.startswith('ASSET_')])
report=dict(input_sha256=expected,output_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),changed_objects=changed,source_scope='Only the three rack bar centerlines/transforms and longitudinal mesh coordinates change for capacity, with corresponding cap normals recomputed. UVs, face/material assignments, radial profiles, root position and all unrelated objects remain unchanged.',rack_lowered_m=0,expected_cloth_overlap_m=.0001,before=before,after=after)
(out/'capacity-source-migration.json').write_text(json.dumps(report,indent=2)+'\n')
print('RACK_CAPACITY_REPAIRED',json.dumps({k:report[k] for k in ['changed_objects','output_sha256']}))

"""Check both editable sources and clean GLB reimports in Blender."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
items=[('mall-floor-corner-trim','ASSET_MallFloorCornerTrim',[.06,.06,.03],2,0),('mall-wall-corner','ASSET_MallWallCorner',[1.26,1.26,3],19,None)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(objects):
    pts=[o.matrix_world @ Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
    return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
def check(b,d):
    for i in range(3):assert abs(b['max'][i]-b['min'][i]-d[i])<.0001,(b,d)
for slug,name,dim,n,top in items:
    base=root/'models'/slug;source=base/'sources'/f'{slug}.blend';glb=base/'exports'/f'{slug}.glb'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);bpy.context.view_layer.update();obj=bpy.data.objects[name];parts=list(obj.children_recursive)
    assert sum(o.type=='MESH' for o in parts)==n,(slug,len(parts))
    before=bounds(parts);check(before,dim)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));bpy.context.view_layer.update()
    after=bounds(bpy.context.scene.objects);check(after,dim)
    for k in ['min','max']:
        for a,b in zip(before[k],after[k]):assert abs(a-b)<.0001,(slug,before,after)
    if top is not None:assert abs(after['max'][2]-top)<.0001
    out={'result':'PASS','blender':bpy.app.version_string,'sourceSha256':sha(source),'glbSha256':sha(glb),'sourceMeshes':n,'sourceBoundsBlenderMetres':before,'reimportBoundsBlenderMetres':after}
    (base/'reports/source-reimport.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

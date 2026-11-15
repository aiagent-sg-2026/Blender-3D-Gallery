"""Inspect editable source and a clean GLB reimport."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
HERE=Path(__file__).resolve().parent
source=HERE/'sources/mall-floor-edge-trim.blend';glb=HERE/'exports/mall-floor-edge-trim.glb'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(objects):
    points=[o.matrix_world @ Vector(c) for o in objects if o.type=='MESH' for c in o.bound_box]
    return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
def check(b):
    assert all(abs((b['max'][i]-b['min'][i])-v)<.0001 for i,v in enumerate([1.2,.06,.03])),b
    assert abs(b['max'][2])<.0001,b
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);bpy.context.view_layer.update()
root=bpy.data.objects['ASSET_MallFloorEdgeTrim'];objects=list(root.children_recursive)
assert len([o for o in objects if o.type=='MESH'])==2
assert all(any(o.name==name for o in objects) for name in ['TRIM_Body','TRIM_Cap','CONNECTOR_Left','CONNECTOR_Right'])
a=bounds(objects);check(a)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));bpy.context.view_layer.update()
b=bounds(bpy.context.scene.objects);check(b)
out={'blender':bpy.app.version_string,'sourceSha256':digest(source),'glbSha256':digest(glb),'sourceMeshes':2,'sourceBoundsBlenderMetres':a,'reimportBoundsBlenderMetres':b,'result':'PASS'}
(HERE/'reports/source-reimport.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

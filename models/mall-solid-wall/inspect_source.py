"""Reopen editable source and independently reimport the GLB to inspect bounds."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
HERE=Path(__file__).resolve().parent
source=HERE/'sources/mall-solid-wall.blend'
glb=HERE/'exports/mall-solid-wall.glb'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def bounds(objects):
    points=[obj.matrix_world @ Vector(corner) for obj in objects if obj.type=='MESH' for corner in obj.bound_box]
    return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
def check(b):
    expected=[1.2,.12,3.0]
    size=[b['max'][i]-b['min'][i] for i in range(3)]
    assert all(abs(a-b)<.0001 for a,b in zip(size,expected)),size
    assert abs(b['min'][2])<.0001,b
    return size
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
root=bpy.data.objects['ASSET_MallSolidWall']
bpy.context.view_layer.update()
children=list(root.children_recursive)
assert len([o for o in children if o.type=='MESH'])==6
assert all(bpy.data.objects.get(n) for n in ['PANEL_1','PANEL_2','PANEL_3','CONNECTOR_Left','CONNECTOR_Right'])
source_bounds=bounds(children); check(source_bounds)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
bpy.context.view_layer.update()
imported=bounds(bpy.context.scene.objects); check(imported)
out={'blender':bpy.app.version_string,'source_sha256':digest(source),'glb_sha256':digest(glb),'source_meshes':6,'source_bounds_blender_m':source_bounds,'reimport_bounds_blender_m':imported,'result':'PASS'}
(HERE/'reports/source-reimport.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))

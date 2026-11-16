"""Independent Blender 5.x GLB importer and geometry gate. Use: blender -b --python qa/verify_blender.py -- path.glb."""
import bpy, sys, json, math, os
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
paths=args or [os.path.abspath(os.path.join(os.path.dirname(__file__),'../exports/chibi-visitor-v2.glb'))]
for path in paths:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    if not meshes:raise RuntimeError('No imported meshes: '+path)
    extents=[o.matrix_world@Vector(corner) for o in meshes for corner in o.bound_box]
    minxyz=[min(p[i] for p in extents) for i in range(3)]
    maxxyz=[max(p[i] for p in extents) for i in range(3)]
    tri=sum(sum(len(p.vertices)-2 for p in obj.data.polygons) for obj in meshes)
    vertices=sum(len(o.data.vertices) for o in meshes)
    materials=len({m.name for o in meshes for m in o.data.materials if m is not None})
    detail={'file':os.path.basename(path),'bytes':os.path.getsize(path),'meshes':len(meshes),'vertices':vertices,'triangles':tri,'materials':materials,'bounds_min':[round(v,4) for v in minxyz],'bounds_max':[round(v,4) for v in maxxyz],'animations':len(bpy.data.actions)}
    print('CHIBI_V2_BLENDER_IMPORT_QA='+json.dumps(detail),flush=True)
    assert 17<=len(meshes)<=25,detail
    assert 0<vertices<=60000 and 0<tri<=40000,detail
    assert materials>=12,detail
    assert -.10<minxyz[2]<.12 and 1.70<maxxyz[2]<2.05,detail
    assert maxxyz[0]-minxyz[0]<1.6 and maxxyz[1]-minxyz[1]<1.5,detail
print('CHIBI_V2_BLENDER_PASS',flush=True)

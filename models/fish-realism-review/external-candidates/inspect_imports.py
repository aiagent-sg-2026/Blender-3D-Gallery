import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
out=[]
for slug in ['barramundi','betta']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/slug/'original.glb'))
 bpy.context.view_layer.update();items=[]
 for obj in bpy.context.scene.objects:
  if obj.type=='MESH':
   pts=[obj.matrix_world@Vector(c) for c in obj.bound_box];lo=[min(p[d] for p in pts) for d in range(3)];hi=[max(p[d] for p in pts) for d in range(3)]
   items.append({'name':obj.name,'vertices':len(obj.data.vertices),'bounds':[lo,hi],'materials':[m.name for m in obj.data.materials]})
 info={'slug':slug,'meshes':items,'rigs':[{'name':o.name,'bones':len(o.data.bones)} for o in bpy.context.scene.objects if o.type=='ARMATURE'],'actions':[{'name':a.name,'frames':list(a.frame_range)} for a in bpy.data.actions],'images':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images]}
 out.append(info)
(ROOT/'import-inventory.json').write_text(json.dumps(out,indent=2)+'\n');print('IMPORT_INVENTORY',json.dumps(out),flush=True)

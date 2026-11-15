"""Place paired pelvic bases on the skin and verify actual posed surface contact."""
import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def pelvic_base(profile,side,u,root_x=-.44):
 x=root_x+.05*(u-.5);hi,lo,width=profile(x);ratio=.24
 return Vector((x,side*width*ratio,(hi+lo)/2-(hi-lo)/2*math.sqrt(1-ratio*ratio)+.0006))

def repair_pelvic_roots(scene,profile):
 repaired=[]
 for obj in scene.objects:
  if obj.type!='MESH' or not obj.name.startswith('Pelvic_') or obj.get('pelvic_surface_anchor'):continue
  side=1 if sum(v.co.y for v in obj.data.vertices)>0 else -1
  uv=obj.data.uv_layers.active;coordinates={loop.vertex_index:uv.data[loop.index].uv.copy() for loop in obj.data.loops};old=Vector((-.44,side*.12,profile(-.44)[1]));transform=obj.matrix_local.copy();inverse=transform.inverted()
  for vertex in obj.data.vertices:
   u,span=coordinates[vertex.index];delta=pelvic_base(profile,side,u)-old;vertex.co=inverse@(transform@vertex.co+(1-span)*delta)
  obj.data.update();obj['pelvic_surface_anchor']='Ventrolateral body surface with a small embedded root curve';repaired.append(obj.name)
 return repaired

def check_surface_contact(scene):
 meshes=[o for o in scene.objects if o.type=='MESH'];body=next((o for o in meshes if o.name.startswith(('Skin_AnatomicalProfile','Ribbon_ContinuousBody'))),None)
 assert body is not None,'Need the real body surface for fin contact QA'
 dg=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(dg);tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in evaluated.data.vertices],[list(p.vertices) for p in evaluated.data.polygons]);results={}
 for obj in meshes:
  if not obj.name.startswith(('Dorsal_','Anal_','Pelvic_','Pectoral_','Caudal_','Finlet_','Barbel_')) or not obj.data.uv_layers.active:continue
  uv=obj.data.uv_layers.active;indices={loop.vertex_index for loop in obj.data.loops if abs(uv.data[loop.index].uv.y)<1e-7};assert indices,obj.name;evaluated=obj.evaluated_get(dg);signed=[]
  for i in indices:
   p=evaluated.matrix_world@evaluated.data.vertices[i].co;point,normal,_,distance=tree.find_nearest(p);signed.append((p-point).dot(normal))
  if obj.name.startswith(('Pectoral_Filament_','Barbel_')):
   # A tubular ray base straddles the skin; its outer ring naturally protrudes.
   assert min(signed)<.0015 and max(signed)<.0055,(obj.name,'Detached tubular sensory base',min(signed),max(signed))
  elif obj.name.startswith('Caudal_'):
   # The leading caudal edge can rise beyond the peduncle but must intersect it.
   assert min(signed)<.002,(obj.name,'Disconnected caudal root',min(signed))
  else:assert max(signed)<.002,(obj.name,'Fin base outside actual posed skin',max(signed))
  results[obj.name]={'root_vertices':len(indices),'min_signed_distance':min(signed),'max_signed_distance':max(signed)}
 return results

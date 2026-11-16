"""Anchor fin roots to the body and feather stabilizing motion toward the tips."""
import bpy,bisect

def attach_fin_roots(scene,tip_blend=.85):
 xs=[-1.8,-.8,-.15,.45,.95,1.4,1.8]
 for obj in scene.objects:
  role=obj.get('deform_role')
  if obj.type!='MESH' or role not in ['dorsal','anal','pectoral'] or not obj.data.uv_layers.active:continue
  mod=next((m for m in obj.modifiers if m.type=='ARMATURE'),None)
  if not mod:continue
  spans=[0.0]*len(obj.data.vertices);uv=obj.data.uv_layers.active
  for loop in obj.data.loops:spans[loop.vertex_index]=float(uv.data[loop.index].uv.y)
  # Volumetric fin caps have UV seams; their anatomical span is a point attribute.
  span_attribute=obj.data.attributes.get('fin_span')
  if span_attribute:spans=[float(datum.value) for datum in span_attribute.data]
  for group in obj.vertex_groups:group.remove(list(range(len(obj.data.vertices))))
  groups={g.name:g for g in obj.vertex_groups}
  for vertex,t in zip(obj.data.vertices,spans):
   p=obj.matrix_local@vertex.co;i=max(0,min(5,bisect.bisect_right(xs,p.x)-1));f=max(0,min(1,(p.x-xs[i])/(xs[i+1]-xs[i])));blend=tip_blend*max(0,min(1,t))**1.7
   weights={'Spine_%02d'%i:(1-f)*(1-blend),'Spine_%02d'%(i+1):f*(1-blend)}
   extra='Dorsal' if role=='dorsal' else 'Anal' if role=='anal' else 'Pectoral_L' if p.y>0 else 'Pectoral_R';weights[extra]=blend
   for name,value in weights.items():
    if value>1e-7:groups[name].add([vertex.index],value,'REPLACE')
  obj['fin_root_anchor']='Body spine weights at span=0; independent motion feathers to tip'
 bpy.context.view_layer.update()

"""Build free sensory fin rays with body-anchored roots."""
import math
from mathutils import Vector

def build_filaments(B, config, profile, flank):
 count=config.get('pectoral_filaments',0)
 if not count:return
 mat=B.material('SensoryPectoralFilaments',tuple(config.get('filament_color',[.49,.50,.42])),.50,.02)
 for side in [-1,1]:
  for ray in range(count):
   x=config['gill_x']+.11+.006*ray;z=config.get('pectoral_root_z',-.18)-.035-.012*ray;y=flank(x,z,side,.001)
   length=config.get('filament_lengths',[.32,.46,.60,.72])[ray];drop=.16+.035*ray
   points=[Vector((x+length*t,y+side*(.025*t+.022*math.sin(math.pi*t)),z-drop*t+.045*math.sin(math.pi*t))) for t in [i/32 for i in range(33)]]
   vertices=[];uv=[];faces=[];rings=8
   for i,p in enumerate(points):
    t=i/32;direction=(points[min(32,i+1)]-points[max(0,i-1)]).normalized();normal=direction.cross(Vector((0,0,1))).normalized();binormal=direction.cross(normal).normalized();radius=.0032*(1-.82*t)
    for j in range(rings):
     angle=2*math.pi*j/rings;vertices.append(tuple(p+radius*(math.cos(angle)*normal+math.sin(angle)*binormal)));uv.append((j/rings,t))
   for i in range(32):
    for j in range(rings):a=i*rings+j;b=i*rings+(j+1)%rings;faces.append((a,b,b+rings,a+rings))
   faces.extend([tuple(range(rings-1,-1,-1)),tuple(32*rings+j for j in range(rings))])
   obj=B.mesh('Pectoral_Filament_%s_%d'%(side,ray+1),vertices,faces,mat,uv,deform='pectoral');obj['anatomy']='One free sensory pectoral ray; root follows body, distal weights feather pectoral motion'


def build_pelvic_filaments(B, config, profile):
 """Build the paired free pelvic rays used by gouramis."""
 if not config.get('pelvic_filaments'):return
 from fin_attachment import pelvic_base
 mat=B.material('SensoryPelvicFilaments',tuple(config.get('pelvic_filament_color',[.46,.45,.36])),.46)
 targets=config['pelvic_filament_targets']
 for index,side in enumerate([-1,1]):
  root=pelvic_base(profile,side,.5,config.get('pelvic_filament_root_x',-.85));target=Vector(targets[index]);target.y*=side;control=root+(target-root)*.45+Vector((.03,side*.025,-.04));points=[root*(1-t)**2+control*2*t*(1-t)+target*t*t for t in [i/40 for i in range(41)]];vertices=[];uv=[];faces=[];rings=8
  for i,p in enumerate(points):
   t=i/40;direction=(points[min(40,i+1)]-points[max(0,i-1)]).normalized();normal=direction.cross(Vector((0,0,1))).normalized();binormal=direction.cross(normal).normalized();radius=.0023*(1-.82*t)
   for j in range(rings):
    angle=2*math.pi*j/rings;vertices.append(tuple(p+radius*(math.cos(angle)*normal+math.sin(angle)*binormal)));uv.append((j/rings,t))
  for i in range(40):
   for j in range(rings):a=i*rings+j;b=i*rings+(j+1)%rings;faces.append((a,b,b+rings,a+rings))
  faces.extend([tuple(range(rings-1,-1,-1)),tuple(40*rings+j for j in range(rings))]);obj=B.mesh('Pelvic_Filament_'+str(side),vertices,faces,mat,uv,deform='pelvic_sensory');obj['sensory_side']=side;obj['sensory_root']=list(root)


def bind_pelvic_filaments(rig):
 """Feather each sensory ray onto its own cyclic control, preserving body roots."""
 import bpy
 rays=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('deform_role')=='pelvic_sensory']
 if not rays:return
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for obj in rays:
  name='Pelvic_Sensory_'+('L' if obj['sensory_side']>0 else 'R');bone=rig.data.edit_bones.new(name);root=Vector(obj['sensory_root']);bone.head=root;bone.tail=root+Vector((.2,0,-.25));bone.parent=rig.data.edit_bones['Spine_01'];obj['sensory_control']=name
 bpy.ops.object.mode_set(mode='OBJECT')
 for obj in rays:
  baseline=[[(g.group,g.weight) for g in vertex.groups] for vertex in obj.data.vertices];indices=list(range(len(obj.data.vertices)));spans=[0.0]*len(indices)
  for loop in obj.data.loops:spans[loop.vertex_index]=obj.data.uv_layers.active.data[loop.index].uv.y
  for group in obj.vertex_groups:group.remove(indices)
  extra=obj.vertex_groups.new(name=obj['sensory_control'])
  for vertex,t,weights in zip(obj.data.vertices,spans,baseline):
   blend=.82*t**1.7
   for group,weight in weights:
    if weight*(1-blend)>1e-7:obj.vertex_groups[group].add([vertex.index],weight*(1-blend),'REPLACE')
   if blend>1e-7:extra.add([vertex.index],blend,'REPLACE')
  obj['fin_root_anchor']='Body spine roots; independently phased pelvic sensory control toward tips'
 for f in range(1,74,2):
  phase=2*math.pi*(f-1)/72
  for index,obj in enumerate(rays):
   bone=rig.pose.bones[obj['sensory_control']];bone.rotation_mode='XYZ';bone.rotation_euler=(.09*math.sin(phase+index*.9),.025*math.sin(phase+index*1.1),.06*math.sin(phase+index*1.3));bone.keyframe_insert(data_path='rotation_euler',frame=f,group=bone.name)
 bpy.context.scene.frame_set(1)

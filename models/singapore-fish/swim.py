"""Small portable skeletal swim rig; all movement is baked into the exported clip."""
import bpy, math
from mathutils import Vector

# Durations complete one tail cycle; tiny fish beat faster, long fish move slowly.
def profile(kind, slug):
 if kind=='ray':return 3.2,.025,.24
 if kind in ['eel','ribbon','snake','catlong']:return 2.4,.13,.10
 if kind=='shark':return (3.2 if slug=='whale-shark' else 2.4),.08,.07
 if kind=='puffer':return 1.6,.035,.28
 if kind in ['fancy','guppy','round']:return 1.6,.085,.24
 if kind in ['disc','diamond']:return 2.0,.055,.22
 return (2.4 if kind in ['bass','cat','arowana'] else 2.0),.09,.16

def rig_swim(root,kind,slug,h,w):
 scene=bpy.context.scene
 objects=[o for o in root.children_recursive if o.type=='MESH']
 data=bpy.data.armatures.new('SWIM_Skeleton');rig=bpy.data.objects.new('RIG_Swim',data);scene.collection.objects.link(rig);rig.parent=root
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 starts=[-.48,-.20,-.02,.16,.32,.48,.70];ends=starts[1:]+[1.20]
 names=[]
 for i,(a,b) in enumerate(zip(starts,ends)):
  bone=data.edit_bones.new('Spine_%02d'%i);bone.head=(a,0,0);bone.tail=(b,0,0)
  if i:bone.parent=data.edit_bones[names[-1]];bone.use_connect=True
  names.append(bone.name)
 for side,label in [(1,'L'),(-1,'R')]:
  bone=data.edit_bones.new('Fin_'+label);bone.head=(-.20,side*w*.8,0);bone.tail=(-.02,side*(w+.14),-.07);bone.parent=data.edit_bones[names[1]]
  if kind=='ray':bone.head=(-.12,0,0);bone.tail=(-.12,side*.4,0)
 for name,z in [('Dorsal',h*.75),('Anal',-h*.8)]:
  bone=data.edit_bones.new(name);bone.head=(.02,0,z);bone.tail=(.12,0,z+(h*.7 if z>0 else -h*.6));bone.parent=data.edit_bones[names[2]]
 bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
 def spine_weights(x):
  if x<=starts[0]:return {names[0]:1.}
  for i in range(len(starts)-1):
   if x<=starts[i+1]:
    t=(x-starts[i])/(starts[i+1]-starts[i]);return {names[i]:1-t,names[i+1]:t}
  return {names[-1]:1.}
 for obj in objects:
  groups={b.name:obj.vertex_groups.new(name=b.name) for b in data.bones}
  transform=obj.matrix_local
  for v in obj.data.vertices:
   p=transform @ v.co;weights=spine_weights(p.x);extra=None;blend=0.
   if kind=='ray' and obj.name.startswith('BODY_'):
    extra='Fin_L' if p.y>0 else 'Fin_R';blend=min(.95,(abs(p.y)/.34)**1.4)
   elif obj.name.startswith('PECTORAL_'):
    extra='Fin_L' if p.y>0 else 'Fin_R';blend=min(.95,max(0,(abs(p.y)-w*.70)/.15))
   elif obj.name.startswith(('DORSAL_','ANAL_')):
    extra='Dorsal' if obj.name.startswith('DORSAL_') else 'Anal';blend=min(.85,max(0,(abs(p.z)-h*.7)/(h*.7)))
   if extra:
    weights={n:value*(1-blend) for n,value in weights.items()};weights[extra]=blend
   for n,value in weights.items():
    if value>1e-7:groups[n].add([v.index],value,'REPLACE')
  mod=obj.modifiers.new('Swim deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False
 duration,amplitude,fin_amplitude=profile(kind,slug)
 fps=30;frames=round(duration*fps);scene.render.fps=fps;scene.frame_start=0;scene.frame_end=frames
 # Key every two frames, including an exactly matching endpoint for a seamless loop.
 for f in list(range(0,frames,2))+[frames]:
  phase=2*math.pi*f/frames
  for i,n in enumerate(names):
   pb=rig.pose.bones[n];pb.rotation_mode='XYZ'
   strength=(i/6)**.8
   if kind in ['eel','ribbon','snake','catlong']:strength=.18+.82*i/6
   angle=amplitude*strength*math.sin(phase-i*.58)
   if kind=='ray':angle*=.35
   pb.rotation_euler=(0,0,angle);pb.keyframe_insert(data_path='rotation_euler',frame=f,group=n)
  for side,label in [(1,'L'),(-1,'R')]:
   pb=rig.pose.bones['Fin_'+label];pb.rotation_mode='XYZ'
   pb.rotation_euler=(fin_amplitude*math.sin(phase+(0 if kind=='ray' else side*.35)),0,side*.045*math.sin(phase+math.pi/2));pb.keyframe_insert(data_path='rotation_euler',frame=f,group=pb.name)
  for n,sign in [('Dorsal',1),('Anal',-1)]:
   pb=rig.pose.bones[n];pb.rotation_mode='XYZ';pb.rotation_euler=(sign*.09*math.sin(phase+.8),0,.025*math.sin(phase));pb.keyframe_insert(data_path='rotation_euler',frame=f,group=n)
 action=rig.animation_data.action;action.name='Swim_Loop'
 # Blender 4.4+ stores F-curves in action slots; linear baked samples are portable.
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for key in curve.keyframe_points:key.interpolation='LINEAR'
 root['swim_duration_seconds']=duration;root['swim_style']=('pectoral undulation' if kind=='ray' else 'whole-body wave' if kind in ['eel','ribbon','snake','catlong'] else 'tail propulsion with fin stabilization')
 scene.frame_set(0)
 return rig

def export_swim(root,path):
 # glTF skinned mesh nodes must be identity-transform scene roots. Bake only
 # temporary mesh copies; retain the organized editable source hierarchy.
 meshes=[o for o in root.children_recursive if o.type=='MESH'];saved=[]
 bpy.ops.object.select_all(action='DESELECT')
 selected=[root]+list(root.children_recursive)
 for obj in meshes:
  saved.append((obj,obj.parent,obj.matrix_basis.copy(),obj.data))
  world=obj.matrix_world.copy();obj.data=obj.data.copy();obj.parent=None;obj.matrix_world=world
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.object.select_all(action='DESELECT')
 for obj in selected:obj.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=False,export_extras=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_nla_strips_merged_animation_name='Swim_Loop',export_frame_range=True,export_force_sampling=True,export_texcoords=False)
 for obj,parent,basis,data in saved:
  temporary=obj.data;obj.data=data;obj.parent=parent;obj.matrix_basis=basis;bpy.data.meshes.remove(temporary)
 bpy.context.view_layer.update()

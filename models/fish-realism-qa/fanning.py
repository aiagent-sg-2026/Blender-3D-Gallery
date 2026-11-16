"""Retarget existing fin controls for restrained, repeated hovering strokes."""
import math

def retarget_fanning(rig,config,profile=None):
 if not config.get('fanning_cycles'):return
 cycles=int(config['fanning_cycles']);gain=float(config.get('fanning_gain',1));assert 1<=cycles<=6 and 0<gain<=5
 phases={'Dorsal':0,'Anal':.7,'Pectoral_L':1.4,'Pectoral_R':2.1};selected=config.get('fanning_bones',list(phases));action=rig.animation_data.action;start,end=action.frame_range
 local_hinges=config.get('fanning_local_hinges',False)
 if local_hinges:
  import bpy
  from mathutils import Vector
  assert profile is not None
  bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
  for name in selected:
   bone=rig.data.edit_bones[name]
   if name in ['Dorsal','Anal']:
    x=(config.get('dorsal_second_start',config['dorsal_split'])+config['dorsal_end'])/2 if name=='Dorsal' else (config['anal_start']+config['anal_end'])/2
    z=profile(x)[0 if name=='Dorsal' else 1];head=Vector((x,0,z));axis=Vector((.22,0,0))
   else:
    x=config['gill_x']+.10;z=config.get('pectoral_root_z',-.05);hi,lo,width=profile(x);q=max(-.999,min(.999,(2*z-hi-lo)/(hi-lo)));side=1 if name.endswith('_L') else -1;head=Vector((x,side*(width*math.sqrt(1-q*q)+.001),z));axis=Vector((0,0,.20))
   bone.head=head;bone.tail=head+axis;bone.parent=min((b for b in rig.data.edit_bones if b.name.startswith('Spine_')),key=lambda b:abs(b.head.x-x))
  bpy.ops.object.mode_set(mode='OBJECT')
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     name=next((name for name in selected if ('["'+name+'"]') in curve.data_path),None)
     if name is None or not curve.data_path.endswith('rotation_euler'):continue
     amplitude=((.065 if curve.array_index==1 else .010 if curve.array_index==2 else 0) if local_hinges else (.065 if curve.array_index==0 else .035 if curve.array_index==2 else 0))*gain
     for key in curve.keyframe_points:
      key.co.y=amplitude*math.sin(2*math.pi*cycles*(key.co.x-start)/(end-start)+phases[name]);key.handle_left_type='AUTO';key.handle_right_type='AUTO'
     curve.update()

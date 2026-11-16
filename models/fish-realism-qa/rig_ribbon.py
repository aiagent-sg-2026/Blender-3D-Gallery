"""Weight a ribbonfish body and its independently travelling dorsal-fin wave."""
import bpy,bisect,math

def bind_ribbon(B,profile):
 meshes=[o for o in B.ROOT.children_recursive if o.type=='MESH'];data=bpy.data.armatures.new('RibbonSwimSkeleton');rig=bpy.data.objects.new('RibbonSwimRig',data);bpy.context.scene.collection.objects.link(rig);rig.parent=B.ROOT;bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 xs=[-1.65+i*3.70/18 for i in range(19)];names=[]
 for i,x in enumerate(xs):
  name='Spine_%02d'%i;bone=data.edit_bones.new(name);bone.head=(x,0,0);bone.tail=(xs[i+1] if i<18 else x+.20,0,0)
  if i:bone.parent=data.edit_bones[names[-1]];bone.use_connect=True
  names.append(name)
 fin_xs=[-1.24+i*3.28/12 for i in range(13)];wave=[]
 for i,x in enumerate(fin_xs):
  name='DorsalWave_%02d'%i;bone=data.edit_bones.new(name);z=profile(x)[0];bone.head=(x,0,z);bone.tail=(x,0,z+.07);bone.parent=data.edit_bones[names[max(0,min(18,bisect.bisect_right(xs,x)-1))]];wave.append(name)
 for side in [-1,1]:
  bone=data.edit_bones.new('Pectoral_L' if side>0 else 'Pectoral_R');bone.head=(-1.13,side*.025,-.025);bone.tail=(-.93,side*.06,-.06);bone.parent=data.edit_bones[names[2]]
 bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
 def interpolation(points,names,x):
  i=max(0,min(len(points)-2,bisect.bisect_right(points,x)-1));t=max(0,min(1,(x-points[i])/(points[i+1]-points[i])));return {names[i]:1-t,names[i+1]:t}
 for obj in meshes:
  groups={bone.name:obj.vertex_groups.new(name=bone.name) for bone in data.bones};spans=[0.0]*len(obj.data.vertices)
  if obj.data.uv_layers.active:
   for loop in obj.data.loops:spans[loop.vertex_index]=float(obj.data.uv_layers.active.data[loop.index].uv.y)
  role=obj.get('deform_role')
  for vertex,span in zip(obj.data.vertices,spans):
   p=obj.matrix_local@vertex.co;weights=interpolation(xs,names,p.x);blend=.90*max(0,min(1,span))**1.4 if role in ['dorsal','pectoral'] else 0
   if blend:
    weights={k:v*(1-blend) for k,v in weights.items()};extra=interpolation(fin_xs,wave,p.x) if role=='dorsal' else {'Pectoral_L' if p.y>0 else 'Pectoral_R':1}
    for name,weight in extra.items():weights[name]=weights.get(name,0)+blend*weight
   for name,weight in weights.items():
    if weight>1e-7:groups[name].add([vertex.index],weight,'REPLACE')
  modifier=obj.modifiers.new('RibbonBodyAndFinWave','ARMATURE');modifier.object=rig
  if role in ['dorsal','pectoral']:obj['fin_root_anchor']='Body spine weights at span=0; dorsal wave and pectoral motion feather toward tips'
 scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=73
 for frame in range(1,74,2):
  phase=2*math.pi*(frame-1)/72
  for i,name in enumerate(names):
   pose=rig.pose.bones[name];pose.rotation_mode='XYZ';amplitude=0 if i<3 else .050*(i/18)**1.8;pose.rotation_euler=(0,0,amplitude*math.sin(phase-i*.45));pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
  for i,name in enumerate(wave):
   pose=rig.pose.bones[name];pose.rotation_mode='XYZ';pose.rotation_euler=(.40*math.sin(phase-i*.75)+.05*math.sin(2*phase-i*1.35),0,0);pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
  for side,name in [(-1,'Pectoral_R'),(1,'Pectoral_L')]:
   pose=rig.pose.bones[name];pose.rotation_mode='XYZ';pose.rotation_euler=(.065*math.sin(phase+side*.8),0,.03*math.sin(phase+side*.8));pose.keyframe_insert(data_path='rotation_euler',frame=frame,group=name)
 rig.animation_data.action.name='Swim_Loop';scene.frame_set(13);return rig

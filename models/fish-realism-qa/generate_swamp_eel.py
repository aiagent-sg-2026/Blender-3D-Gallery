"""Author a scaleless swamp eel with a tapered body and travelling axial motion."""
import bpy,math,json,importlib.util,bisect
import numpy as np
from pathlib import Path
HERE=Path(__file__).resolve().parent;SLUG='swamp-eel';C=json.loads((HERE/'profiles.json').read_text())[SLUG];OUT=HERE/SLUG;OUT.mkdir(exist_ok=True);TEX=OUT/'textures';TEX.mkdir(exist_ok=True);PI=math.pi
spec=importlib.util.spec_from_file_location('eel_surface_utils',HERE.parent/'fish-realism-review/revision-02/create_review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R);B=R.B
def profile(x):return [B.interp(list(zip(C['profile_x'],C[k])),x) for k in ['top','bottom','width']]
def flank(x,z,side):
 hi,lo,w=profile(x);q=max(-.999,min(.999,(2*z-hi-lo)/(hi-lo)));return side*w*math.sqrt(1-q*q)
def surfaces():
 u,v=np.meshgrid(np.linspace(0,1,2048),np.linspace(0,1,512));z=np.sin(v*2*PI);coarse=R.noise(u,v,47,15,1501);micro=R.noise(u,v,560,230,1502);fine=R.noise(u,v,1100,460,1503)
 a=R.smoothstep(.10,.93,z)[...,None];color=np.array(C['side_color'])*(1-a)+np.array(C['back_color'])*a;a=R.smoothstep(.10,.92,-z)[...,None];color=color*(1-a)+np.array(C['belly_color'])*a;color+=(coarse-.5)[...,None]*.035+(micro-.5)[...,None]*.024
 flecks=R.smoothstep(.72,.90,micro)*.035;color+=flecks[...,None];xs=-1.65+3.70*u;hi=np.interp(xs,C['profile_x'],C['top']);lo=np.interp(xs,C['profile_x'],C['bottom']);world_z=(hi+lo)/2+(hi-lo)/2*z
 mouth_z=-.006-.025*np.clip((xs+1.65)/.18,0,1);mouth=np.exp(-((world_z-mouth_z)/.0013)**2)*(1-R.smoothstep(-1.49,-1.46,xs))*np.abs(np.cos(v*2*PI))**.6
 gill=np.exp(-((xs-(-1.35+.045*np.abs(np.cos(v*2*PI))))/.0025)**2)*(1-R.smoothstep(-.98,-.80,z));color*=1-np.maximum(mouth,gill)[...,None]*.40
 height=(micro-.5)*.000025+(fine-.5)*.000012;gy,gx=np.gradient(height,1.3/511,3.7/2047);normal=np.stack((-gx,-gy,np.ones_like(height)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 images={key:R.image_file('Eel_Scaleless_'+key,data,TEX,key!='color') for key,data in [('color',np.clip(color,0,1)),('normal',normal*.5+.5),('rough',.44+(coarse-.5)*.10+(fine-.5)*.035)]};mat=R.maps_material('Eel_ScalelessSkin',images,.0,.44);mat.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.025;return mat
def body(mat):
 vertices=[];uv=[];faces=[];nx=320;na=64
 for i in range(nx+1):
  x=-1.65+3.7*i/nx;hi,lo,w=profile(x)
  for j in range(na):a=2*PI*j/na;vertices.append((x,w*math.cos(a),(hi+lo)/2+(hi-lo)/2*math.sin(a)));uv.append((i/nx,j/na))
 for i in range(nx):
  for j in range(na):a=i*na+j;b=i*na+(j+1)%na;faces.append((a,b,b+na,a+na))
 # A hemispherical snout keeps the head blunt instead of ending like a pencil.
 previous=list(range(na));hi,lo,w=profile(-1.65)
 for radius in [.82,.55,.25]:
  current=[]
  for j in range(na):
   angle=2*PI*j/na;current.append(len(vertices));vertices.append((-1.65-.035*math.sqrt(1-radius*radius),w*radius*math.cos(angle),(hi+lo)/2+(hi-lo)/2*radius*math.sin(angle)));uv.append((.015*(1-radius),j/na))
  for j in range(na):faces.append((previous[(j+1)%na],previous[j],current[j],current[(j+1)%na]))
  previous=current
 center=len(vertices);vertices.append((-1.685,0,(hi+lo)/2));uv.append((.02,.5))
 for j in range(na):faces.append((previous[(j+1)%na],previous[j],center))
 faces.append(tuple(nx*na+j for j in range(na)));obj=B.mesh('Skin_AnatomicalProfile',vertices,faces,mat,uv)
 for polygon in obj.data.polygons:
  if len(polygon.vertices)>4:
   for loop in polygon.loop_indices:
    p=obj.data.vertices[obj.data.loops[loop].vertex_index].co;obj.data.uv_layers.active.data[loop].uv=(.035+.08*p.y,.50+.12*p.z)
  elif any(v%na==na-1 for v in polygon.vertices) and any(v%na==0 for v in polygon.vertices):
   for loop in polygon.loop_indices:
    if obj.data.loops[loop].vertex_index%na==0:obj.data.uv_layers.active.data[loop].uv.y=1
 return obj
def eyes():
 u,v=np.meshgrid(np.linspace(-1,1,256),np.linspace(-1,1,256));d=np.sqrt(u*u+v*v);a=np.arctan2(v,u);color=np.zeros((*d.shape,3))+np.array([.24,.16,.075]);color+=(np.sin(a*93+d*19)*.015)[...,None];pupil=1-R.smoothstep(.73,.79,d);color=color*(1-pupil[...,None])+np.array([.001,.002,.002])*pupil[...,None];mat=R.maps_material('Eel_SmallIris',{'color':R.image_file('Eel_Iris',np.clip(color,0,1),TEX)},.0,.30);mat.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=0;mat.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.16;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.36
 for side in [-1,1]:
  x,z,r=-1.54,.029,.008;vertices=[];uv=[];faces=[];nr=10;na=48
  for ring in range(nr+1):
   t=max(.00001,ring/nr)
   for j in range(na):a=2*PI*j/na;xx=x+r*t*math.cos(a);zz=z+r*t*math.sin(a);vertices.append((xx,flank(xx,zz,side)+side*(.0003+.0012*(1-t*t)),zz));uv.append((.5+.5*t*math.cos(a),.5+.5*t*math.sin(a)))
  for ring in range(nr):
   for j in range(na):a=ring*na+j;b=ring*na+(j+1)%na;face=(a,a+na,b+na,b);faces.append(face if side>0 else face[::-1])
  B.mesh('Eye_EmbeddedIris_'+str(side),vertices,faces,mat,uv)
def rig_body():
 data=bpy.data.armatures.new('Eel_AxialSkeleton');rig=bpy.data.objects.new('Swim_Armature',data);bpy.context.scene.collection.objects.link(rig);rig.parent=B.ROOT;xs=[-1.75+3.90*i/24 for i in range(25)];bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for i,x in enumerate(xs):
  bone=data.edit_bones.new('Spine_%02d'%i);bone.head=(x,0,0);bone.tail=(xs[i+1] if i<24 else x+.16,0,0)
  if i:bone.parent=data.edit_bones['Spine_%02d'%(i-1)]
 bpy.ops.object.mode_set(mode='OBJECT')
 for obj in [o for o in B.ROOT.children_recursive if o.type=='MESH']:
  groups=[obj.vertex_groups.new(name='Spine_%02d'%i) for i in range(25)]
  for vertex in obj.data.vertices:
   i=max(0,min(23,bisect.bisect_right(xs,vertex.co.x)-1));f=max(0,min(1,(vertex.co.x-xs[i])/(xs[i+1]-xs[i])));groups[i].add([vertex.index],1-f,'REPLACE');groups[i+1].add([vertex.index],f,'REPLACE')
  mod=obj.modifiers.new('Eel_AxialDeformation','ARMATURE');mod.object=rig
 scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=73
 for frame in range(1,74,2):
  phase=2*PI*(frame-1)/72
  for i in range(25):
   bone=rig.pose.bones['Spine_%02d'%i];bone.rotation_mode='XYZ';progress=i/24;bone.rotation_euler=(0,0,(.009+.070*progress**1.5*C.get('axial_wave_gain',1))*math.sin(phase-i*.44));bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=bone.name)
 rig.animation_data.action.name='Swim_Loop';scene.frame_set(1);return rig
bpy.ops.wm.read_factory_settings(use_empty=True);B.ROOT=bpy.data.objects.new('ASSET_PhotoInformed_swamp-eel',None);bpy.context.scene.collection.objects.link(B.ROOT);B.SLUG=SLUG;body(surfaces());eyes();rig_body()
spec=importlib.util.spec_from_file_location('eel_studio',HERE.parent/'fish-realism-review/revision-03/create_review.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);scene=P.studio(OUT);scene.render.engine='BLENDER_EEVEE';scene.camera.location=(-.05,-5,6.5);P.aim(scene.camera,(.15,0,0));scene.camera.data.ortho_scale=4.5;scene.frame_set(13);scene.frame_end=73
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'swamp-eel.blend'));bpy.ops.render.render(write_still=True);scene.camera.location=(-1.50,-4,.65);P.aim(scene.camera,(-1.46,0,.01));scene.camera.data.ortho_scale=.65;scene.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True);print('GENERATED swamp-eel',flush=True)

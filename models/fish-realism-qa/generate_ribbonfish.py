"""Author a scaleless ribbonfish with real open jaws and travelling dorsal motion."""
import bpy,bmesh,math,json,sys,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;SLUG='ribbonfish';OUT=HERE/SLUG;OUT.mkdir(exist_ok=True);TEX=OUT/'textures';TEX.mkdir(exist_ok=True);PI=math.pi
spec=importlib.util.spec_from_file_location('ribbon_surface_utils',HERE.parent/'fish-realism-review/revision-02/create_review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R);B=R.B
X=[-1.65,-1.50,-1.30,-1.18,-.90,-.40,.15,.65,1.1,1.5,1.82,2.05]
TOP=[.026,.085,.105,.108,.112,.105,.087,.064,.042,.020,.008,.0007]
BOTTOM=[-.026,-.067,-.108,-.118,-.122,-.115,-.095,-.072,-.048,-.024,-.009,-.0007]
WIDTH=[.005,.018,.027,.029,.026,.021,.016,.011,.007,.004,.0017,.0004]
def profile(x):return [B.interp(list(zip(X,values)),x) for values in [TOP,BOTTOM,WIDTH]]
def jaw_gap(x):
 t=max(0,min(1,(x+1.65)/.47));return .032*(.65+.35*math.sin(PI*t))*(1-R.smoothstep(-1.38,-1.18,x))
def normal_map(h,sx,sy):
 gy,gx=np.gradient(h,sy/(h.shape[0]-1),sx/(h.shape[1]-1));n=np.stack((-gx,-gy,np.ones_like(h)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return n*.5+.5

def surfaces():
 u,v=np.meshgrid(np.linspace(0,1,2048),np.linspace(0,1,512));z=np.sin(v*2*PI);coarse=R.noise(u,v,32,10,1401);grain=R.noise(u,v,520,240,1402);smear=R.noise(u,v,210,7,1403)
 color=np.zeros((*u.shape,3))+np.array([.65,.69,.70]);back=R.smoothstep(.45,.98,z);belly=R.smoothstep(.10,.9,-z);color=color*(1-back[...,None])+np.array([.30,.35,.36])*back[...,None];color=color*(1-belly[...,None])+np.array([.80,.81,.80])*belly[...,None];color+=(coarse-.5)[...,None]*.09+(smear-.5)[...,None]*.018+(grain-.5)[...,None]*.012
 xs=-1.65+3.70*u;gill=np.exp(-((xs+1.20+.12*((z+.04)/.95)**2)/.004)**2)*(1-R.smoothstep(.72,.96,np.abs(z)));color*=1-gill[...,None]*.36
 height=(grain-.5)*.000018+(smear-.5)*.000008;rough=.28+(coarse-.5)*.18+(grain-.5)*.025
 images={k:R.image_file('Ribbon_Scaleless_'+k,im,TEX,k!='color') for k,im in [('color',np.clip(color,0,1)),('normal',normal_map(height,3.7,.65)),('rough',rough)]};skin=R.maps_material('Ribbon_SteelySilverSkin',images,.22,.28);p=skin.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.53;p.inputs['Coat Weight'].default_value=.015
 fu,fv=np.meshgrid(np.linspace(0,1,1024),np.linspace(0,1,512));grain=R.noise(fu,fv,310,180,1405);rays=np.exp(-(np.sin(PI*(fu*132+.08*np.sin(fu*23)))/.18)**2);col=np.zeros((*fu.shape,3))+np.array([.53,.59,.59]);col+=(grain-.5)[...,None]*.025+rays[...,None]*.045;col*=1-.54*np.exp(-((fu-.035)/.028)**2)[...,None];fin=R.maps_material('Ribbon_FineDorsalMembrane',{'color':R.image_file('Ribbon_Fin_color',col,TEX),'normal':R.image_file('Ribbon_Fin_normal',normal_map(rays*.00008,3.28,.05),TEX,True)},.02,.44);p=fin.node_tree.nodes['Principled BSDF'];p.inputs['Alpha'].default_value=.77;fin.surface_render_method='DITHERED'
 return skin,fin

def strip(name,x0,x1,n,na,mat,half=None):
 vertices=[];faces=[];uv=[]
 for i in range(n+1):
  x=x0+(x1-x0)*i/n;hi,lo,w=profile(x);gap=jaw_gap(x)
  if half=='lower' and x< -1.65:
   t=max(0,min(1,(x+1.665)/.015));w*=.08+.92*t;lo=-.0135+(-.026+.0135)*t;hi=.026

  for j in range(na+1):
   angle=(PI*j/na if half=='upper' else PI+PI*j/na if half=='lower' else 2*PI*j/na)
   center=(hi+lo)/2;z=center+gap/2+(hi-center-gap/2)*math.sin(angle) if half=='upper' else center-gap/2+(center-gap/2-lo)*math.sin(angle) if half=='lower' else (hi+lo)/2+(hi-lo)/2*math.sin(angle)
   vertices.append((x,w*math.cos(angle),z));uv.append(((x+1.65)/3.70,angle/(2*PI)))
 for i in range(n):
  for j in range(na):a=i*(na+1)+j;faces.append((a,a+1,a+na+2,a+na+1))
 faces.extend([tuple(range(na,-1,-1)),tuple(n*(na+1)+j for j in range(na+1))]);return B.mesh(name,vertices,faces,mat,uv)

def mouth():
 dark=B.material('Ribbon_MouthInterior',(.012,.017,.021),.69);ivory=B.material('Ribbon_BarbedFangs',(.73,.73,.62),.33)
 for side in [-1,1]:
  vertices=[];uv=[]
  for i in range(31):
   x=-1.65+.47*i/30;hi,lo,w=profile(x);gap=jaw_gap(x);mid=(hi+lo)/2;vertices.extend([(x,side*w*.70,mid-gap*.47),(x,side*w*.70,mid+gap*.47)]);uv.extend([(i/30,0),(i/30,1)])
  B.mesh('Ribbon_RecessedMouth_'+str(side),vertices,[tuple(reversed((2*i,2*i+2,2*i+3,2*i+1))) if side>0 else (2*i,2*i+2,2*i+3,2*i+1) for i in range(30)],dark,uv)
  for upper,teeth in [(True,[(-1.60,.022),(-1.54,.032),(-1.46,.016),(-1.38,.010)]),(False,[(-1.57,.017),(-1.49,.012),(-1.41,.009)])]:
   for index,(x,length) in enumerate(teeth):
    w=profile(x)[2];gap=jaw_gap(x);sign=-1 if upper else 1;hi,lo,_=profile(x);z=(hi+lo)/2+(gap*.49 if upper else -gap*.49);vertices=[];uv=[]
    for ring in range(3):
     t=ring/2;radius=.0024*(1-t*.94)
     for j in range(8):
      a=2*PI*j/8;vertices.append((x+.004*t+radius*math.cos(a),side*w*.74+radius*math.sin(a),z+sign*length*t));uv.append((j/8,t))
    faces=[]
    for ring in range(2):
     for j in range(8):a=ring*8+j;b=ring*8+(j+1)%8;faces.append((a,b,b+8,a+8))
    faces.extend([tuple(range(7,-1,-1)),tuple(16+j for j in range(8))]);faces=[tuple(reversed(f)) for f in faces] if upper else faces;B.mesh('Ribbon_Fang_%s_%s_%d'%(side,upper,index),vertices,faces,ivory,uv)

def eyes():
 u,v=np.meshgrid(np.linspace(-1,1,512),np.linspace(-1,1,512));r=np.sqrt(u*u+v*v);a=np.arctan2(v,u);color=np.zeros((*u.shape,3))+np.array([.57,.58,.53]);color+=(.028*np.sin(a*133+r*31))[...,None];pupil=1-R.smoothstep(.68,.73,r);color=color*(1-pupil[...,None])+np.array([.001,.002,.003])*pupil[...,None];mat=R.maps_material('Ribbon_TexturedIris',{'color':R.image_file('Ribbon_Iris',color,TEX)},.01,.24);mat.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.12
 for side in [-1,1]:
  vertices=[];uv=[];faces=[];x,z,radius=-1.49,.055,.026
  for ring in range(13):
   t=max(.00001,ring/12)
   for j in range(64):
    a=2*PI*j/64;xx=x+radius*t*math.cos(a);zz=z+radius*t*math.sin(a);hi,lo,w=profile(xx);q=max(-.99,min(.99,(2*zz-hi-lo)/(hi-lo)));yy=side*(w*math.sqrt(1-q*q)+.0006+.003*(1-t*t));vertices.append((xx,yy,zz));uv.append((.5+.5*t*math.cos(a),.5+.5*t*math.sin(a)))
  for ring in range(12):
   for j in range(64):a=ring*64+j;b=ring*64+(j+1)%64;face=(a,a+64,b+64,b);faces.append(face[::-1] if side>0 else face)
  B.mesh('Eye_EmbeddedIris_'+str(side),vertices,faces,mat,uv)

def membrane(name,root,edge,mat,n,m,role):
 vertices=[];uv=[];faces=[]
 for i in range(n+1):
  u=i/n;a=Vector(root(u));b=Vector(edge(u))
  for j in range(m+1):
   t=j/m;p=a.lerp(b,t);p.y+=.0013*t*t*math.sin(u*PI*53);p.z+=.001*t**4*math.sin(u*PI*264);vertices.append(tuple(p));uv.append((u,t))
 for i in range(n):
  for j in range(m):a=i*(m+1)+j;faces.append((a,a+m+1,a+m+2,a+1))
 return B.mesh(name,vertices,faces,mat,uv,deform=role)

bpy.ops.wm.read_factory_settings(use_empty=True);B.ROOT=bpy.data.objects.new('ASSET_PhotoInformed_ribbonfish',None);bpy.context.scene.collection.objects.link(B.ROOT);B.SLUG=SLUG
skin,fin=surfaces();body=strip('Ribbon_ContinuousBody',-1.18,2.05,280,48,skin);upper=strip('Skin_UpperJaw',-1.65,-1.18,64,24,skin,'upper');lower=strip('Skin_LowerJaw',-1.665,-1.18,64,24,skin,'lower')
# Weld the real jaw/body boundary; internal cap normals previously left a
# mechanical-looking transverse seam behind the operculum.
bpy.ops.object.select_all(action='DESELECT')
for obj in [body,upper,lower]:obj.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join();bm=bmesh.new();bm.from_mesh(body.data)
caps=[f for f in bm.faces if all(abs(v.co.x+1.18)<1e-6 for v in f.verts)]
bmesh.ops.delete(bm,geom=caps,context='FACES_ONLY');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update();bm.to_mesh(body.data);bm.free();body.data.update();mouth();eyes()
membrane('Dorsal_ContinuousWaveMembrane',lambda u:(-1.24+3.28*u,0,profile(-1.24+3.28*u)[0]),lambda u:(-1.24+3.28*u,0,profile(-1.24+3.28*u)[0]+.0004+.085*(1-.70*u)*R.smoothstep(0,.035,u)*(1-R.smoothstep(.86,1,u))),fin,300,18,'dorsal')
for side in [-1,1]:membrane('Pectoral_'+str(side),lambda u:(-1.13,side*.027,-.015+(u-.5)*.016),lambda u:(-.94+.06*u,side*(.031+.015*math.sin(PI*u)),-.035-.025*math.sin(PI*u)),fin,52,14,'pectoral')
sys.path.insert(0,str(HERE));from rig_ribbon import bind_ribbon
bind_ribbon(B,profile)
spec=importlib.util.spec_from_file_location('ribbon_studio',HERE.parent/'fish-realism-review/revision-03/create_review.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);s=P.studio(OUT);s.camera.data.ortho_scale=4.5;s.camera.location=(-.05,-7,2.5);P.aim(s.camera,(.20,0,0));s.frame_set(13);s.frame_end=73
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ribbonfish.blend'));bpy.ops.render.render(write_still=True)
s.camera.location=(-1.43,-6,1);P.aim(s.camera,(-1.40,0,.015));s.camera.data.ortho_scale=.80;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True)
s.camera.location=(.35,-4,1.6);P.aim(s.camera,(.35,0,.09));s.camera.data.ortho_scale=1.7;s.render.filepath=str(OUT/'dorsal-detail.png');s.frame_set(19);bpy.ops.render.render(write_still=True)
print('GENERATED ribbonfish',flush=True)

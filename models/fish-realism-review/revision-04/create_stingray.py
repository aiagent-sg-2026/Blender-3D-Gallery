"""Photo-informed maskray rebuild. Writes only revision-04/stingray."""
import bpy,math,json,sys,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;OUT=HERE/'stingray';OUT.mkdir(exist_ok=True);TEX=OUT/'textures';TEX.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('texture_helpers',HERE.parent/'revision-02'/'create_review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
PI=math.pi

def smooth(a,b,x):return R.smoothstep(a,b,x)
def material(name,color,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Specular IOR Level'].default_value=.27;return m

def mesh(name,verts,faces,mat,uv=None):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.parent=ROOT;d.materials.append(mat)
 for p in d.polygons:p.use_smooth=True
 if uv is not None:
  l=d.uv_layers.new(name='UVMap')
  for p in d.polygons:
   for i in p.loop_indices:l.data[i].uv=uv[d.loops[i].vertex_index]
 return o

def mapped(name,images,rough=.55):
 m=material(name,(.2,.16,.1),rough);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for key,img in images.items():
  t=n.new('ShaderNodeTexImage');t.image=img
  if key=='color':l.new(t.outputs['Color'],p.inputs['Base Color'])
  elif key=='rough':l.new(t.outputs['Color'],p.inputs['Roughness'])
  elif key=='normal':
   b=n.new('ShaderNodeNormalMap');b.inputs['Strength'].default_value=.65;l.new(t.outputs['Color'],b.inputs['Color']);l.new(b.outputs['Normal'],p.inputs['Normal'])
 return m

def textures():
 if '--reuse-textures' in sys.argv:
  result={}
  for key,name in [('color','Maskray_PigmentAndPores'),('normal','Maskray_DermalNormal'),('rough','Maskray_RoughnessVariation')]:
   im=bpy.data.images.load(str(TEX/(name+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if key=='color' else 'Non-Color';im.pack();result[key]=im
  return result
 n=2048;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));x=-1.30+2.55*u;y=-1.35+2.70*v
 coarse=R.noise(u,v,10,12,711);mottle=R.noise(u,v,74,80,712);grain=R.noise(u,v,720,760,713);fine=R.noise(u,v,1500,1420,714)
 color=np.zeros((n,n,3))+np.array([.22,.181,.116]);color+=(coarse-.5)[...,None]*np.array([.055,.047,.028])+(mottle-.5)[...,None]*.030
 # Broad mask pigment surrounds the eye/spiracle area; no painted geometric seam.
 mask=np.exp(-((x+.64)/.27)**4-((np.abs(y)-.22)/.16)**4);color*=1-mask[...,None]*(.12+.10*mottle[...,None])
 pores=smooth(.61,.83,grain)*smooth(.40,.67,mottle);color*=1-pores[...,None]*.22
 color+=(grain-.5)[...,None]*.018+(fine-.5)[...,None]*.010
 rng=np.random.default_rng(718);points=[]
 for k in range(400):
  px,py=rng.uniform(-1.10,.88),rng.uniform(-1.13,1.13)
  if (px/1.22)**2+(py/1.29)**2>.88 or ((px+.66)/.40)**2+(py/.48)**2<1:continue
  if any((px-a)**2+(py-b)**2<.014 for a,b in points):continue
  points.append((px,py));radius=rng.uniform(.018,.047);ratio=rng.uniform(.75,1.3);ang=rng.uniform(-PI,PI)
  extent=radius*2.0;x0=max(0,int((px-extent+1.30)/2.55*n));x1=min(n,int((px+extent+1.30)/2.55*n)+2);y0=max(0,int((py-extent+1.35)/2.70*n));y1=min(n,int((py+extent+1.35)/2.70*n)+2)
  xx=x[y0:y1,x0:x1];yy=y[y0:y1,x0:x1];dx=(xx-px)*math.cos(ang)+(yy-py)*math.sin(ang);dy=-(xx-px)*math.sin(ang)+(yy-py)*math.cos(ang)
  d=np.sqrt((dx/ratio)**2+(dy*ratio)**2);edge=radius*(1+.045*np.sin(np.arctan2(dy,dx)*5+k));local=color[y0:y1,x0:x1]
  halo=1-smooth(edge*1.0,edge*1.45,d);local*=1-halo[...,None]*.28
  a=1-smooth(edge*.75,edge*1.10,d);pigment=np.array([.016,.22,.33])*rng.uniform(.75,1.2);center=(1-smooth(0,edge*.85,d))*.22
  target=pigment[None,None,:]*(1+center[...,None])+(fine[y0:y1,x0:x1]-.5)[...,None]*.012;color[y0:y1,x0:x1]=local*(1-a[...,None])+target*a[...,None]
 # Derivatives use physical UV spacing. Earlier drafts differentiated in pixels,
 # producing near-flat normals even when a detailed height map was present.
 height=(grain-.5)*.00065+(fine-.5)*.00016+(mottle-.5)*.00055
 gy,gx=np.gradient(height,2.70/(n-1),2.55/(n-1));normal=np.stack((-gx,-gy,np.ones_like(gx)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 rough=np.clip(.48+(coarse-.5)*.12+(grain-.5)*.10+pores*.07,.36,.68)
 return {key:R.image_file(name,arr,TEX,key!='color') for key,name,arr in [('color','Maskray_PigmentAndPores',np.clip(color,0,1)),('normal','Maskray_DermalNormal',normal*.5+.5),('rough','Maskray_RoughnessVariation',rough)]}

def width(x):
 xs=[-1.21,-1.11,-.86,-.50,-.08,.23,.55,.82,1.03];ys=[.008,.27,.59,.91,1.24,1.13,.85,.47,.012]
 return max(.005,R.B.interp(list(zip(xs,ys)),x))

def surface(x,y,bottom=False):
 w=width(x);s=min(1,abs(y)/max(w,.001));trunk=math.exp(-((x+.20)/.68)**2-(y/.32)**2)
 z=.012+.030*(1-s*s)+.135*trunk
 # Orbital tissue belongs to the continuous skin, rather than a ball sitting on it.
 z+=.115*math.exp(-((x+.69)/.15)**2-((abs(y)-.235)/.115)**2)
 # Open spiracles are sculpted as bowls behind each eye.
 z-=.070*math.exp(-((x+.43)/.105)**4-((abs(y)-.25)/.061)**4)
 z+=.012*s**4*math.sin(x*4.1+y*2.1)
 z+=.015*math.exp(-((x-.78)/.27)**2-(y/.13)**2)
 if bottom:z=-.012-.062*trunk-.008*(1-s*s)+.012*s**4*math.sin(x*4.1+y*2.1)
 return z

def body(skin,belly):
 nx,ny=164,144;verts=[];uv=[];faces=[]
 for bottom in [False,True]:
  for i in range(nx+1):
   x=-1.21+2.24*i/nx;w=width(x)
   for j in range(ny+1):
    y=w*(-1+2*j/ny);verts.append((x,y,surface(x,y,bottom)));uv.append(((x+1.30)/2.55,(y+1.35)/2.70))
 count=(nx+1)*(ny+1)
 for side in [0,1]:
  off=side*count
  for i in range(nx):
   for j in range(ny):
    a=off+i*(ny+1)+j;f=(a,a+ny+1,a+ny+2,a+1)
    cx=sum(verts[k][0] for k in f)/4;cy=sum(verts[k][1] for k in f)/4
    if side==0 and ((cx+.43)/.069)**2+((abs(cy)-.25)/.034)**2<1:continue
    faces.append(f[::-1] if side else f)
  if side==0:topfaces=len(faces)
 bottomfaces=len(faces)-topfaces
 for j in [0,ny]:
  for i in range(nx):a=i*(ny+1)+j;b=a+ny+1;faces.append((a,a+count,b+count,b))
 for i in [0,nx]:
  for j in range(ny):a=i*(ny+1)+j;faces.append((a,a+1,a+1+count,a+count))
 o=mesh('Maskray_ContinuousDisc',verts,faces,skin,uv);o.data.materials.append(belly)
 for p in o.data.polygons:
  if topfaces<=p.index<topfaces+bottomfaces:p.material_index=1
 return o

def iris_material():
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));x=2*u-1;y=2*v-1;d=np.sqrt(x*x+y*y);a=np.arctan2(y,x)
 grain=R.noise(u,v,210,220,801);radial=.5+.25*np.sin(a*131+d*22)+.15*np.sin(a*83-d*36)
 c=np.zeros((n,n,3))+np.array([.20,.16,.070]);c+=(radial-.5)[...,None]*np.array([.10,.085,.035])+(grain-.5)[...,None]*.06
 c*=1-smooth(.73,1,d)[...,None]*.45
 # U-shaped pupil with a central iris operculum, as in the inspected eye macro.
 r=np.sqrt((x/.68)**2+((y-.03)/.70)**2);inner=np.sqrt((x/.40)**2+((y-.21)/.56)**2)
 pupil=(1-smooth(.95,1.02,r))*smooth(.85,1.05,inner)*(1-smooth(.36,.58,y))
 c=c*(1-pupil[...,None])+np.array([.001,.002,.001])*pupil[...,None]
 im=R.image_file('Maskray_IrisWithOperculum',np.clip(c,0,1),TEX);m=mapped('Maskray_NaturalIris',{'color':im},.32);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Coat Weight'].default_value=.06;p.inputs['Coat Roughness'].default_value=.16;return m

def eye(side,skin,iris):
 center=Vector((-.70,side*.255,.185));u=Vector((1,0,0));normal=Vector((0,side*.50,.866));v=normal.cross(u);rings=14;around=80;verts=[];uv=[];faces=[]
 for j in range(rings+1):
  r=max(.00001,j/rings)
  for i in range(around):
   a=i*2*PI/around;q=center+u*(.078*r*math.cos(a))+v*(.049*r*math.sin(a))+normal*(.024*(1-r*r));q.z=surface(q.x,q.y)+.016*(1-r*r)+.0015;verts.append(q);uv.append((.5+.5*r*math.cos(a),.5+.5*r*math.sin(a)))
 for j in range(rings):
  for i in range(around):a=j*around+i;b=j*around+(i+1)%around;faces.append((a,a+around,b+around,b))
 o=mesh('Maskray_Iris_'+str(side),verts,faces,iris,uv)


def spiracles(side,skin,cavity):
 # Recess lining lies within the sculpted skin bowl and has a visibly fleshy lip.
 verts=[];uv=[];faces=[];n=72;m=12
 for j in range(m+1):
  r=max(.0001,j/m)
  for i in range(n):
   a=2*PI*i/n;x=-.43+.075*r*math.cos(a);y=side*(.25+.038*r*math.sin(a));z=surface(x,y)-.001
   verts.append((x,y,z));uv.append(((x+1.30)/2.55,(y+1.35)/2.70))
 for j in range(m):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
 mesh('Maskray_RecessedSpiracle_'+str(side),verts,faces,cavity,uv)
 # A continuous smooth lip covers the grid cut boundary and leaves a rounded opening.
 verts=[];uv=[];faces=[]
 for j in range(9):
  t=j/8;r=.59+.72*t
  for i in range(n):
   a=2*PI*i/n;x=-.43+.069*r*math.cos(a);y=side*(.25+.034*r*math.sin(a));z=surface(x,y)+.0015+.004*math.sin(PI*t)
   verts.append((x,y,z));uv.append(((x+1.30)/2.55,(y+1.35)/2.70))
 for j in range(8):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
 mesh('Maskray_SoftSpiracleLip_'+str(side),verts,faces,skin,uv)


def tail(skin):
 verts=[];uv=[];faces=[];n=160;m=24
 for i in range(n+1):
  t=i/n;x=.77+2.85*t;y=.17*math.sin(t*PI*1.45);z=.025-.095*t+.025*math.sin(PI*t);r=.067*(1-t)**1.8+.002
  for j in range(m+1):
   a=2*PI*j/m;verts.append((x,y+r*math.cos(a),z+r*.75*math.sin(a)));uv.append((t,j/m))
 for i in range(n):
  for j in range(m):a=i*(m+1)+j;faces.append((a,a+1,a+m+2,a+m+1))
 mat=material('Maskray_TailSkin',(.055,.047,.030),.52);nt=mat.node_tree;n=nt.nodes;l=nt.links;p=n['Principled BSDF'];tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180;bum=n.new('ShaderNodeBump');bum.inputs['Distance'].default_value=.0006;bum.inputs['Strength'].default_value=.5;l.new(tex.outputs['Fac'],bum.inputs['Height']);l.new(bum.outputs['Normal'],p.inputs['Normal'])
 return mesh('Maskray_TaperedWhipTail',verts,faces,mat,uv)

def animate_disc(o):
 o.shape_key_add(name='Basis');basis=[v.co.copy() for v in o.data.vertices]
 for side in [-1,1]:
  for quadrature in [0,1]:
   key=o.shape_key_add(name=('Left' if side<0 else 'Right')+('_Sine' if quadrature==0 else '_Cosine'),from_mix=False);key.slider_min=-1;key.slider_max=1
   for i,p in enumerate(basis):
    x,y,z=p;span=smooth(.25,1.20,abs(y));envelope=float(np.sin(PI*max(.001,min(.999,(x+1.21)/2.24))))**.60
    amp=.245*span**1.5*envelope*(1 if side<0 else .96)
    if y*side<=0:amp=0
    phase=-2*PI*1.05*(x+1.21)/2.24+(0 if side<0 else .09)
    wave=math.sin(phase) if quadrature==0 else math.cos(phase);key.data[i].co.z+=amp*wave
   for f in range(1,98,2):
    phase=2*PI*(f-1)/96;key.value=math.cos(phase) if quadrature==0 else math.sin(phase);key.keyframe_insert('value',frame=f)
 o.data.shape_keys.animation_data.action.name='Pectoral_Traveling_Wave'

def animate_tail(o):
 o.shape_key_add(name='Basis');key=o.shape_key_add(name='PassiveTailLag');key.slider_min=-1
 for i,v in enumerate(o.data.vertices):
  t=max(0,min(1,(v.co.x-.77)/2.85));key.data[i].co.y+=.055*t*t;key.data[i].co.z+=.015*t*t
 for f in range(1,98,2):key.value=math.sin(2*PI*(f-1)/96-.6);key.keyframe_insert('value',frame=f)
 o.data.shape_keys.animation_data.action.name='Passive_Tail_Lag'

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def studio():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1280;s.render.resolution_y=854;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=97
 s.world=bpy.data.worlds.new('NeutralReferenceWorld');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.23,.26,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.40
 for name,pos,power,size in [('Key',(-3,-4,5),650,3.5),('Fill',(1,4,3),300,4),('Rim',(3,0,4),350,3)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.specular_factor=.50 if name=='Key' else .15;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;aim(o,(0,0,0))
 d=bpy.data.cameras.new('ReviewCamera');o=bpy.data.objects.new('ReviewCamera',d);s.collection.objects.link(o);s.camera=o;o.location=(-3.5,-5.5,6.2);aim(o,(.9,0,.0));d.type='ORTHO';d.ortho_scale=5.6
 s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/'preview.png');return s

bpy.ops.wm.read_factory_settings(use_empty=True);ROOT=bpy.data.objects.new('PhotoInformedMaskray',None);bpy.context.scene.collection.objects.link(ROOT)
print('BUILD_TEXTURES',flush=True)
skin=mapped('Maskray_DermalSkin',textures());belly=material('Maskray_VentralSkin',(.43,.40,.32),.60);cavity=material('Maskray_SpiracleInterior',(.012,.009,.005),.77)
print('BUILD_ANATOMY',flush=True)
disc=body(skin,belly);iris=iris_material()
for side in [-1,1]:eye(side,skin,iris);spiracles(side,skin,cavity)
print('BUILD_TRAVELING_WAVE',flush=True)
whip=tail(skin);animate_disc(disc);animate_tail(whip)
sys.path.insert(0,str(HERE))
from portable_morphs import make_portable
make_portable(disc);make_portable(whip)
s=studio();s.frame_set(13);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'stingray-review.blend'));bpy.ops.render.render(write_still=True)
# A separate close-up exposes the eye and skin surface rather than hiding them in a wide shot.
cam=s.camera;cam.location=(-2.2,-3.3,2.4);aim(cam,(-.52,-.20,.15));cam.data.ortho_scale=1.20;s.render.filepath=str(OUT/'eye-skin-detail.png');bpy.ops.render.render(write_still=True)
print('SOURCE_AND_STILLS_COMPLETE',flush=True)

"""Independent photo-informed fish studies. One selected profile per invocation."""
import bpy,math,json,sys,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT_REPO=HERE.parents[1]
spec=importlib.util.spec_from_file_location('review_utils',HERE.parent/'fish-realism-review'/'revision-02'/'create_review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R);B=R.B
PI=math.pi
slug=sys.argv[sys.argv.index('--')+1];C=json.loads((HERE/'profiles.json').read_text())[slug];OUT=HERE/slug;OUT.mkdir(exist_ok=True);TEX=OUT/'textures';TEX.mkdir(exist_ok=True)

def cached_maps(prefix,channels):
 result={}
 for channel in channels:
  image=bpy.data.images.load(str(TEX/(prefix+'_'+channel+'.png')),check_existing=False);image.colorspace_settings.name='sRGB' if channel=='color' else 'Non-Color';image.pack();result[channel]=image
 return result

def normal_map(height,size_x,size_y):
 gy,gx=np.gradient(height,size_y/(height.shape[0]-1),size_x/(height.shape[1]-1));n=np.stack((-gx,-gy,np.ones_like(height)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return n*.5+.5

def skin_maps():
 if '--reuse-textures' in sys.argv:return cached_maps(slug,['color','normal','rough'])
 w,h=2048,1024;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));z=np.sin(v*2*PI);coarse=R.noise(u,v,15,13,901);micro=R.noise(u,v,440,260,902);fine=R.noise(u,v,1200,680,903)
 back=np.array(C['back_color']);side=np.array(C['side_color']);belly=np.array(C['belly_color']);a=R.smoothstep(.12,.93,z)[...,None];base=side*(1-a)+back*a;a=R.smoothstep(.1,.90,-z)[...,None];base=base*(1-a)+belly*a;base+=(coarse-.5)[...,None]*.035+(micro-.5)[...,None]*.018
 color=base.copy();color+=(micro-.5)[...,None]*.018+(fine-.5)[...,None]*.012;height=(micro-.5)*.00012+(fine-.5)*.00005;rough=C.get('surface_roughness',.51)+(coarse-.5)*.11+(fine-.5)*.045
 nx,ny=(85,50) if C['pattern']=='fine_scales' else (63,39);rng=np.random.default_rng(906);tiles=[]
 for row in range(-1,ny+1):
  for col in range(-1,nx+1):
   cx=(col+.5*(row%2)+rng.uniform(-.13,.13))/nx;cy=(row+.5+rng.uniform(-.10,.10))/ny;tiles.append((cx,cy,rng.uniform(.79,1.1),rng.uniform(.59,.80),rng.uniform(-.16,.16),rng.uniform(-1,1)))
 for cx,cy,rx,ry,ang,pigment in sorted(tiles,key=lambda t:-t[0]):
  x0=max(0,int((cx-1.15/nx)*w));x1=min(w,int((cx+1.15/nx)*w)+1);y0=max(0,int((cy-1/ny)*h));y1=min(h,int((cy+1/ny)*h)+1)
  if x1<=x0 or y1<=y0:continue
  px=(u[y0:y1,x0:x1]-cx)*nx;py=(v[y0:y1,x0:x1]-cy)*ny;xx=px*math.cos(ang)+py*math.sin(ang);yy=-px*math.sin(ang)+py*math.cos(ang);d=np.sqrt((xx/rx)**2+(yy/ry)**2)
  mask=(1-R.smoothstep(.91,1,d))*R.smoothstep(.16,.27,u[y0:y1,x0:x1]);rim=np.exp(-((d-.94)/.045)**2)*R.smoothstep(-.45,.40,xx/rx);local=base[y0:y1,x0:x1]+pigment*(.007 if C['pattern']=='fine_scales' else .027)+rim[...,None]*(.012 if C['pattern']=='fine_scales' else .015 if C['pattern']=='grouper' else .052)+(micro[y0:y1,x0:x1]-.5)[...,None]*.022+(fine[y0:y1,x0:x1]-.5)[...,None]*.012
  color[y0:y1,x0:x1]=color[y0:y1,x0:x1]*(1-mask[...,None])+local*mask[...,None];raised=(.00012 if C['pattern']=='fine_scales' else .00045)*rim+.00015*np.maximum(0,1-d*d)
  height[y0:y1,x0:x1]=height[y0:y1,x0:x1]*(1-mask)+raised*mask;rough[y0:y1,x0:x1]=rough[y0:y1,x0:x1]*(1-mask)+(C.get('surface_roughness',.51)+.06*pigment+rim*.02)*mask
 if C['pattern']=='grouper':
  patch=R.noise(u,v,13,10,911)
  bars=np.zeros_like(u)
  for center in [.24,.40,.56,.72,.87]:
   distance=np.abs(u-center-.024*np.sin(v*PI*4+.7));bars=np.maximum(bars,1-R.smoothstep(.021,.070,distance))
  color*=1-bars[...,None]*.27*(.65+.35*patch[...,None])
  rng=np.random.default_rng(919)
  for k in range(2600):
   cx,cy=rng.uniform(.025,.99),rng.random();rx,ry=rng.uniform(.0012,.0035),rng.uniform(.0018,.0045);x0=max(0,int((cx-rx*1.5)*w));x1=min(w,int((cx+rx*1.5)*w)+2);y0=max(0,int((cy-ry*1.5)*h));y1=min(h,int((cy+ry*1.5)*h)+2)
   d=np.sqrt(((u[y0:y1,x0:x1]-cx)/rx)**2+((v[y0:y1,x0:x1]-cy)/ry)**2);mask=(1-R.smoothstep(.72,1.20,d))*rng.uniform(.35,.75);target=np.array([.18,.105,.040]);local=color[y0:y1,x0:x1];color[y0:y1,x0:x1]=local*(1-mask[...,None])+target*mask[...,None]

 # Mouth and operculum are shallow skin recesses, not detached dark tubes.
 xs=-1.65+2.90*u
 hi=np.interp(xs,C['profile_x'],C['top']);lo=np.interp(xs,C['profile_x'],C['bottom']);world_z=(hi+lo)/2+(hi-lo)/2*np.sin(v*2*PI);flank_mask=np.abs(np.cos(v*2*PI))**4
 endx,endz=C['mouth_end'];startz=-.10 if slug=='golden-pomfret' else -.16 if slug=='grouper' else -.145
 target=startz+(endz-startz)*np.clip((xs+1.65)/(endx+1.65),0,1)
 mouth=np.exp(-((world_z-target)/.0025)**2)*R.smoothstep(-1.66,-1.61,xs)*(1-R.smoothstep(endx-.03,endx+.02,xs))*flank_mask
 gx=C['gill_x'];gh,gl,gw=profile(gx);mid=(gh+gl)/2;radius=(gh-gl)*.5;curve=gx+.08-.24*((world_z-mid)/radius)**2
 gill=np.exp(-((xs-curve)/.0028)**2)*R.smoothstep(gl*.88,gl*.68,world_z)*(1-R.smoothstep(gh*.60,gh*.75,world_z))*flank_mask
 crease=np.maximum(mouth,gill);color*=1-crease[...,None]*.43;height-=crease*.00065
 return {key:R.image_file(slug+'_'+key,data,TEX,key!='color') for key,data in [('color',np.clip(color,0,1)),('normal',normal_map(height,2.9,2.5)),('rough',rough)]}

def pbr(name,images,metal=.04):
 mat=B.material(name,(.3,.3,.3),.43,metal);nt=mat.node_tree;p=nt.nodes['Principled BSDF'];p.inputs['Coat Weight'].default_value=.0;p.inputs['Specular IOR Level'].default_value=.24
 for key,im in images.items():
  t=nt.nodes.new('ShaderNodeTexImage');t.image=im
  if key=='normal':
   n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.58;nt.links.new(t.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs[0],p.inputs['Normal'])
  else:nt.links.new(t.outputs['Color'],p.inputs[{'color':'Base Color','rough':'Roughness','alpha':'Alpha'}[key]])
 return mat

def fin_mat():
 if '--reuse-textures' in sys.argv:return pbr('Fin_ThinBranchingMembrane',cached_maps(slug+'_fin',['color','normal','rough','alpha']),.0)
 n=1024;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));rng=np.random.default_rng(920);grain=R.noise(u,v,240,180,922);coarse=R.noise(u,v,15,12,923);rays=np.zeros_like(u);branches=np.zeros_like(u);positions=np.cumsum(rng.uniform(.75,1.25,23));positions=(positions-positions[0])/(positions[-1]-positions[0])
 for pos in positions:
  center=pos+rng.uniform(-.012,.012)*v*v;width=.0013+.0015*(1-v);rays=np.maximum(rays,np.exp(-((u-center)/width)**2));fork=rng.uniform(.3,.6)
  for sign in [-1,1]:
   child=center+sign*.014*np.maximum(0,(v-fork)/(1-fork));branches=np.maximum(branches,np.exp(-((u-child)/(width*.7))**2)*R.smoothstep(fork,fork+.04,v))
 lines=np.maximum(rays,branches*.70);color=np.zeros((n,n,3))+np.array(C['fin_color']);color+=(coarse-.5)[...,None]*.08; color+=lines[...,None]*np.array([.075,.045,.030]);alpha=np.clip(.74+coarse*.10+lines*.15-.15*R.smoothstep(.80,1,v),.20,.97)
 if C['pattern']=='grouper':
  for k in range(210):
   px,py=rng.random(2);radius=rng.uniform(.007,.018);d=np.sqrt((u-px)**2+(v-py)**2);a=(1-R.smoothstep(radius*.7,radius*1.1,d))*.55;color=color*(1-a[...,None])+np.array([.065,.045,.022])*a[...,None]
 height=lines*.00075+(grain-.5)*.0001;images={key:R.image_file(slug+'_fin_'+key,data,TEX,key!='color') for key,data in [('color',np.clip(color,0,1)),('normal',normal_map(height,1.2,.45)),('rough',.45+(grain-.5)*.09),('alpha',alpha)]}
 return pbr('Fin_ThinBranchingMembrane',images,.0)

def profile(x):return [B.interp(list(zip(C['profile_x'],C[k])),x) for k in ['top','bottom','width']]
def flank(x,z,side,offset=0):
 hi,lo,w=profile(x);a=max(-.999,min(.999,(2*z-hi-lo)/max(.001,hi-lo)));return side*(w*math.sqrt(1-a*a)+offset)

def body(mat):
 verts=[];faces=[];uv=[];nx=142;na=96
 for i in range(nx+1):
  x=-1.65+2.90*i/nx;hi,lo,w=profile(x)
  for j in range(na+1):
   a=2*PI*j/na;y=w*math.cos(a);z=(hi+lo)/2+(hi-lo)/2*math.sin(a);xx=x+C.get('round_snout',0)*(1-R.smoothstep(0,.13,i/nx))*math.sin(a)**2;verts.append((xx,y,z));uv.append((i/nx,j/na))
 for i in range(nx):
  for j in range(na):a=i*(na+1)+j;faces.append((a,a+1,a+na+2,a+na+1))
 faces += [tuple(range(na,-1,-1)),tuple(nx*(na+1)+j for j in range(na+1))];return B.mesh('Skin_AnatomicalProfile',verts,faces,mat,uv)

def eye_material():
 n=512;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));xx=2*u-1;zz=2*v-1;d=np.sqrt(xx*xx+zz*zz);angle=np.arctan2(zz,xx);grain=R.noise(u,v,210,220,942)
 radial=.5+.20*np.sin(angle*121+d*29)+.14*np.sin(angle*77-d*45);color=np.zeros((n,n,3))+np.array(C.get('eye_color',[.27,.025,.012]));color*=.70+radial[...,None]*.45;color+=(grain-.5)[...,None]*.018;rim=R.smoothstep(.81,1,d);color*=1-rim[...,None]*.60;pupil=1-R.smoothstep(.49,.54,d);color=color*(1-pupil[...,None])+np.array([.001,.002,.002])*pupil[...,None]
 im=R.image_file(slug+'_iris',np.clip(color,0,1),TEX);mat=pbr('Eye_RadialIris',{'color':im},.0);p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.26;p.inputs['Coat Weight'].default_value=.12;p.inputs['Coat Roughness'].default_value=.18;return mat

def eyes():
 x,z,r=C['eye'];mat=eye_material()
 for side in [-1,1]:
  verts=[];uv=[];faces=[];nr,na=12,72
  for j in range(nr+1):
   t=max(.00001,j/nr)
   for i in range(na):
    a=2*PI*i/na;xx=x+r*t*math.cos(a);zz=z+r*t*math.sin(a);yy=flank(xx,zz,side,.001)+side*.012*(1-t*t);verts.append((xx,yy,zz));uv.append((.5+.5*t*math.cos(a),.5+.5*t*math.sin(a)))
  for j in range(nr):
   for i in range(na):a=j*na+i;b=j*na+(i+1)%na;f=(a,a+na,b+na,b);faces.append(f if side>0 else f[::-1])
  B.mesh('Eye_EmbeddedIris_'+str(side),verts,faces,mat,uv)

def details():
 eyes()
 # Closed natural mouths and gill creases are authored into the skin maps.
 crease=B.material('NostrilInterior',tuple(v*.25 for v in C['side_color']),.70)
 for side in [-1,1]:B.sphere('Nostril',(-1.48,flank(-1.48,.045,side,.001),.045),(.005,.001,.003),crease)


def fins(mat):
 R.fan('Caudal_Membrane',lambda u:(1.18,0,(u-.5)*.15),lambda u:(2.03-C['tail_fork']*(1-abs(2*u-1)**C.get('tail_power',2)),0,C['tail_height']*(2*u-1)),mat,n=120,m=32,flutter=.020,role='tail')
 start,split,end=C['dorsal_start'],C['dorsal_split'],C['dorsal_end'];spines=11 if slug!='golden-pomfret' else 6
 def edge(u):
  t=u*(spines-1);i=min(spines-2,int(t));f=t-i;xx=start+(split-start)*u;peak=C['spine_height']*(.68+.32*math.sin(u*PI));return(xx,0,profile(xx)[0]+max(.002,peak-min(.035,.45*C['spine_height'])*math.sin(PI*f)))
 R.fan('Dorsal_SpinyMembrane',lambda u:(start+(split-start)*u,0,profile(start+(split-start)*u)[0]*.995),edge,mat,n=120,m=24,flutter=.006,role='dorsal')
 R.fan('Dorsal_SoftRays',lambda u:(split+(end-split)*u,0,profile(split+(end-split)*u)[0]),lambda u:(split+(end-split)*u+(.28*math.sin(PI*u) if slug=='golden-pomfret' else 0),0,profile(split+(end-split)*u)[0]+(B.interp([(0,0),(.10,.47),(.24,.28),(.55,.10),(1,0)],u) if slug=='golden-pomfret' else C['soft_height']*math.sin(PI*u)**.7)),mat,n=120,m=32,flutter=.020,role='dorsal',phase=.5)
 anal_start=C.get('anal_start',.20);anal_span=C.get('anal_end',1.07)-anal_start
 R.fan('Anal_SoftMembrane',lambda u:(anal_start+anal_span*u,0,profile(anal_start+anal_span*u)[1]),lambda u:(anal_start+anal_span*u+(.30*math.sin(PI*u) if slug=='golden-pomfret' else 0),0,profile(anal_start+anal_span*u)[1]-(B.interp([(0,0),(.12,.44),(.27,.25),(.6,.10),(1,0)],u) if slug=='golden-pomfret' else .25*math.sin(PI*u)**.65)),mat,n=100,m=28,flutter=.018,role='anal',phase=1.1)
 for side in [-1,1]:
  gx=C['gill_x'];rootx=gx+.10;h,l,w=profile(rootx)
  R.fan('Pectoral_'+str(side),lambda u:(rootx,side*w*.92,-.05+(u-.5)*.07),lambda u:(rootx+.46+.05*math.sin(PI*u),side*(w+.13*math.sin(PI*u)),-.14+(u-.5)*.24),mat,n=82,m=24,flutter=.018,role='pectoral',phase=side)
  R.fan('Pelvic_'+str(side),lambda u:(-.44,side*.12,profile(-.44)[1]),lambda u:(-.21+.27*u,side*(.13+.07*math.sin(PI*u)),profile(-.44)[1]-.19*math.sin(PI*u)),mat,n=66,m=20,flutter=.012,role='anal',phase=side*.4)

bpy.ops.wm.read_factory_settings(use_empty=True);B.ROOT=bpy.data.objects.new('ASSET_PhotoInformed_'+slug,None);bpy.context.scene.collection.objects.link(B.ROOT);B.SLUG=slug
print('BUILD_MAPS',slug,flush=True);skin=pbr('Skin_IndividualScales',skin_maps(),C.get('metallic',.055 if C['pattern']=='fine_scales' else .025));fm=fin_mat();body(skin);details();fins(fm)
print('BIND_SWIM',slug,flush=True);rig=B.add_rig('bass')
sys.path.insert(0,str(HERE))
from fin_weights import attach_fin_roots
attach_fin_roots(bpy.context.scene)
for o in B.ROOT.children_recursive:
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=True
# Studio utility uses a neutral environment; no habitat hides anatomical detail.
spec=importlib.util.spec_from_file_location('studio',HERE.parent/'fish-realism-review'/'revision-03'/'create_review.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);s=P.studio(OUT);s.camera.data.ortho_scale=4.6;s.camera.location=(-.15,-9,.85);P.aim(s.camera,(.14,0,.02));s.frame_set(13);s.frame_end=73
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(slug+'.blend')));bpy.ops.render.render(write_still=True)
s.camera.location=(-1.15,-7,.55);P.aim(s.camera,(-1.03,0,.02));s.camera.data.ortho_scale=1.65;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True)
print('GENERATED',slug,flush=True)

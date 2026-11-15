"""Independent photo-informed fish studies. One selected profile per invocation."""
import bpy,math,json,sys,importlib.util
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT_REPO=HERE.parents[1]
sys.path.insert(0,str(HERE))
from fin_attachment import pelvic_base
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
 nx,ny=C.get('scale_density',(85,50) if C['pattern']=='fine_scales' else (63,39));rng=np.random.default_rng(906);tiles=[]
 if C['pattern']!='scaleless':
  for row in range(-1,ny+1):
   for col in range(-1,nx+1):
    jitter=C.get('scale_jitter',[.13,.10]);cx=(col+.5*(row%2)+rng.uniform(-jitter[0],jitter[0]))/nx;cy=(row+.5+rng.uniform(-jitter[1],jitter[1]))/ny;tiles.append((cx,cy,rng.uniform(.79,1.1),rng.uniform(.59,.80),rng.uniform(-.16,.16),rng.uniform(-1,1)))
 for cx,cy,rx,ry,ang,pigment in sorted(tiles,key=lambda t:-t[0]):
  x0=max(0,int((cx-1.15/nx)*w));x1=min(w,int((cx+1.15/nx)*w)+1);y0=max(0,int((cy-1/ny)*h));y1=min(h,int((cy+1/ny)*h)+1)
  if x1<=x0 or y1<=y0:continue
  px=(u[y0:y1,x0:x1]-cx)*nx;py=(v[y0:y1,x0:x1]-cy)*ny;xx=px*math.cos(ang)+py*math.sin(ang);yy=-px*math.sin(ang)+py*math.cos(ang);d=np.sqrt((xx/rx)**2+(yy/ry)**2)
  mask=(1-R.smoothstep(.91,1,d))*R.smoothstep(.16,.27,u[y0:y1,x0:x1]);rim=np.exp(-((d-.94)/.045)**2)*R.smoothstep(-.45,.40,xx/rx);local=base[y0:y1,x0:x1]+pigment*C.get('scale_pigment_gain',.007 if C['pattern']=='fine_scales' else .027)+rim[...,None]*C.get('scale_rim_gain',.012 if C['pattern']=='fine_scales' else .015 if C['pattern']=='grouper' else .052)+(micro[y0:y1,x0:x1]-.5)[...,None]*.022+(fine[y0:y1,x0:x1]-.5)[...,None]*.012
  dark_rim=np.exp(-((d-.94)/C.get('scale_dark_rim_width',.045))**2)*R.smoothstep(-.45,.40,xx/rx)
  if C.get('scale_rim_tint'):local+=dark_rim[...,None]*np.array(C['scale_rim_tint'])*(.65+.35*pigment)
  local-=dark_rim[...,None]*C.get('scale_dark_rim_gain',0)*(.8+.2*pigment)
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

 if C.get('markings')=='black_pomfret':
  px=(C['gill_x']+.10+1.65)/2.90;patch=np.exp(-((u-px)/.028)**2-((z+.02)/.21)**2);color*=1-patch[...,None]*.52
 if C.get('markings')=='indian_mackerel':
  stripe=np.zeros_like(u)
  for level in [.27,.46,.65]:stripe=np.maximum(stripe,np.exp(-((z-level-.008*np.sin(u*31))/.026)**2))
  stripe*=R.smoothstep(.20,.31,u)*(1-R.smoothstep(.91,.99,u));color=color*(1-stripe[...,None]*.36)+np.array([.25,.24,.055])*stripe[...,None]*.36
  spots=np.zeros_like(u)
  for row,level in enumerate([.81,.94]):
   for k in range(15):
    cx=.29+k*.039+.012*row;spots=np.maximum(spots,np.exp(-((u-cx)/.0045)**2-((z-level)/.022)**2))
  color*=1-spots[...,None]*.55;patch=np.exp(-((u-.34)/.024)**2-((z+.13)/.13)**2);color*=1-patch[...,None]*.64
 if C.get('markings')=='spanish_mackerel':
  wave=u*43+.27*np.sin(u*7)+.14*np.sin(v*19+u*8)+.10*np.sin(v*43+u*7);bars=np.exp(-(np.sin(PI*wave)/.32)**2)*R.smoothstep(.28,.32,u)*(1-R.smoothstep(.95,1,u))*R.smoothstep(-.76,-.55,z)
  color*=1-bars[...,None]*.19
 # Mouth and operculum are shallow skin recesses, not detached dark tubes.
 xs=-1.65+2.90*u
 hi=np.interp(xs,C['profile_x'],C['top']);lo=np.interp(xs,C['profile_x'],C['bottom']);world_z=(hi+lo)/2+(hi-lo)/2*np.sin(v*2*PI);flank_mask=np.abs(np.cos(v*2*PI))**4
 if C.get('markings') in ['yellow_scad','bigeye_scad','trevally']:
  yellow=C['markings']=='yellow_scad';level=.14-.035*(xs+.8);band=np.exp(-((world_z-level)/(.040 if yellow else .022))**2)*R.smoothstep(-1.39,-1.24,xs)*(1-R.smoothstep(1.15,1.25,xs))*flank_mask
  strength=.82 if yellow else 0 if C['markings']=='trevally' else .15;color=color*(1-band[...,None]*strength)+np.array([.83,.64,.085])*band[...,None]*strength
  sx,sz=(-.81,.22) if C['markings']=='trevally' else (-.96,.27);spot=np.exp(-((xs-sx)/.044)**2-((world_z-sz)/.042)**2)*flank_mask;color*=1-spot[...,None]*(.76 if yellow else .68 if C['markings']=='trevally' else .30)
  line_z=.12*(1-R.smoothstep(-.15,.38,xs));lateral=np.exp(-((world_z-line_z)/.0035)**2)*R.smoothstep(-.83,-.67,xs)*flank_mask;color*=1-lateral[...,None]*.10
  # Posterior scutes remain tiny skin relief, not detached polygon plates.
  for k in range(29 if C['markings']=='trevally' else 17):
   sx=.30+k*.030+.002*math.sin(k*2.17) if C['markings']=='trevally' else .38+k*.047;dx=(xs-sx)/.022;dz=(world_z-.003)/(.019*(.88+.12*math.sin(k*1.71)) if C['markings']=='trevally' else .025);scute=np.exp(-((dx+.28*np.abs(dz))/.15)**2)*(1-R.smoothstep(.65,1.05,np.abs(dz)))*flank_mask
   height+=scute*.00035
   if C['markings']=='trevally':color*=1-scute[...,None]*.11
   else:color+=scute[...,None]*.018
 if C.get('markings')=='parrotfish':
  bars=np.exp(-(np.sin(PI*((xs+.9)*1.9+.1*np.sin(world_z*10)))/.65)**2)*R.smoothstep(-.93,-.65,xs)*flank_mask;color*=1-bars[...,None]*.13
  lines=np.zeros_like(xs)
  for level in [-.15,-.02,.16]:lines=np.maximum(lines,np.exp(-((world_z-level-.045*np.sin((xs+1.6)*6))/.011)**2))
  lines*=R.smoothstep(-1.66,-1.55,xs)*(1-R.smoothstep(-.96,-.80,xs))*flank_mask;color=color*(1-lines[...,None]*.84)+np.array([.08,.47,.49])*lines[...,None]*.84
 if C.get('markings')=='lionfish':
  phase=(xs+1.65)*3.0+.20*np.sin(world_z*5)+.07*np.sin(world_z*17+xs*8)+(R.noise(u,v,35,26,1030)-.5)*.09;bars=1-R.smoothstep(.45,.70,np.abs(np.sin(PI*phase)));narrow=np.exp(-(np.sin(PI*(phase*3+.25))/.24)**2);a=np.maximum(bars*.95,narrow*.64);color=color*(1-a[...,None])+np.array([.19,.035,.023])*a[...,None]
 if C.get('markings')=='clownfish':
  from clown_pattern import paint_bands
  color=paint_bands(color,xs,world_z,R.smoothstep)
 if C.get('markings')=='humpback_puffer':
  field=R.noise(u,v,44,31,1001)*.58+R.noise(u,v,97,63,1002)*.29+R.noise(u,v,210,141,1004)*.13;reticulation=np.exp(-((field-.51)/.030)**2);color*=.58+.42*reticulation[...,None];color+=(micro-.5)[...,None]*.018;height+=R.smoothstep(.75,.94,R.noise(u,v,180,130,1003))*.0003
 if C.get('markings')=='hampala':
  boundary=(R.noise(u,v,65,47,998)-.5)*.12;distance=np.sqrt(((xs-.10-.02*np.sin(world_z*12))/.145)**2+((world_z-.18)/.43)**2);bar=(1-R.smoothstep(.62,1.25,distance+boundary))*flank_mask;color*=1-bar[...,None]*.61
 if C.get('markings')=='jade_perch':
  blotches=np.maximum(np.exp(-((xs+.10)/.17)**2-((world_z-.17)/.14)**2),np.exp(-((xs-.62)/.14)**2-((world_z+.02)/.12)**2))*flank_mask;color*=1-blotches[...,None]*C.get('marking_gain',.10)
  stripe=np.exp(-((world_z+.045-.018*np.sin((xs+1.5)*4))/.020)**2)*R.smoothstep(-1.57,-1.43,xs)*(1-R.smoothstep(-1.12,-.95,xs))*flank_mask;color+=stripe[...,None]*.055
 if C.get('markings')=='grey_mullet':
  lines=np.zeros_like(u)
  for level in [-.22,-.13,-.04,.05,.14,.23]:lines=np.maximum(lines,np.exp(-((world_z-level)/.009)**2))
  color*=1-lines[...,None]*flank_mask[...,None]*R.smoothstep(-1.03,-.80,xs)[...,None]*.11
  spot=np.exp(-((xs+.84)/.043)**2-((world_z-.02)/.052)**2)*flank_mask;color*=1-spot[...,None]*.62
 if C.get('markings')=='three_spot_gourami':
  edge=(R.noise(u,v,93,73,996)-.5)*.14;d1=np.sqrt(((xs+.05)/.125)**2+((world_z-.01)/.12)**2);d2=np.sqrt(((xs-1.08)/.075)**2+(world_z/.075)**2);spots=np.maximum(1-R.smoothstep(.65,1.15,d1+edge),1-R.smoothstep(.65,1.15,d2+edge))*flank_mask
  color*=1-spots[...,None]*.84
  marbling=R.smoothstep(.47,.69,R.noise(u,v,18,14,995))*R.smoothstep(.25,.38,u)*.18;color*=1-marbling[...,None]
 if C.get('markings')=='climbing_perch':
  edge_noise=(R.noise(u,v,120,90,989)-.5)*.20;d1=np.sqrt(((xs+.86)/.05)**2+((world_z-.13)/.065)**2);d2=np.sqrt(((xs-1.09)/.055)**2+(world_z/.065)**2);spot=np.maximum(1-R.smoothstep(.65,1.10,d1+edge_noise),1-R.smoothstep(.65,1.10,d2+edge_noise));color*=1-spot[...,None]*flank_mask[...,None]*.82
  bars=np.exp(-(np.sin(PI*(u*7+.10*np.sin(v*16)))/.53)**2)*R.smoothstep(.30,.42,u)*(1-R.smoothstep(.91,.98,u));color*=1-bars[...,None]*.10
 if C.get('markings')=='giant_snakehead':
  boundary=-.04+.035*np.sin(xs*17)+.014*np.sin(xs*43);band=(1-R.smoothstep(boundary+.025,boundary+.10,world_z))*R.smoothstep(-.22,-.13,world_z)*flank_mask*R.smoothstep(-1.40,-1.05,xs);color=color*(1-band[...,None]*.68)+np.array([.10,.135,.15])*band[...,None]*.68
 if C.get('markings')=='snakehead':
  bars=np.exp(-(np.sin(PI*(u*9+.13*np.sin(v*15)+.25*v))/.45)**2)*R.smoothstep(-1.05,-.80,xs)*R.smoothstep(-.45,.5,z);color*=1-bars[...,None]*.35
  mottled=R.noise(u,v,35,25,981)*.55+R.noise(u,v,83,61,982)*.45;mask=R.smoothstep(.50,.66,mottled)*(1-R.smoothstep(.28,.42,u))*.25;color*=1-mask[...,None]
 if C.get('markings')=='marble_goby':
  mottled=R.noise(u,v,10,9,971)*.65+R.noise(u,v,23,17,972)*.35;mask=R.smoothstep(.46,.59,mottled)*.76;target=np.array([.105,.082,.045]);color=color*(1-mask[...,None])+target*mask[...,None]
 if C.get('markings')=='tilapia':
  bars=np.exp(-(np.sin(PI*(u*8.2+.10*np.sin(v*17)))/.53)**2)*R.smoothstep(.23,.33,u);color*=1-bars[...,None]*.21
  lateral=np.exp(-((world_z-.05)/.018)**2)*R.smoothstep(-1.05,-.8,xs)*flank_mask;color*=1-lateral[...,None]*.18
 if C.get('markings')=='red_tilapia':
  flush=R.noise(u,v,11,9,963);patch=R.smoothstep(.48,.72,flush)*.24;color=color*(1-patch[...,None])+np.array([.72,.33,.28])*patch[...,None]
 if C.get('markings')=='croaker':
  patch=np.exp(-((xs-(C['gill_x']+.08))/.085)**2-((world_z-.07)/.12)**2)*flank_mask;color*=1-patch[...,None]*.38
 if C.get('markings')=='red_seabream':
  rng=np.random.default_rng(955)
  for k in range(180):
   cx,cy=rng.uniform(.18,.91),rng.uniform(.025,.46);rx,ry=rng.uniform(.0013,.0023),rng.uniform(.0015,.0025);x0=max(0,int((cx-rx*1.5)*w));x1=min(w,int((cx+rx*1.5)*w)+2);y0=max(0,int((cy-ry*1.5)*h));y1=min(h,int((cy+ry*1.5)*h)+2)
   d=np.sqrt(((u[y0:y1,x0:x1]-cx)/rx)**2+((v[y0:y1,x0:x1]-cy)/ry)**2);mask=(1-R.smoothstep(.65,1.20,d))*.50;local=color[y0:y1,x0:x1];color[y0:y1,x0:x1]=local*(1-mask[...,None])+np.array([.42,.61,.61])*mask[...,None]
 if C.get('markings')=='rabbitfish':
  rng=np.random.default_rng(951)
  for k in range(350):
   cx,cy=rng.uniform(.10,.97),rng.random();rx,ry=rng.uniform(.0025,.0048),rng.uniform(.0035,.0065);x0=max(0,int((cx-rx*1.5)*w));x1=min(w,int((cx+rx*1.5)*w)+2);y0=max(0,int((cy-ry*1.5)*h));y1=min(h,int((cy+ry*1.5)*h)+2)
   d=np.sqrt(((u[y0:y1,x0:x1]-cx)/rx)**2+((v[y0:y1,x0:x1]-cy)/ry)**2);mask=(1-R.smoothstep(.55,1.15,d))*rng.uniform(.35,.67);local=color[y0:y1,x0:x1];color[y0:y1,x0:x1]=local*(1-mask[...,None])+np.array([.64,.70,.65])*mask[...,None]
 if C.get('markings') in ['sardine','anchovy']:
  anchovy=C['markings']=='anchovy';level=.025 if anchovy else .105;stripe=np.exp(-((world_z-level)/(.042 if anchovy else .018))**2)*R.smoothstep(-1.10,-.89,xs)*(1-R.smoothstep(1.12,1.25,xs))*flank_mask;strength=.76 if anchovy else .19
  target=np.array([.86,.89,.88]) if anchovy else np.array([.66,.62,.35]);color=color*(1-stripe[...,None]*strength)+target*stripe[...,None]*strength;rough-=stripe*(.10 if anchovy else .025)
 endx,endz=C['mouth_end'];startz=C.get('mouth_start_z',-.10 if slug=='golden-pomfret' else -.16 if slug=='grouper' else -.145)
 target=startz+(endz-startz)*np.clip((xs+1.65)/(endx+1.65),0,1)
 mouth=np.exp(-((world_z-target)/.0025)**2)*R.smoothstep(-1.66,-1.61,xs)*(1-R.smoothstep(endx-.03,endx+.02,xs))*flank_mask
 gx=C['gill_x'];gh,gl,gw=profile(gx);mid=(gh+gl)/2;radius=(gh-gl)*.5;curve=gx+.08-.24*((world_z-mid)/radius)**2
 gill=np.exp(-((xs-curve)/.0028)**2)*R.smoothstep(gl*.88,gl*.68,world_z)*(1-R.smoothstep(gh*.60,gh*.75,world_z))*flank_mask
 if 'gill_bounds' in C:
  gb,gt=C['gill_bounds'];gm=(gb+gt)/2;gr=(gt-gb)/2;curve=gx+.04-.08*((world_z-gm)/gr)**2;gill=np.exp(-((xs-curve)/.0028)**2)*R.smoothstep(gb,gb+.06,world_z)*(1-R.smoothstep(gt-.06,gt,world_z))*flank_mask
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

def fin_mat(tail=False,spiny=False):
 prefix=slug+('_spiny' if spiny else '_tail' if tail else '_fin')
 if '--reuse-textures' in sys.argv:return pbr('Fin_ThinBranchingMembrane',cached_maps(prefix,['color','normal','rough','alpha']),.0)
 n=1024;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));rng=np.random.default_rng(920);grain=R.noise(u,v,240,180,922);coarse=R.noise(u,v,15,12,923);rays=np.zeros_like(u);branches=np.zeros_like(u);positions=np.cumsum(rng.uniform(.75,1.25,23));positions=(positions-positions[0])/(positions[-1]-positions[0])
 for pos in positions:
  center=pos+rng.uniform(-.012,.012)*v*v;width=.0013+.0015*(1-v);rays=np.maximum(rays,np.exp(-((u-center)/width)**2));fork=rng.uniform(.3,.6)
  for sign in [-1,1]:
   child=center+sign*.014*np.maximum(0,(v-fork)/(1-fork));branches=np.maximum(branches,np.exp(-((u-child)/(width*.7))**2)*R.smoothstep(fork,fork+.04,v))
 lines=np.maximum(rays,branches*.70);color=np.zeros((n,n,3))+np.array(C['tail_color'] if tail else C['fin_color']);color+=(coarse-.5)[...,None]*.08; color+=lines[...,None]*np.array([.075,.045,.030]);alpha=np.clip(.74+coarse*.10+lines*.15-.15*R.smoothstep(.80,1,v),.20,.97)
 if C.get('fin_markings')=='lionfish':
  dots=np.exp(-(np.sin(PI*(u*14+.12*np.sin(v*8)))/.28)**2-(np.sin(PI*(v*7+.15*np.sin(u*15)))/.33)**2);color=color*(1-dots[...,None]*.83);alpha=np.maximum(.40+lines*.32,dots*.9)
 if spiny and C.get('lion_radial_fins'):
  band=1-R.smoothstep(.35,.64,np.abs(np.sin(PI*(v*8+.07*np.sin(u*7)))));color=color*(1-band[...,None]*.92)+np.array([.20,.035,.024])*band[...,None]*.92;alpha=np.ones_like(v)
 if C.get('fin_markings')=='marble':
  patch=R.smoothstep(.41,.64,coarse)*.65;color=color*(1-patch[...,None])+np.array([.10,.08,.045])*patch[...,None]
 if C.get('fin_markings')=='tilapia':
  if tail:
   bars=np.exp(-(np.sin(v*PI*7+.20*np.sin(u*8))/.42)**2);color*=1-bars[...,None]*.39
  else:
   marks=np.exp(-(np.sin((u*11+v*4)*PI)/.37)**2)*R.smoothstep(.25,.7,v);color*=1-marks[...,None]*.28;color*=1-R.smoothstep(.94,1,v)[...,None]*.25
 if spiny:color*=1-C.get('spiny_dorsal_dark_top',0)*R.smoothstep(.28,.65,v)[...,None]
 if tail and C.get('tail_dark_margin'):
  color*=1-C['tail_dark_margin']*R.smoothstep(.87,.99,v)[...,None]
 if not tail and C.get('fin_dark_margin'):color*=1-C['fin_dark_margin']*R.smoothstep(.89,.99,v)[...,None]
 if tail and C.get('tail_submarginal_stripe'):
  stripe=np.exp(-((v-.85)/.055)**4)*R.smoothstep(.10,.25,np.abs(u-.5));color*=1-stripe[...,None]*C['tail_submarginal_stripe']
  if C.get('tail_pale_margin'):color+=R.smoothstep(.965,1,v)[...,None]*C['tail_pale_margin']
 if spiny and C.get('dorsal_black_tip'):
  tip=R.smoothstep(.72,.91,v)*(1-R.smoothstep(.16,.42,u));color*=1-tip[...,None]*C['dorsal_black_tip']
 if spiny and C.get('markings')=='clownfish':
  from clown_pattern import paint_bands
  xs=C['dorsal_start']+(C['dorsal_split']-C['dorsal_start'])*u;world_z=np.interp(xs,C['profile_x'],C['top'])+C['spine_height']*v;color=paint_bands(color,xs,world_z,R.smoothstep);color*=1-C.get('fin_dark_margin',.72)*R.smoothstep(.93,.99,v)[...,None]
 if C.get('fin_margin_color'):
  margin=R.smoothstep(.87,.97,v)*C.get('fin_margin_gain',.85);color=color*(1-margin[...,None])+np.array(C['fin_margin_color'])*margin[...,None]
 if C['pattern']=='grouper':
  for k in range(210):
   px,py=rng.random(2);radius=rng.uniform(.007,.018);d=np.sqrt((u-px)**2+(v-py)**2);a=(1-R.smoothstep(radius*.7,radius*1.1,d))*.55;color=color*(1-a[...,None])+np.array([.065,.045,.022])*a[...,None]
 height=lines*.00075+(grain-.5)*.0001;images={key:R.image_file(prefix+'_'+key,data,TEX,key!='color') for key,data in [('color',np.clip(color,0,1)),('normal',normal_map(height,1.2,.45)),('rough',.45+(grain-.5)*.09),('alpha',alpha)]}
 return pbr('Fin_ThinBranchingMembrane',images,.0)

def profile(x):return [B.interp(list(zip(C['profile_x'],C[k])),x) for k in ['top','bottom','width']]
def flank(x,z,side,offset=0):
 hi,lo,w=profile(x);a=max(-.999,min(.999,(2*z-hi-lo)/max(.001,hi-lo)));return side*(w*math.sqrt(1-a*a)+offset)

def body(mat):
 verts=[];faces=[];uv=[];nx=142;na=96
 for i in range(nx+1):
  x=-1.65+2.90*i/nx;hi,lo,w=profile(x)
  for j in range(na+1):
   a=2*PI*j/na;y=w*math.cos(a);z=(hi+lo)/2+(hi-lo)/2*math.sin(a);xx=x+C.get('round_snout',0)*(1-R.smoothstep(0,.13,i/nx))*math.sin(a)**2
   if C.get('lip_bulge'):
    start=C.get('mouth_start_z',-.14);endx,endz=C['mouth_end'];mouth_z=start+(endz-start)*max(0,min(1,(x+1.65)/(endx+1.65)));ridge=math.exp(-((z-mouth_z-.032)/.035)**2)+math.exp(-((z-mouth_z+.032)/.035)**2);xx-=C['lip_bulge']*math.exp(-((x+1.60)/.14)**2)*ridge
   verts.append((xx,y,z));uv.append((i/nx,j/na))
 for i in range(nx):
  for j in range(na):a=i*(na+1)+j;faces.append((a,a+1,a+na+2,a+na+1))
 if C.get('lip_bulge'):
  # A curved lip cannot be closed by a single non-planar n-gon: tessellate the snout.
  hi,lo,w=profile(-1.65);previous=list(range(na+1))
  for ring in range(1,13):
   radius=1-ring/13;current=[]
   for j in range(na+1):
    angle=2*PI*j/na;y=w*math.cos(angle)*radius;z=(hi+lo)/2+(hi-lo)/2*math.sin(angle)*radius;mouth_z=C.get('mouth_start_z',-.14)
    ridge=math.exp(-((z-mouth_z-.032)/.035)**2)+math.exp(-((z-mouth_z+.032)/.035)**2)
    xx=-1.65-.035*(1-radius*radius)+C.get('round_snout',0)*math.sin(angle)**2*radius*radius-C['lip_bulge']*math.exp(-(.05/.14)**2)*ridge
    current.append(len(verts));verts.append((xx,y,z));uv.append((.018*(1-radius),j/na))
   for j in range(na):faces.append((previous[j+1],previous[j],current[j],current[j+1]))
   previous=current
  center=len(verts);verts.append((-1.69,0,(hi+lo)/2));uv.append((.02,.5))
  for j in range(na):faces.append((previous[j+1],previous[j],center))
 else:faces.append(tuple(range(na,-1,-1)))
 faces.append(tuple(nx*(na+1)+j for j in range(na+1)));return B.mesh('Skin_AnatomicalProfile',verts,faces,mat,uv)

def eye_material():
 n=512;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));xx=2*u-1;zz=2*v-1;d=np.sqrt(xx*xx+zz*zz);angle=np.arctan2(zz,xx);grain=R.noise(u,v,210,220,942)
 radial=.5+.20*np.sin(angle*121+d*29)+.14*np.sin(angle*77-d*45);color=np.zeros((n,n,3))+np.array(C.get('eye_color',[.27,.025,.012]));color*=.70+radial[...,None]*.45;color+=(grain-.5)[...,None]*.018;rim=R.smoothstep(.81,1,d);color*=1-rim[...,None]*.60;pupil=1-R.smoothstep(C.get('pupil_radius',.515)-.025,C.get('pupil_radius',.515)+.025,d);color=color*(1-pupil[...,None])+np.array([.001,.002,.002])*pupil[...,None]
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


def fin_sweep(u,anal=False):
 if slug=='golden-pomfret':return (.30 if anal else .28)*math.sin(PI*u)
 if C.get('fin_shape')=='pomfret':return .16*math.sin(PI*u)
 return 0

def fin_height(u,anal=False):
 if C.get('anal_height_curve' if anal else 'soft_height_curve'):return B.interp(C['anal_height_curve' if anal else 'soft_height_curve'],u)
 if anal and C.get('anal_soft_start_height'):return C['anal_height']*math.sin(PI*u)**.65+C['anal_soft_start_height']*(1-u)**4
 if not anal and C.get('soft_start_height'):return C['soft_height']*math.sin(PI*u)**.7+C['soft_start_height']*(1-u)**4
 if C.get('soft_forward_lobes'):return B.interp([(0,0),(.13,1),(.36,.48),(.72,.13),(1,0)],u)*(C.get('anal_height',.25) if anal else C['soft_height'])
 if slug=='golden-pomfret':return B.interp([(0,0),(.12,.44),(.27,.25),(.6,.10),(1,0)] if anal else [(0,0),(.10,.47),(.24,.28),(.55,.10),(1,0)],u)
 if C.get('fin_shape')=='pomfret':return B.interp([(0,0),(.12,.30),(.35,.16),(.70,.055),(1,0)],u)*C['soft_height']/.30
 return C.get('anal_height',.25)*math.sin(PI*u)**.65 if anal else C['soft_height']*math.sin(PI*u)**.7

def fins(mat):
 caudal_mat=fin_mat(True) if 'tail_color' in C else mat
 spiny_mat=fin_mat(spiny=True) if C.get('spiny_dorsal_dark_top') or C.get('dorsal_black_tip') or C.get('markings')=='clownfish' else mat
 R.fan('Caudal_Membrane',lambda u:(1.18,0,(u-.5)*.15),lambda u:(C.get('tail_end',2.03)-C['tail_fork']*(1-abs(2*u-1)**C.get('tail_power',2)),0,C['tail_height']*(2*u-1)*(1+C.get('tail_lower_extra',0) if u<.5 else 1)),caudal_mat,n=120,m=32,flutter=.020,role='tail')
 start,split,end=C['dorsal_start'],C['dorsal_split'],C['dorsal_end'];spines=C.get('dorsal_spines',6 if slug=='golden-pomfret' else 11)
 def edge(u):
  t=u*(spines-1);i=min(spines-2,int(t));f=t-i;xx=start+(split-start)*u;peak=(.01+C['spine_height']*(1-u)**.85) if C.get('spine_taper') else C['spine_height']*(.68+.32*math.sin(u*PI));peak=B.interp(C['spine_height_curve'],u) if C.get('spine_height_curve') else peak;return(xx,0,profile(xx)[0]+max(.002,peak-(C.get('spine_notch_factor',0)*peak if C.get('spine_notch_factor') else min(.035,.45*C['spine_height']))*math.sin(PI*f)))
 if spines>0:R.fan('Dorsal_SpinyMembrane',lambda u:(start+(split-start)*u,0,profile(start+(split-start)*u)[0]*.995),edge,spiny_mat,n=120,m=24,flutter=.006,role='dorsal')
 second=C.get('dorsal_second_start',split)
 R.fan('Dorsal_SoftRays',lambda u:(second+(end-second)*u,0,profile(second+(end-second)*u)[0]),lambda u:(second+(end-second)*u+fin_sweep(u),0,profile(second+(end-second)*u)[0]+fin_height(u)),spiny_mat if C.get('dorsal_black_tip') else mat,n=120,m=32,flutter=.020,role='dorsal',phase=.5)
 anal_start=C.get('anal_start',.20)
 if C.get('anal_spines'):
  a0=anal_start;a1=C['anal_split'];count=C['anal_spines']
  def anal_spiny_edge(u):
   x=a0+(a1-a0)*u;val=(u*(count-1))%1;extent=C.get('anal_spine_height',.16)*(.65+.35*math.sin(PI*u))-.035*math.sin(PI*val)
   return(x,0,profile(x)[1]-max(.003,extent))
  R.fan('Anal_SpinyMembrane',lambda u:(a0+(a1-a0)*u,0,profile(a0+(a1-a0)*u)[1]),anal_spiny_edge,mat,n=100,m=24,flutter=.005,role='anal');anal_start=a1
 anal_span=C.get('anal_end',1.07)-anal_start
 R.fan('Anal_SoftMembrane',lambda u:(anal_start+anal_span*u,0,profile(anal_start+anal_span*u)[1]),lambda u:(anal_start+anal_span*u+fin_sweep(u,True),0,profile(anal_start+anal_span*u)[1]-fin_height(u,True)),mat,n=100,m=28,flutter=.018,role='anal',phase=1.1)
 from adipose import build_adipose
 build_adipose(B,C,profile)
 for k in range(C.get('finlets',0)):
  x=C.get('finlet_start',.94)+k*C.get('finlet_spacing',.055);height=C.get('finlet_height',.055)*(1-k*C.get('finlet_taper',.12))
  for sign,role in [(1,'dorsal'),(-1,'anal')]:
   idx=0 if sign>0 else 1;vs=[(x,0,profile(x)[idx]),(x+.052,0,profile(x+.052)[idx]),(x+.035,.001,profile(x+.035)[idx]+sign*height),(x+.014,0,profile(x+.014)[idx]+sign*height*.35)]
   B.mesh('Finlet_%s_%d'%(role,k),vs,[(0,1,2),(0,2,3)],mat,[(0,0),(1,0),(.65,1),(.25,.35)],deform=role)
 if C.get('caudal_keel'):
  for side in [-1,1]:
   vertices=[];uv=[]
   for i,x in enumerate([.92,1.04,1.16,1.25]):
    hi,lo,w=profile(x);mid=(hi+lo)/2;extent=.008*math.sin(PI*i/3)
    vertices.extend([(x,side*w,mid-.006),(x,side*(w+extent),mid),(x,side*w,mid+.006)]);uv.extend([(i/3,0),(i/3,.5),(i/3,1)])
   faces=[]
   for i in range(3):
    a=i*3;faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
   B.mesh('Caudal_PeduncleKeel_'+str(side),vertices,faces,mat,uv)
 for side in [-1,1]:
  gx=C['gill_x'];rootx=gx+.10;h,l,w=profile(rootx);root_z=C.get('pectoral_root_z',-.05)
  def pectoral_edge(u):
   if C.get('pectoral_shape')=='rounded':
    spread=math.sin(PI*u)**.6
    return(rootx+C.get('pectoral_length',.4)*spread,side*(w+.08*math.sin(PI*u)),root_z+(u-.5)*C.get('pectoral_height',.29)-C.get('pectoral_droop',.1)*spread)
   if C.get('pectoral_shape')=='tapered':
    spread=B.interp([(0,0),(.22,1),(.64,.55),(1,0)],u)
    return(rootx+C.get('pectoral_length',.46)*spread,side*(w+.08*math.sin(PI*u)),root_z-C.get('pectoral_droop',.09)*spread+(u-.5)*C.get('pectoral_height',.24)*(1-.5*spread))
   return(rootx+C.get('pectoral_length',.46)+.05*math.sin(PI*u),side*(w+.13*math.sin(PI*u)),root_z-C.get('pectoral_droop',.09)+(u-.5)*C.get('pectoral_height',.24))
  pectoral=R.fan('Pectoral_'+str(side),lambda u:(rootx,flank(rootx,root_z+(u-.5)*.07,side,.001) if C.get('pectoral_surface_anchor') else side*w*.92,root_z+(u-.5)*.07),pectoral_edge,mat,n=82,m=24,flutter=.018,role='pectoral',phase=side)
  if C.get('pectoral_shape') in ['tapered','rounded']:
   # The preserved review utility used a fixed world-space edge ripple, which
   # overwhelms small membranes. Retain only a slight natural irregularity.
   uv=pectoral.data.uv_layers.active;coordinates={loop.vertex_index:uv.data[loop.index].uv.copy() for loop in pectoral.data.loops}
   for vertex in pectoral.data.vertices:
    u,t=coordinates[vertex.index];noise=.008*math.sin(u*113+side)+.005*math.sin(u*197+1.7)+.004*math.sin(u*61+.4);vertex.co.z-=noise*t**5*.85
   pectoral.data.update()
  if C.get('pelvic',True):
   pelvic=R.fan('Pelvic_'+str(side),lambda u:pelvic_base(profile,side,u,C.get('pelvic_root_x',-.44)),lambda u:(C.get('pelvic_start_x',-.21)+(C.get('pelvic_end_x',.06)-C.get('pelvic_start_x',-.21))*u,side*(.13+.07*math.sin(PI*u)),profile(C.get('pelvic_root_x',-.44))[1]-C.get('pelvic_length',.19)*math.sin(PI*u)),mat,n=66,m=20,flutter=.012,role='anal',phase=side*.4)
   pelvic['pelvic_surface_anchor']='Ventrolateral body surface with a small embedded root curve'
 if 'fin_edge_noise_gain' in C:
  # The review utility's fixed edge displacement overwhelms small soft fins.
  for obj in [o for o in B.ROOT.children_recursive if o.type=='MESH']:
   name=obj.name
   if name.startswith('Pectoral_') or not name.startswith(('Caudal_Membrane','Dorsal_SpinyMembrane','Dorsal_SoftRays','Anal_SpinyMembrane','Anal_SoftMembrane','Pelvic_')):continue
   phase=.5 if name.startswith('Dorsal_SoftRays') else 1.1 if name.startswith('Anal_SoftMembrane') else .4 if name.startswith('Pelvic_1') else -.4 if name.startswith('Pelvic_-1') else 0
   coordinates={loop.vertex_index:obj.data.uv_layers.active.data[loop.index].uv.copy() for loop in obj.data.loops}
   for vertex in obj.data.vertices:
    u,t=coordinates[vertex.index];edge=.008*math.sin(u*113+phase)+.005*math.sin(u*197+1.7)+.004*math.sin(u*61+.4);vertex.co.z-=edge*t**5*(1-C['fin_edge_noise_gain'])
   obj.data.update()

bpy.ops.wm.read_factory_settings(use_empty=True);B.ROOT=bpy.data.objects.new('ASSET_PhotoInformed_'+slug,None);bpy.context.scene.collection.objects.link(B.ROOT);B.SLUG=slug
print('BUILD_MAPS',slug,flush=True);skin=pbr('Skin_Microstructure' if C['pattern']=='scaleless' else 'Skin_IndividualScales',skin_maps(),C.get('metallic',.055 if C['pattern']=='fine_scales' else .025));fm=fin_mat();body(skin);details();fins(fm)
sys.path.insert(0,str(HERE))
from filaments import build_filaments
build_filaments(B,C,profile,flank)
from filaments import build_pelvic_filaments,bind_pelvic_filaments
build_pelvic_filaments(B,C,profile)
from barbels import build_barbels
build_barbels(B,C,profile)
if C.get('dental_plates'):
 from beak import build_beak
 build_beak(B,C)
if C.get('lion_radial_fins'):
 from lion_fins import build_lion_fins
 build_lion_fins(B,R.fan,C,profile,flank,fm,fin_mat(spiny=True))
print('BIND_SWIM',slug,flush=True);rig=B.add_rig('bass')
bind_pelvic_filaments(rig)
from fanning import retarget_fanning
retarget_fanning(rig,C,profile)
if C.get('body_wave_gain'):
 for layer in rig.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     if 'Spine_' not in curve.data_path:continue
     for point in curve.keyframe_points:
      point.co.y*=C['body_wave_gain'];point.handle_left.y*=C['body_wave_gain'];point.handle_right.y*=C['body_wave_gain']
     curve.update()

sys.path.insert(0,str(HERE))
from fin_weights import attach_fin_roots
from timing import retime_swim
end_frame=retime_swim(rig,C.get('swim_seconds',3.0))
attach_fin_roots(bpy.context.scene,C.get('stabilizer_tip_blend',.85))
for o in B.ROOT.children_recursive:
 for mod in o.modifiers:
  if mod.type=='ARMATURE':mod.use_deform_preserve_volume=True
# Studio utility uses a neutral environment; no habitat hides anatomical detail.
spec=importlib.util.spec_from_file_location('studio',HERE.parent/'fish-realism-review'/'revision-03'/'create_review.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P);s=P.studio(OUT);s.camera.data.ortho_scale=C.get('preview_scale',4.6);s.camera.location=(-.15,-9,.85);P.aim(s.camera,(.14,0,C.get('preview_z',.02)));s.frame_set(13);s.frame_end=end_frame
# EEVEE provides an early owning-runtime sample close to the realtime viewer.
if '--quick-preview' in sys.argv:s.render.engine='BLENDER_EEVEE'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(slug+'.blend')));bpy.ops.render.render(write_still=True)
s.camera.location=(-1.15,-7,.55);P.aim(s.camera,(-1.03,0,.02));s.camera.data.ortho_scale=1.65;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True)
if C.get('pectoral_filaments'):
 s.camera.location=(-.2,-7,.25);P.aim(s.camera,(-.35,0,-.27));s.camera.data.ortho_scale=1.5;s.render.filepath=str(OUT/'filament-detail.png');bpy.ops.render.render(write_still=True)
print('GENERATED',slug,flush=True)

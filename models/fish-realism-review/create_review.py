"""Original Blender realism studies; isolated drafts, not gallery replacements.
Run with Blender 5.1: blender -b --python create_review.py -- barramundi
No downloaded code, photographs, or third-party assets are embedded.
"""
import bpy, math, sys, json, random
import numpy as np
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PI = math.pi
ROOT = None
SLUG = ''

def smoothstep(a, b, value):
    x = np.clip((value-a)/(b-a), 0, 1)
    return x*x*(3-2*x)

def image_file(name, data, folder, data_map=False):
    h,w = data.shape[:2]
    if data.ndim == 2: data = np.repeat(data[:,:,None],3,axis=2)
    rgba = np.concatenate((data[:,:,:3],np.ones((h,w,1))),axis=2).astype(np.float32)
    image = bpy.data.images.new(name,width=w,height=h,alpha=True,float_buffer=False)
    image.colorspace_settings.name = 'Non-Color' if data_map else 'sRGB'
    image.pixels.foreach_set(rgba.ravel())
    image.filepath_raw = str(folder/(name+'.png'));image.file_format='PNG';image.save();image.pack()
    return image

def material(name, color, rough=.35, metal=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return mat

def maps_material(name, images, metal=.45, rough=.3):
    mat=material(name,(.3,.35,.4),rough,metal);nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
    for channel,image in images.items():
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.label=channel
        if channel=='color':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        elif channel=='normal':
            normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.20
            nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
        elif channel=='rough':nt.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
    bs.inputs['Coat Weight'].default_value=.22;bs.inputs['Coat Roughness'].default_value=.18
    return mat

def body_maps(kind, folder):
    w,h=2048,1024;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h))
    rng=np.random.default_rng(123 if kind=='bass' else 227)
    ny=32 if kind=='bass' else 22;nx=60 if kind=='bass' else 35
    row=np.floor(v*ny);sx=np.mod(u*nx+row*.5,1)-.5;sy=np.mod(v*ny,1)
    r=np.sqrt((sx/.57)**2+((sy+.08)/1.05)**2)
    arc=np.exp(-((r-1)/.055)**2)
    scale=np.clip(1-r*r,0,1)
    jitter=(np.sin(np.floor(u*nx+row*.5)*73.13+row*19.71)*43758.54)%1
    mask=smoothstep(.24,.36,u)
    height=(scale*.65-arc*.22)*mask
    dy,dx=np.gradient(height)
    normal=np.stack((-dx*7,-dy*5,np.ones_like(u)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal=normal*.5+.5
    z=np.sin(v*2*PI)
    if kind=='bass':
        back=np.array([.29,.34,.31]);silver=np.array([.66,.70,.67]);belly=np.array([.86,.86,.78])
        dorsal=smoothstep(.22,.9,z)[...,None];ventral=smoothstep(.04,.9,-z)[...,None]
        color=silver*(1-dorsal)+back*dorsal;color=color*(1-ventral)+belly*ventral
        color*=1-mask[...,None]*(arc*.07+(jitter-.5)*.11)[...,None]
        color+=mask[...,None]*(scale*.035)[...,None]
        rough=.33+mask*arc*.045+rng.random(u.shape)*.025
    else:
        back=np.array([.025,.08,.12]);blue=np.array([.035,.37,.47]);belly=np.array([.07,.12,.18])
        dorsal=smoothstep(.1,.95,z)[...,None];ventral=smoothstep(.05,.9,-z)[...,None]
        color=blue*(1-dorsal)+back*dorsal;color=color*(1-ventral)+belly*ventral
        color*=1-mask[...,None]*(arc*.18+(jitter-.5)*.22)[...,None]
        color+=mask[...,None]*(scale*.025)[...,None]*np.array([.15,.8,1.])
        head=1-smoothstep(.1,.30,u);color=color*(1-head[...,None]*.65)+np.array([.015,.036,.05])*head[...,None]*.65
        rough=.30+mask*arc*.09+rng.random(u.shape)*.03
    color=np.clip(color+(rng.random(color.shape)-.5)*.017+(np.sin(u*43+np.sin(v*11))*np.sin(v*19+u*17)*.013)[...,None],0,1)
    return {'color':image_file(kind+'_skin_color',color,folder),'normal':image_file(kind+'_skin_normal',normal,folder,True),'rough':image_file(kind+'_skin_roughness',rough,folder,True)}

def mesh(name, vertices, faces, mat, uv=None, deform='body'):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);obj.parent=ROOT;data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    if uv is not None:
        layer=data.uv_layers.new(name='UVMap')
        for poly in data.polygons:
            for li in poly.loop_indices:layer.data[li].uv=uv[data.loops[li].vertex_index]
    obj['deform_role']=deform
    return obj

def sphere(name, location, size, mat, deform='body'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=location)
    obj=bpy.context.object;obj.name=name;obj.scale=size;obj.parent=ROOT;obj.data.materials.append(mat);obj['deform_role']=deform
    for p in obj.data.polygons:p.use_smooth=True
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return obj

def tube(name, points, radius, mat, deform='body'):
    # Direct mesh construction avoids a whole-scene dependency rebuild per tiny fin ray.
    points=[Vector(p) for p in points];vertices=[];faces=[];around=10
    for i,p in enumerate(points):
        tangent=points[min(i+1,len(points)-1)]-points[max(0,i-1)]
        if tangent.length<1e-9:tangent=Vector((1,0,0))
        tangent.normalize();up=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((0,1,0))
        n=tangent.cross(up).normalized();b=tangent.cross(n).normalized()
        for j in range(around):
            a=2*PI*j/around;vertices.append(tuple(p+radius*(math.cos(a)*n+math.sin(a)*b)))
    for i in range(len(points)-1):
        for j in range(around):
            a=i*around+j;z=i*around+(j+1)%around;faces.append((a,z,z+around,a+around))
    faces.extend([tuple(range(around-1,-1,-1)),tuple((len(points)-1)*around+j for j in range(around))])
    return mesh(name,vertices,faces,mat,deform=deform)

def interp(points, x):
    # Hermite interpolation keeps the silhouette smooth without overshooting widths.
    xs=[p[0] for p in points];i=max(0,min(len(points)-2,int(np.searchsorted(xs,x)-1)))
    x0,x1=xs[i:i+2];t=max(0,min(1,(x-x0)/(x1-x0)));a=points[i][1];b=points[i+1][1]
    m0=(b-points[max(i-1,0)][1])/(x1-xs[max(i-1,0)])
    m1=(points[min(i+2,len(points)-1)][1]-a)/(xs[min(i+2,len(points)-1)]-x0)
    return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*m0*(x1-x0)+(-2*t**3+3*t*t)*b+(t**3-t*t)*m1*(x1-x0)

PROFILES={}
def build_body(kind, mat):
    if kind=='bass':
        xs=[-1.8,-1.62,-1.3,-.95,-.48,0,.5,.9,1.22,1.43]
        top=[.115,.195,.255,.40,.52,.50,.38,.25,.145,.13]
        bottom=[-.018,-.13,-.28,-.38,-.43,-.41,-.30,-.19,-.12,-.105]
        width=[.025,.085,.17,.24,.28,.265,.21,.135,.076,.065]
    else:
        xs=[-1.08,-.93,-.74,-.48,-.12,.25,.55,.76]
        top=[.07,.19,.26,.29,.27,.21,.14,.11]
        bottom=[-.015,-.12,-.21,-.245,-.22,-.16,-.10,-.085]
        width=[.022,.075,.115,.145,.137,.10,.065,.045]
    PROFILES[kind]=[list(zip(xs,v)) for v in [top,bottom,width]]
    vertices=[];uv=[];faces=[];n,m=140,96
    for i in range(n+1):
        u=i/n;x=xs[0]+u*(xs[-1]-xs[0]);hi,lo,wid=[interp(p,x) for p in PROFILES[kind]]
        for j in range(m+1):
            theta=2*PI*j/m;z=(hi+lo)/2+(hi-lo)/2*math.sin(theta);y=wid*math.cos(theta)
            vertices.append((x,y,z));uv.append((u,j/m))
    for i in range(n):
        for j in range(m):
            a=i*(m+1)+j;faces.append((a,a+1,a+m+2,a+m+1))
    faces.extend([tuple(range(m,-1,-1)),tuple(n*(m+1)+j for j in range(m+1))])
    return mesh('Skin_AnatomicalBody',vertices,faces,mat,uv)

def flank(kind,x,z,side,offset=.003):
    hi,lo,w=[interp(p,x) for p in PROFILES[kind]]
    return side*(w*math.sqrt(max(.02,1-((z-(hi+lo)/2)/((hi-lo)/2))**2))+offset)

def eyes(kind):
    dark=material('Eye_BlackPupil',(.0015,.003,.004),.085,.05)
    iris=material('Eye_Iris',(.20,.135,.037) if kind=='bass' else (.045,.075,.055),.35,.18)
    rim=material('Eye_Socket',(.045,.065,.055),.40,.1)
    cornea=material('Eye_Cornea',(.8,.9,.95),.07);bs=cornea.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.36
    for side in [-1,1]:
        x,z,r=(-1.27,.18,.069) if kind=='bass' else (-.88,.105,.041)
        y=flank(kind,x,z,side,-.003)
        sphere('EyeSocket', (x,y,z),(r*1.17,r*.26,r*1.17),rim)
        sphere('Iris', (x,y+side*r*.17,z),(r,r*.27,r),iris)
        # Narrow radial iris fibers are actual mesh, not large painted eye whites.
        for j in range(54):
            a=2*PI*j/54;rr=r*(.63+.12*math.sin(j*7.13))
            pts=[(x+rr*math.cos(a),y+side*r*.40,z+rr*math.sin(a)),(x+r*.91*math.cos(a+.009),y+side*r*.32,z+r*.91*math.sin(a+.009))]
            tube('IrisFiber',pts,r*.011,dark)
        sphere('Pupil',(x,y+side*r*.42,z),(r*.55,r*.13,r*.61),dark)
        sphere('ClearCornea',(x,y+side*r*.20,z),(r*1.005,r*.40,r*1.005),cornea)

def head_details(kind):
    dark=material('MouthAndGill_Recess',(.027,.037,.033),.48)
    lip=material('Jaw_WetSkin',(.30,.34,.29) if kind=='bass' else (.022,.065,.08),.31,.18)
    for side in [-1,1]:
        if kind=='bass':
            raw=[(-1.79,.057),(-1.65,.024),(-1.43,-.045),(-1.18,-.105),(-1.03,-.085)]
            gill=[(-.97,.32),(-.77,.27),(-.67,.13),(-.66,-.06),(-.79,-.27),(-.96,-.31)]
        else:
            raw=[(-1.072,.052),(-.99,.015),(-.89,-.005)]
            gill=[(-.70,.205),(-.58,.13),(-.56,-.03),(-.67,-.16)]
        pts=[]
        for k in range(len(raw)-1):
            a,b=raw[k:k+2]
            for t in np.linspace(0,1,12):
                x,z=(1-t)*np.array(a)+t*np.array(b);pts.append((x,flank(kind,x,z,side),z))
        tube('Mouth_ClosedJawSeam',pts,.0025 if kind=='bass' else .0017,dark)
        tube('LowerLip_SubtleRidge',[(x,y,z-.004) for x,y,z in pts[:18]],.0025 if kind=='bass' else .0017,lip)
        pts=[]
        for k in range(len(gill)-1):
            a,b=gill[k:k+2]
            for t in np.linspace(0,1,12):
                x,z=(1-t)*np.array(a)+t*np.array(b);pts.append((x,flank(kind,x,z,side,.002),z))
        tube('Operculum_RecessedEdge',pts,.002 if kind=='bass' else .0015,dark)
        x,z=(-1.57,.135) if kind=='bass' else (-.99,.115)
        sphere('Nostril',(x,flank(kind,x,z,side,.003),z),(.014,.003,.008) if kind=='bass' else (.006,.002,.004),dark)
    if kind=='bass':
        mat=material('LateralLine_Pores',(.19,.24,.21),.39,.2)
        for side in [-1,1]:
            pts=[]
            for x in np.linspace(-.57,1.34,110):
                z=.075+.035*math.sin((x+.55)*1.5);pts.append((x,flank(kind,x,z,side,.003),z))
            tube('LateralLine',pts,.0023,mat)

FIN_CACHE={}
def fin_material(kind,folder):
    if kind in FIN_CACHE:return FIN_CACHE[kind]
    w,h=1024,1024;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h))
    rays=(.5+.5*np.cos(u*PI*2*(42 if kind=='betta' else 24)))**20
    fine=(.5+.5*np.cos(u*PI*2*(84 if kind=='betta' else 48)+v*5))**30
    if kind=='betta':
        edge=smoothstep(.35,.90,v+.10*np.sin(u*9))[...,None]
        color=np.array([.03,.28,.40])*(1-edge)+np.array([.52,.027,.045])*edge
        color*=1-(rays*.16+fine*.06)[...,None]
        color+=((1-edge)*np.array([.025,.08,.10]))*(.5+.5*np.sin(u*210+v*7))[...,None]*.22
    elif kind=='bass':
        color=np.zeros((h,w,3))+np.array([.35,.40,.35]);color*=(.87+.13*v)[...,None];color*=1-(rays*.25+fine*.06)[...,None]
    else:color=np.zeros((h,w,3))+np.array([.48,.53,.48]);color*=1-(rays*.22)[...,None]
    mat=maps_material('Fin_'+kind,{'color':image_file('fin_'+kind+'_color',color,folder)},metal=.025 if kind=='betta' else .04,rough=.48)
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=0
    bs.inputs['Coat Weight'].default_value=.035;bs.inputs['Subsurface Weight'].default_value=0
    bs.inputs['Subsurface Weight'].default_value=0;bs.inputs['IOR'].default_value=1.36
    # Thin-sheet translucency preserves visible membranes under backlighting.
    nt=mat.node_tree;out=nt.nodes.get('Material Output');trans=nt.nodes.new('ShaderNodeBsdfTransparent' if kind=='clear' else 'ShaderNodeBsdfTranslucent');trans.inputs[0].default_value=(1,1,1,1) if kind=='clear' else (.12,.16,.17,1)
    mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.70 if kind=='clear' else .20
    nt.links.new(bs.outputs['BSDF'],mix.inputs[1]);nt.links.new(trans.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
    FIN_CACHE[kind]=mat;return mat

def fan(name, root_fn, edge_fn, mat, n=128, m=28, flutter=.018, role='tail', phase=0):
    vertices=[];uv=[];faces=[]
    for i in range(n+1):
        u=i/n;a=np.array(root_fn(u));b=np.array(edge_fn(u))
        for j in range(m+1):
            t=j/m;p=a*(1-t)+b*t
            p[1]+=flutter*t*t*(math.sin(u*PI*2*5+phase+t*1.6)+.15*math.sin(u*PI*2*19+t*2))
            if SLUG=='betta':
                if role=='tail':p[1]-=.06*t
                elif role in ['dorsal','anal']:p[1]+=.025*t
            vertices.append(tuple(p));uv.append((u,t))
    for i in range(n):
        for j in range(m):
            a=i*(m+1)+j;faces.append((a,a+m+1,a+m+2,a+1))
    return mesh(name,vertices,faces,mat,uv,deform=role)

def barramundi(folder):
    build_body('bass',maps_material('Barramundi_SilverScales',body_maps('bass',folder),.44,.34));eyes('bass');head_details('bass')
    fm=fin_material('bass',folder);raymat=material('FinRay_Silver',(.28,.31,.25),.42,.12)
    def tail_edge(u):
        a=-1.40+2.80*u;r=.52*(1-.022*math.cos(u*PI*2*18));return (1.57+.60*math.cos(a),0,r*math.sin(a))
    fan('Caudal_RoundedRayMembrane',lambda u:(1.36,0,(u-.5)*.17),tail_edge,fm,flutter=.010)
    for i in range(19):
        u=i/18;a=np.array((1.36,0,(u-.5)*.17));b=np.array(tail_edge(u));tube('Caudal_FinRay',[tuple(a*(1-t)+b*t+np.array([0,-.002,.001])) for t in np.linspace(0,1,24)],.0025,raymat,'tail')
    spine_x=[-.87,-.70,-.50,-.30,-.10,.05,.18,.28]
    spine_z=[.58,.79,.87,.83,.76,.66,.56,.48]
    def edge(u):
        t=u*7;i=min(6,int(t));f=t-i
        x=(1-f)*spine_x[i]+f*spine_x[i+1];z=(1-f)*spine_z[i]+f*spine_z[i+1]-.08*math.sin(PI*f)
        return (x,0,z)
    fan('Dorsal_FirstEightSpines',lambda u:(-.87+1.15*u,0,interp(PROFILES['bass'][0],-.87+1.15*u)*.985),edge,fm,flutter=.005,role='dorsal')
    for x,z in zip(spine_x,spine_z):tube('Dorsal_Spine',[(x,0,interp(PROFILES['bass'][0],x)*.97),(x-.015,0,z)],.0035,raymat,'dorsal')
    fan('Dorsal_SecondSoftRays',lambda u:(.25+.94*u,0,interp(PROFILES['bass'][0],.25+.94*u)),lambda u:(.26+.97*u,0,interp(PROFILES['bass'][0],.26+.97*u)+.35*math.sin(PI*u)**.52),fm,flutter=.008,role='dorsal')
    fan('Anal_Rounded',lambda u:(.30+.85*u,0,interp(PROFILES['bass'][1],.30+.85*u)),lambda u:(.32+.86*u,0,interp(PROFILES['bass'][1],.32+.86*u)-.29*math.sin(PI*u)**.6),fm,flutter=.009,role='anal')
    for side in [-1,1]:
        fan('Pectoral_'+str(side),lambda u:(-.70,side*.22,-.06+(u-.5)*.08),lambda u:(-.16+.19*math.cos((u-.5)*PI),side*(.42+.12*math.cos((u-.5)*PI)),-.15+(u-.5)*.36),fin_material('clear',folder),n=64,m=24,flutter=.008,role='pectoral')
        fan('Pelvic_'+str(side),lambda u:(-.39,side*.12,-.39),lambda u:(-.13+.32*u,side*(.18+.15*math.sin(PI*u)),-.40-.25*math.sin(PI*u)),fm,n=64,m=20,flutter=.005,role='anal')

def betta(folder):
    build_body('betta',maps_material('Betta_IridescentScales',body_maps('betta',folder),.44,.35));eyes('betta');head_details('betta')
    fm=fin_material('betta',folder)
    def edge(u):
        a=-PI*.485+PI*.97*u;r=1.04*(1+.006*math.sin(u*PI*2*41)+.012*math.sin(u*PI*2*7))
        return (.77+r*math.cos(a),.025*math.sin(a*2),r*math.sin(a))
    fan('Caudal_HalfmoonPleatedMembrane',lambda u:(.68,0,(u-.5)*.16),edge,fm,n=240,m=48,flutter=.022,role='tail',phase=.6)
    # Ribs branch toward the trailing edge instead of a few triangular spikes.
    rib=material('FinRays_DeepCrimson',(.16,.013,.028),.45,.12)
    for i in range(37):
        u=i/36;a=np.array((.68,0,(u-.5)*.16));b=np.array(edge(u))
        pts=[]
        for t in np.linspace(.04,1,42):
            p=a*(1-t)+b*t;p[1]+=.022*t*t*(math.sin(u*PI*2*5+.6+t*1.6)+.15*math.sin(u*PI*2*19+t*2))-.001
            p[1]-=.06*t
            pts.append(p)
        tube('Caudal_PrimaryRay',pts,.0015,rib,'tail')
    fan('Dorsal_SoftFlowingFin',lambda u:(-.48+1.22*u,0,interp(PROFILES['betta'][0],-.48+1.22*u)),lambda u:(-.46+1.62*u,0,.28+.47*math.sin(PI*u)**.67+.13*u+.009*math.sin(u*PI*2*23)),fm,n=160,m=40,flutter=.018,role='dorsal',phase=1)
    fan('Anal_LongFlowingFin',lambda u:(-.72+1.45*u,0,interp(PROFILES['betta'][1],-.72+1.45*u)),lambda u:(-.65+1.82*u,0,-.19-.64*math.sin(PI*u)**.62-.1*u+.008*math.sin(u*PI*2*28)),fm,n=180,m=40,flutter=.025,role='anal',phase=2)
    clear=fin_material('clear',folder)
    for side in [-1,1]:
        fan('Pectoral_'+str(side),lambda u:(-.63,side*.125,-.02),lambda u:(-.27+.09*math.cos(PI*(u-.5)),side*(.26+.04*math.sin(PI*u)),-.015+.20*(u-.5)),clear,n=64,m=20,flutter=.01,role='pectoral')
        fan('Pelvic_TaperedStreamer_'+str(side),lambda u:(-.63,side*.08,-.15),lambda u:(-.50+.22*u,side*(.12+.03*math.sin(u*4)),-.27-.50*math.sin(PI*u)**.8),fm,n=60,m=24,flutter=.012,role='anal')

def ray_maps(folder):
    w=h=1536;u,v=np.meshgrid(np.linspace(-1.5,1.7,w),np.linspace(-1.5,1.5,h));rng=np.random.default_rng(219)
    grain=rng.random(u.shape);waves=np.sin(u*9+np.sin(v*7))*np.cos(v*13-u*5)
    color=np.zeros((*u.shape,3))+np.array([.38,.32,.21]);color+=(waves*.045+(grain-.5)*.035)[...,None]
    for i in range(77):
        x,y=rng.uniform(-1.16,1.10),rng.uniform(-1.12,1.12)
        if abs(y)>.94-.38*abs(x) or (x+.25)**2+(y*.9)**2<.04:continue
        radius=rng.uniform(.025,.052);d=np.sqrt((u-x)**2+(v-y)**2)
        edge=1-smoothstep(radius*.70,radius*1.20,d);halo=(1-smoothstep(radius*1.15,radius*1.4,d))*.22
        color=color*(1-halo[...,None])+np.array([.095,.12,.09])*halo[...,None]
        color=color*(1-edge[...,None])+np.array([.025,.22,.40])*edge[...,None]
        core=1-smoothstep(radius*.15,radius*.75,d);color+=core[...,None]*np.array([.005,.025,.055])
    # The dark eye mask is pigment integrated in the texture.
    mask=np.exp(-((u+.60)/.27)**4-((v)/.44)**6)*.5;color*=1-mask[...,None]
    rough=.56+(grain-.5)*.11
    normal=np.stack((.5+(grain-.5)*.16,.5+(rng.random(u.shape)-.5)*.16,np.ones_like(u)),axis=-1)
    return {'color':image_file('ray_dorsal_color',np.clip(color,0,1),folder),'normal':image_file('ray_microdenticle_normal',normal,folder,True),'rough':image_file('ray_roughness',rough,folder,True)}

def stingray(folder):
    skin=maps_material('Maskray_SandAndBluePigment',ray_maps(folder),.0,.56)
    skin.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.035
    belly=material('Ray_VentralIvory',(.58,.59,.49),.5)
    # Rounded rhomboid boundary: the pectoral disc is continuous and cambered.
    angles=np.array([0,.40,.78,1.10,1.57,2.08,2.55,PI,3.73,4.2,4.71,5.18,5.65,2*PI])
    radii=np.array([1.02,1.10,1.40,1.39,1.32,1.10,1.05,1.26,1.05,1.10,1.32,1.39,1.40,1.02])
    vertices=[];uv=[];faces=[];n,m=224,60
    for bottom in [False,True]:
        for j in range(m+1):
            t=max(.0003,j/m)
            for i in range(n):
                a=2*PI*i/n;r=interp(list(zip(angles,radii)),a)*t
                x=r*math.cos(a);y=r*math.sin(a)
                core=.16*math.exp(-((x+.37)/.70)**2-(y/.30)**2)
                z=core+.020+.035*(1-t*t)+.018*t**5*math.sin(a*5+.6)
                z+=.075*math.exp(-((x+.66)/.16)**2-((abs(y)-.20)/.11)**2)
                if bottom:z=-.025-.055*(1-t*t)-core*.34+.012*t**5*math.sin(a*5+.6)
                vertices.append((x,y,z));uv.append(((x+1.5)/3.2,(y+1.5)/3))
    for side in [0,1]:
        offset=side*(m+1)*n
        for j in range(m):
            for i in range(n):
                a=offset+j*n+i;b=offset+j*n+(i+1)%n;face=(a,b,b+n,a+n)
                faces.append(face[::-1] if side==0 else face)
    for i in range(n):
        a=m*n+i;b=m*n+(i+1)%n;off=(m+1)*n;faces.append((a,off+a,off+b,b))
    body=mesh('Ray_ContinuousCamberedDisc',vertices,faces,skin,uv,deform='wing');body.data.materials.append(belly)
    for p in body.data.polygons:
        if p.index>=m*n:p.material_index=1
    dark=material('Ray_SpiracleAndEye',(.017,.021,.013),.28)
    iris=material('Ray_BronzeIris',(.13,.14,.075),.24,.4)
    cavity=material('Ray_GillAndSpiracleCavity',(.006,.004,.003),1)
    cavity.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=0
    for side in [-1,1]:
        x,y=-.705,side*.20
        sphere('Ray_Eye',(x,y,.213),(.051,.036,.022),dark)
        sphere('Ray_IrisFleck',(x-.012,y,.229),(.023,.020,.005),iris)
        sphere('Ray_Pupil',(x-.019,y,.232),(.019,.015,.005),dark)
        # Eye mounds are sculpted into the continuous skin mesh, never detached balls.
        rim=material('Ray_EyelidSkin_'+str(side),(.19,.15,.085),.57)
        pts=[(-.665+.075*math.cos(a),side*.20+.049*math.sin(a),.219+.006*math.cos(a)) for a in np.linspace(-PI*.45,PI*.45,44)]
        tube('Ray_UpperEyelid',pts,.006,rim)
        # Recesses sit flush with the local disc, rather than raised oval buttons.
        sphere('Ray_Spiracle',(-.40,side*.245,.143),(.078,.034,.008),cavity)
        pts=[(-.40+.080*math.cos(a),side*.245+.036*math.sin(a),.147+.003*math.sin(a)) for a in np.linspace(0,2*PI,64)]
        tube('Ray_SpiracleRim',pts,.0035,rim)
        for j in range(5):
            x=-.55+j*.13;tube('Ventral_GillSlit',[(x,side*(.22+.018*k),-.105-.01*math.sin(k/8*PI)) for k in range(9)],.006,dark)
    # A true tapered 3D whip tail with distal bands and a swept barb.
    vertices=[];uv=[];faces=[];count=180;around=20
    centers=[]
    for i in range(count+1):
        t=i/count;x=.70+3.25*t;y=.10*math.sin(t*PI)+.28*t*t;z=.02-.13*t+.15*t*t
        centers.append((x,y,z));radius=.071*(1-t)**1.6+.0035
        for j in range(around+1):
            a=2*PI*j/around;vertices.append((x,y+radius*math.cos(a),z+radius*.7*math.sin(a)));uv.append((t,j/around))
    for i in range(count):
        for j in range(around):
            a=i*(around+1)+j;faces.append((a,a+1,a+around+2,a+around+1))
    tail_skin=material('Ray_TailSkin',(.20,.155,.09),.53)
    tail=mesh('Ray_TaperedWhipTail',vertices,faces,tail_skin,uv,deform='tail');band=material('Tail_DarkBands',(.025,.031,.025),.48);tail.data.materials.append(band)
    for p in tail.data.polygons:
        t=p.center.x
        if t>2.0 and int(t*8)%2==0:p.material_index=1
    tube('Ray_TailBarb',[(1.0,0,.065),(1.18,.008,.12),(1.48,.025,.13),(1.66,.03,.11)],.012,band,'tail')
    # Small non-cartoon ventral mouth, only visible from below.
    tube('Ray_VentralMouth',[(-.91,.14*math.cos(a),-.115-.008*math.sin(a)) for a in np.linspace(0,PI,40)],.007,dark)

def add_rig(kind):
    objects=[o for o in ROOT.children_recursive if o.type=='MESH'];data=bpy.data.armatures.new('AnatomicalSwimSkeleton');rig=bpy.data.objects.new('Swim_Armature',data);bpy.context.scene.collection.objects.link(rig);rig.parent=ROOT
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    xs=([-1.8,-.8,-.15,.45,.95,1.4,1.8] if kind=='bass' else [-1.1,-.5,-.1,.35,.7,1.1,1.6] if kind=='betta' else [-1.3,-.5,.2,.8,1.5,2.4,3.3]);names=[]
    for i,x in enumerate(xs):
        bone=data.edit_bones.new('Spine_%02d'%i);bone.head=(x,0,0);bone.tail=(xs[i+1] if i<6 else x+.4,0,0)
        if i:bone.parent=data.edit_bones[names[-1]];bone.use_connect=True
        names.append(bone.name)
    if kind!='ray':
        for label,head,tail in [('Dorsal',(0,0,.19),(.1,0,.65)),('Anal',(0,0,-.19),(.1,0,-.65)),('Pectoral_L',(-.6,.10,0),(-.2,.40,-.1)),('Pectoral_R',(-.6,-.10,0),(-.2,-.40,-.1))]:
            bone=data.edit_bones.new(label);bone.head=head;bone.tail=tail;bone.parent=data.edit_bones[names[2] if label in ['Dorsal','Anal'] else names[1]]
    if kind=='ray':
        for side in [-1,1]:
            previous=names[1]
            for i in range(3):
                bone=data.edit_bones.new('Wing_%s_%d'%('L' if side>0 else 'R',i));bone.head=(-.15,side*i*.40,.03);bone.tail=(-.15,side*(i+1)*.40,.03);bone.parent=data.edit_bones[previous];previous=bone.name
    bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
    for obj in objects:
        groups={b.name:obj.vertex_groups.new(name=b.name) for b in data.bones};transform=obj.matrix_local
        for v in obj.data.vertices:
            p=transform@v.co
            if kind=='ray' and obj.get('deform_role')=='wing':
                t=min(2.999,abs(p.y)/.4);i=int(t);f=t-i;label='L' if p.y>0 else 'R';weights={('Spine_01' if i==0 else 'Wing_%s_%d'%(label,i-1)):1-f,'Wing_%s_%d'%(label,i):f}
            else:
                i=max(0,min(5,int(np.searchsorted(xs,p.x)-1)));f=max(0,min(1,(p.x-xs[i])/(xs[i+1]-xs[i])));weights={names[i]:1-f,names[i+1]:f}
            role=obj.get('deform_role');extra=None;blend=0
            if kind!='ray':
                if role=='dorsal':extra='Dorsal';blend=min(.90,max(0,(p.z-.30)/.45))
                elif role=='anal':extra='Anal';blend=min(.90,max(0,(-p.z-.26)/.45))
                elif role=='pectoral':extra='Pectoral_L' if p.y>0 else 'Pectoral_R';blend=min(.92,max(0,(abs(p.y)-.13)/.25))
            if extra:
                weights={name:value*(1-blend) for name,value in weights.items()};weights[extra]=blend
            for name,value in weights.items():
                if value>1e-6:groups[name].add([v.index],value,'REPLACE')
        mod=obj.modifiers.new('Swim_Deformation','ARMATURE');mod.object=rig
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=73
    for f in range(1,74,2):
        phase=2*PI*(f-1)/72
        for i,name in enumerate(names):
            pb=rig.pose.bones[name];pb.rotation_mode='XYZ';amp=.025 if kind=='ray' else .065 if kind=='bass' else .095
            pb.rotation_euler=(0,0,amp*(i/6)**1.5*math.sin(phase-i*.65));pb.keyframe_insert(data_path='rotation_euler',frame=f,group=name)
        if kind!='ray':
            for k,name in enumerate(['Dorsal','Anal','Pectoral_L','Pectoral_R']):
                pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler=(.065*math.sin(phase+k*.7),0,.035*math.sin(phase+k*.7));pb.keyframe_insert(data_path='rotation_euler',frame=f,group=name)
        if kind=='ray':
            for side in [-1,1]:
                for i in range(3):
                    pb=rig.pose.bones['Wing_%s_%d'%('L' if side>0 else 'R',i)];pb.rotation_mode='XYZ';pb.rotation_euler=(side*(.065+.025*i)*math.sin(phase-i*.65),0,0);pb.keyframe_insert(data_path='rotation_euler',frame=f,group=pb.name)
    rig.animation_data.action.name='Swim_Loop';scene.frame_set(1)
    return rig

def aim(obj, target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def studio(kind,folder):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.time_limit=90
    scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=4;scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
    scene.cycles.device='CPU'
    scene.render.threads_mode='FIXED';scene.render.threads=6
    scene.render.resolution_x=1280;scene.render.resolution_y=854;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('DeepBlueStudio');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.035,.055,.065,1);bg.inputs[1].default_value=.35
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=-.35 if kind=='ray' else 0
    for name,location,power,size,color in [('Large_Softbox',(-2,-3,5),700,5,(.84,.94,1)),('Warm_Fill',(1,-4,1),220,4,(1,.88,.72)),('Upper_Rim',(1,3,3),950,3,(.68,.85,1)),('Front_Strip',(-4,0,1),280,2,(.78,.95,1))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=location;aim(obj,(0,0,0))
    floor=material('Studio_Backdrop',(.013,.029,.036),.65)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.55 if kind!='ray' else -.90));obj=bpy.context.object;obj.name='STUDIO_Floor';obj.data.materials.append(floor)
    camera_data=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
    if kind=='ray':camera.location=(-3.2,-5.3,6.4);target=(1.05,0,0);scale=6.5
    elif kind=='bass':camera.location=(-.8,-8,1.2);target=(.1,0,.1);scale=5.2
    else:camera.location=(-.25,-7,.95);target=(.37,0,0);scale=3.9
    aim(camera,target);camera_data.type='ORTHO';camera_data.ortho_scale=scale;camera_data.lens=55
    scene.render.filepath=str(folder/'preview.png')
    scene['review_status']='Awaiting user approval; not deployed';scene['provenance']='Original geometry and generated texture maps; no third-party asset dependencies'
    return camera

def main(slug):
    global ROOT,SLUG
    SLUG=slug;kind={'barramundi':'bass','betta':'betta','stingray':'ray'}[slug];folder=HERE/slug;folder.mkdir(parents=True,exist_ok=True);texture_dir=folder/'textures';texture_dir.mkdir(exist_ok=True)
    FIN_CACHE.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ROOT=bpy.data.objects.new('ASSET_RealismReview_'+slug,None);bpy.context.scene.collection.objects.link(ROOT)
    ROOT['style']='Realism direction study';ROOT['species']='Lates calcarifer' if kind=='bass' else 'Neotrygon kuhlii complex (visual reference)' if kind=='ray' else 'Betta splendens, ornamental halfmoon male'
    print('BUILD_GEOMETRY',slug,flush=True)
    {'bass':barramundi,'betta':betta,'ray':stingray}[kind](texture_dir)
    print('BUILD_RIG',slug,flush=True)
    rig=add_rig(kind);studio(kind,folder)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'-realism-review.blend')))
    print('RENDER_PREVIEW',slug,flush=True)
    bpy.ops.render.render(write_still=True)
    report={'slug':slug,'blender':bpy.app.version_string,'meshes':sum(o.type=='MESH' for o in ROOT.children_recursive),'vertices':sum(len(o.data.vertices) for o in ROOT.children_recursive if o.type=='MESH'),'bones':len(rig.data.bones),'clip':'Swim_Loop','textures':len(list(texture_dir.glob('*.png'))),'packed_images':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'draft':True}
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('REVIEW_COMPLETE',json.dumps(report))

if __name__=='__main__':
    slugs=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['barramundi','stingray','betta']
    for slug in slugs:main(slug)

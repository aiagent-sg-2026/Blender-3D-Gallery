"""Photo-informed second review. Original texture synthesis and Blender geometry.
Only the three isolated drafts are authored; production assets are never replaced.
"""
import bpy, math, sys, json, importlib.util
import numpy as np
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('review_base',HERE.parent/'create_review.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
B.HERE=HERE
PI=math.pi
smoothstep=B.smoothstep


def noise(u,v,nx,ny,seed):
    rng=np.random.default_rng(seed);grid=rng.random((ny+2,nx+2));grid[-2:]=grid[:2]
    x=np.mod(u,1)*nx;y=np.mod(v,1)*ny;ix=x.astype(int);iy=y.astype(int);fx=x-ix;fy=y-iy
    fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
    return (grid[iy,ix]*(1-fx)+grid[iy,ix+1]*fx)*(1-fy)+(grid[iy+1,ix]*(1-fx)+grid[iy+1,ix+1]*fx)*fy


def image_file(name,data,folder,data_map=False):
    """Reload the saved PNG so generated-image color handling cannot affect shading."""
    h,w=data.shape[:2]
    if data.ndim==2:data=np.repeat(data[:,:,None],3,axis=2)
    if data.shape[2]==3:data=np.concatenate((data,np.ones((h,w,1))),axis=2)
    image=bpy.data.images.new(name+'_writer',width=w,height=h,alpha=True,float_buffer=False)
    image.colorspace_settings.name='Non-Color' if data_map else 'sRGB'
    image.pixels.foreach_set(np.clip(data,0,1).astype(np.float32).ravel())
    path=folder/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save()
    bpy.data.images.remove(image)
    image=bpy.data.images.load(str(path),check_existing=False);image.name=name
    image.colorspace_settings.name='Non-Color' if data_map else 'sRGB';image.pack()
    return image


def normals(height,scale=1):
    dy,dx=np.gradient(height);n=np.stack((-dx*scale,-dy*scale,np.ones_like(height)),axis=-1)
    n/=np.linalg.norm(n,axis=-1,keepdims=True);return n*.5+.5


def maps_material(name,images,metal=.12,rough=.4):
    mat=B.material(name,(.18,.20,.18),rough,min(metal,.22));nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
    for channel,img in images.items():
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;tex.label=channel
        if channel=='color':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        elif channel=='rough':nt.links.new(tex.outputs['Color'],bs.inputs['Roughness'])
        elif channel=='normal':
            node=nt.nodes.new('ShaderNodeNormalMap');node.inputs['Strength'].default_value=.38
            nt.links.new(tex.outputs['Color'],node.inputs['Color']);nt.links.new(node.outputs[0],bs.inputs['Normal'])
    bs.inputs['Coat Weight'].default_value=.055;bs.inputs['Coat Roughness'].default_value=.25
    bs.inputs['Specular IOR Level'].default_value=.34
    return mat


def body_maps(kind,folder):
    w,h=2048,1024;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));rng=np.random.default_rng(532 if kind=='bass' else 733)
    coarse=noise(u,v,13,12,17);medium=noise(u,v,85,62,18);micro=noise(u,v,380,290,19);grain=rng.random(u.shape)-.5
    z=np.sin(v*PI*2)
    if kind=='bass':
        back=np.array([.19,.22,.205]);side=np.array([.47,.51,.50]);belly=np.array([.68,.70,.64])
        a=smoothstep(.05,.88,z)[...,None];base=side*(1-a)+back*a
        a=smoothstep(.05,.88,-z)[...,None];base=base*(1-a)+belly*a
        base+=((coarse-.5)*.06+(medium-.5)*.017)[...,None]
        nx,ny=55,35
    else:
        back=np.array([.025,.045,.085]);side=np.array([.025,.19,.45]);belly=np.array([.06,.028,.075])
        a=smoothstep(.10,.90,z)[...,None];base=side*(1-a)+back*a
        a=smoothstep(.1,.85,-z)[...,None];base=base*(1-a)+belly*a
        a=1-smoothstep(.075,.27,u);base=base*(1-a[...,None]*.75)+np.array([.028,.025,.033])*a[...,None]*.75
        nx,ny=34,25
    color=base.copy();height=(micro-.5)*.008+grain*.003;rough=.35+(coarse-.5)*.08+grain*.025
    tilt_x=np.zeros_like(u);tilt_y=np.zeros_like(u)
    tiles=[]
    for row in range(-1,ny+1):
        for col in range(-1,nx+1):
            cx=(col+.5*(row%2)+rng.uniform(-.18,.18))/nx;cy=(row+.5+rng.uniform(-.13,.13))/ny
            cx+=(.16*math.sin(cy*PI*7)+.08*math.sin(cy*PI*17))/nx
            cy+=(.16*math.sin(cx*PI*3)+.08*math.sin(cx*PI*13))/ny
            tiles.append((cx,cy,rng.uniform(.78,1.06),rng.uniform(.59,.77),rng.uniform(-.15,.15),rng.uniform(-1,1),rng.random()))
    # Actual overlapping ellipses painted from posterior to anterior avoid hard cell seams.
    for cx,cy,rx,ry,angle,pigment,hue in sorted(tiles,key=lambda t:-t[0]):
        x0=max(0,int((cx-1.1/nx)*w));x1=min(w,int((cx+1.1/nx)*w)+1)
        y0=max(0,int((cy-.9/ny)*h));y1=min(h,int((cy+.9/ny)*h)+1)
        if x1<=x0 or y1<=y0:continue
        px=(u[y0:y1,x0:x1]-cx)*nx;py=(v[y0:y1,x0:x1]-cy)*ny
        xx=px*math.cos(angle)+py*math.sin(angle);yy=-px*math.sin(angle)+py*math.cos(angle)
        distance=np.sqrt((xx/rx)**2+(yy/ry)**2)
        mask=(1-smoothstep(.90,1.0,distance))*smoothstep(.035,.20,u[y0:y1,x0:x1])
        posterior=smoothstep(-.45,.4,xx/rx)
        rim=np.exp(-((distance-.94)/.032)**2)*posterior
        # Neighboring scales differ slightly, with interrupted silver lips and fine pigment.
        rim*=.65+.35*medium[y0:y1,x0:x1]
        local=base[y0:y1,x0:x1].copy()
        if kind=='bass':
            local+=pigment*.019+rim[...,None]*np.array([.055,.058,.063])
            local+=(hue-.5)*np.array([.014,.005,.020])
        else:
            local+=pigment*np.array([.004,.010,.016])
            local+=(hue-.5)*np.array([.035,.045,.075])
            local+=rim[...,None]*np.array([.025,.055,.09])
            local-=np.exp(-((distance-.995)/.025)**2)[...,None]*posterior[...,None]*np.array([.012,.025,.035])
        color[y0:y1,x0:x1]=color[y0:y1,x0:x1]*(1-mask[...,None])+local*mask[...,None]
        raised=.012*rim+.004*np.maximum(0,1-distance**2)
        height[y0:y1,x0:x1]=height[y0:y1,x0:x1]*(1-mask)+raised*mask
        rough[y0:y1,x0:x1]=rough[y0:y1,x0:x1]*(1-mask)+(.34+pigment*.075+rim*.025)*mask
        tilt_x[y0:y1,x0:x1]=tilt_x[y0:y1,x0:x1]*(1-mask)+pigment*.13*mask
        tilt_y[y0:y1,x0:x1]=tilt_y[y0:y1,x0:x1]*(1-mask)+(hue-.5)*.21*mask
    color+=(micro-.5)[...,None]*.025+grain[...,None]*.017
    normal=normals(height,7)*2-1;normal[:,:,0]+=tilt_x;normal[:,:,1]+=tilt_y
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True);normal=normal*.5+.5
    return {'color':image_file(kind+'_irregular_color',np.clip(color,0,1),folder),'normal':image_file(kind+'_fine_overlap_normal',normal,folder,True),'rough':image_file(kind+'_variable_roughness',np.clip(rough,.23,.52),folder,True)}


def build_body(kind,mat):
    if kind=='bass':
        xs=[-1.8,-1.62,-1.3,-.95,-.48,0,.5,.9,1.22,1.43]
        top=[-.12,.035,.24,.44,.53,.50,.39,.26,.15,.13]
        bottom=[-.26,-.35,-.43,-.46,-.45,-.40,-.30,-.19,-.12,-.105]
        width=[.03,.095,.18,.245,.28,.265,.205,.13,.076,.065]
    else:
        xs=[-1.12,-1.02,-.85,-.62,-.25,.12,.5,.76]
        top=[.10,.17,.28,.32,.28,.22,.15,.11];bottom=[.045,-.04,-.18,-.25,-.22,-.16,-.10,-.085]
        width=[.014,.048,.102,.145,.14,.112,.065,.045]
    B.PROFILES[kind]=[list(zip(xs,v)) for v in [top,bottom,width]]
    vertices=[];uv=[];faces=[];n,m=140,96
    for i in range(n+1):
        u=i/n;x=xs[0]+u*(xs[-1]-xs[0]);hi,lo,wid=[B.interp(p,x) for p in B.PROFILES[kind]]
        for j in range(m+1):
            a=2*PI*j/m;z=(hi+lo)/2+(hi-lo)/2*math.sin(a);y=wid*math.cos(a)
            # Small asymmetry and a fleshy maxillary/cheek transition.
            if kind=='bass':y*=1+.025*math.sin(a*3+x*7)*math.exp(-((x+.95)/.65)**2)
            vertices.append((x,y,z));uv.append((u,j/m))
    for i in range(n):
        for j in range(m):
            a=i*(m+1)+j;faces.append((a,a+1,a+m+2,a+m+1))
    faces.extend([tuple(range(m,-1,-1)),tuple(n*(m+1)+j for j in range(m+1))])
    return B.mesh('Skin_AnatomicalBody',vertices,faces,mat,uv)


def eyes(kind):
    x,z,r=(-1.43,-.105,.054) if kind=='bass' else (-.91,.105,.039)
    socket=B.material('Eye_DermalSocket',(.025,.032,.028),.53)
    iris=B.material('Eye_BrownIris',(.09,.065,.027) if kind=='bass' else (.075,.027,.014),.34,.12)
    pupil=B.material('Eye_WetDarkPupil',(.001,.002,.003),.15)
    pupil.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.8
    pupil.node_tree.nodes.get('Principled BSDF').inputs['Coat Roughness'].default_value=.07
    lid=B.material('Eye_UpperDermis',(.10,.12,.10) if kind=='bass' else (.009,.018,.024),.42,.1)
    for side in [-1,1]:
        y=B.flank(kind,x,z,side,-.003)
        B.sphere('EyeSocket',(x,y,z),(r*1.08,r*.20,r*1.06),socket)
        B.sphere('EyeIris',(x,y+side*r*.10,z),(r,r*.31,r),iris)
        B.sphere('EyePupil',(x,y+side*r*.33,z),(r*.60,r*.13,r*.65),pupil)
        points=[(x+r*1.04*math.cos(a),y+side*r*.11,z+r*1.03*math.sin(a)) for a in np.linspace(.03,PI-.03,45)]
        B.tube('Eye_OrganicUpperLid',points,r*.055,lid)


def smooth_curve(points,steps=80):
    xs=np.linspace(0,len(points)-1,steps)
    return [tuple(B.interp(list(enumerate([p[d] for p in points])),t) for d in range(2)) for t in xs]


def head_details(kind):
    crease=B.material('GillCrease_Shadow',(.043,.052,.045) if kind=='bass' else (.009,.015,.020),.61)
    lip=B.material('Lip_FleshyGrey',(.19,.18,.13) if kind=='bass' else (.026,.02,.024),.42,.04)
    if kind=='bass':
        mouth=[(-1.80,-.203),(-1.68,-.239),(-1.47,-.288),(-1.23,-.277),(-1.12,-.21)]
        cover=[(-.96,.205),(-.72,.09),(-.69,-.09),(-.81,-.30),(-1.01,-.397)]
    else:
        mouth=[(-1.115,.082),(-1.055,.061),(-1.00,.045)]
        cover=[(-.71,.20),(-.58,.10),(-.58,-.06),(-.69,-.17)]
    for side in [-1,1]:
        for name,raw,radius,mat in [('Mouth_Crease',mouth,.0018,crease),('Operculum_OrganicFold',cover,.0017,crease)]:
            pts=[(x,B.flank(kind,x,z,side,.0004),z) for x,z in smooth_curve(raw)]
            B.tube(name,pts,radius,mat)
            if name.startswith('Mouth'):
                B.tube('Fleshy_LowerJawEdge',[(x,y,z-.006) for x,y,z in pts[:58]],.0036 if kind=='bass' else .0016,lip)
        x,z=(-1.64,-.035) if kind=='bass' else (-1.075,.12)
        B.sphere('Nostril_Recess',(x,B.flank(kind,x,z,side,.001),z),(.009,.002,.005),crease)



FIN_CACHE={}
def fin_material(kind,folder):
    if kind in FIN_CACHE:return FIN_CACHE[kind]
    w=h=1024;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));rng=np.random.default_rng(72 if kind=='betta' else 92)
    broad=noise(u,v,12,10,51);grain=noise(u,v,200,170,52);fine=rng.random(u.shape)
    primary=np.zeros_like(u);branch=np.zeros_like(u);blue_tracks=np.zeros_like(u)
    positions=np.cumsum(rng.uniform(.65,1.35,26 if kind=='betta' else 19));positions=(positions-positions[0])/(positions[-1]-positions[0])
    for i,pos in enumerate(positions):
        bend=rng.uniform(-.012,.012);center=pos+bend*v*v+.0015*np.sin(v*8+i)
        width=.0009+.0019*(1-v)
        primary=np.maximum(primary,np.exp(-((u-center)/width)**2))
        fork=rng.uniform(.32,.57);spread=rng.uniform(.008,.017)
        for sign in [-1,1]:
            child=center+sign*spread*np.maximum(0,(v-fork)/(1-fork))**.85
            branch=np.maximum(branch,np.exp(-((u-child)/(width*.76))**2)*smoothstep(fork,fork+.06,v))
            for split in [-1,1]:
                twig=child+split*.0045*np.maximum(0,(v-.72)/.28)
                branch=np.maximum(branch,np.exp(-((u-twig)/(.0010+.0006*(1-v)))**2)*smoothstep(.70,.76,v)*.7)
        track_width=rng.uniform(.004,.016);length=rng.uniform(.25,.68)
        blue_tracks=np.maximum(blue_tracks,np.exp(-((u-center)/track_width)**2)*(1-smoothstep(length-.08,length+.04,v)))
    veins=np.maximum(primary,branch*.75)
    if kind=='betta':
        blue=smoothstep(.02,.25,1-v)*(1-smoothstep(.16,.44+(.5-broad)*.35,v));blue=np.maximum(blue,blue_tracks*.92)
        red=np.zeros((h,w,3))+np.array([.49,.025,.044]);red+=(broad-.5)[...,None]*np.array([.16,.018,.018])
        blue_color=np.array([.035,.18,.47]);color=red*(1-blue[...,None])+blue_color*blue[...,None]
        color*=1-(primary*.36+branch*.36)[...,None]
        color+=(grain-.5)[...,None]*.045
        alpha=.72+.12*broad-.20*smoothstep(.65,1,v)+veins*.24
        alpha-=smoothstep(.55,.88,grain)*smoothstep(.75,1,v)*.20
    else:
        tint=np.array([.24,.265,.22]) if kind=='bass' else np.array([.30,.36,.28])
        color=np.zeros((h,w,3))+tint;color+=(broad-.5)[...,None]*.075
        color+=veins[...,None]*np.array([.09,.08,.05]);alpha=.52+.14*broad+veins*.26
        alpha*=1-.25*smoothstep(.80,1,v)
        if kind=='clear':alpha*=.58
    # Subtle pale, uneven distal membranes and fine pigment granules.
    rim=smoothstep(.955,.995,v+.012*np.sin(u*73))*smoothstep(.25,.85,broad)
    color=color*(1-rim[...,None]*.28)+np.array([.48,.39,.28])*rim[...,None]*.28
    color+=(fine-.5)[...,None]*.024;alpha=np.clip(alpha+(fine-.5)*.06,.08,.99)
    height=primary*.045+branch*.032+(grain-.5)*.022+(fine-.5)*.006
    images={'color':image_file(kind+'_fin_pigment',np.clip(color,0,1),folder),'normal':image_file(kind+'_fin_branch_normal',normals(height,3),folder,True),'rough':image_file(kind+'_fin_roughness',.37+(grain-.5)*.12+(broad-.5)*.12,folder,True)}
    mat=maps_material('Fin_OrganicMembrane_'+kind,images,.015,.38);nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.025
    out=nt.nodes.get('Material Output');translucent=nt.nodes.new('ShaderNodeBsdfTranslucent')
    texture=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.label=='color');nt.links.new(texture.outputs['Color'],translucent.inputs['Color'])
    mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.38;nt.links.new(bs.outputs[0],mix.inputs[1]);nt.links.new(translucent.outputs[0],mix.inputs[2])
    alpha_image=image_file(kind+'_fin_opacity',alpha,folder,True);alpha_node=nt.nodes.new('ShaderNodeTexImage');alpha_node.image=alpha_image
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent');final=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha_node.outputs['Color'],final.inputs[0]);nt.links.new(transparent.outputs[0],final.inputs[1]);nt.links.new(mix.outputs[0],final.inputs[2]);nt.links.new(final.outputs[0],out.inputs['Surface'])
    FIN_CACHE[kind]=mat;return mat


def fan(name,root_fn,edge_fn,mat,n=160,m=38,flutter=.035,role='tail',phase=0):
    vertices=[];uv=[];faces=[];rng=np.random.default_rng(sum(map(ord,name)))
    folds=[(rng.uniform(.10,.90),rng.uniform(.035,.085),rng.uniform(-1,1)) for i in range(5)]
    tip_u=np.linspace(0,1,87);tip_values=rng.uniform(-.018,.024,87);tip_values[::3]+=.012
    for i in range(n+1):
        u=i/n;a=np.array(root_fn(u));b=np.array(edge_fn(u))
        # Irregular branching tips and membrane recesses, rather than a perfect fan edge.
        edge_noise=.008*math.sin(u*113+phase)+.005*math.sin(u*197+1.7)+.004*math.sin(u*61+.4)
        if B.SLUG=='betta' and 'Pelvic' not in name:edge_noise+=float(np.interp(u,tip_u,tip_values))
        for j in range(m+1):
            t=j/m;p=a*(1-t)+b*t
            curl=sum(strength*math.exp(-((u-center)/width)**2) for center,width,strength in folds)
            p[1]+=flutter*t**1.6*(math.sin(u*PI*4.3+phase+t*2)+.45*curl)
            p[2]+=edge_noise*t**5
            if B.SLUG=='betta':
                if role=='tail':p[1]-=.095*t+.024*math.sin(u*7)*t*t
                elif role in ['dorsal','anal']:p[1]+=.045*t
            vertices.append(tuple(p));uv.append((u,t))
    for i in range(n):
        for j in range(m):
            a=i*(m+1)+j;faces.append((a,a+m+1,a+m+2,a+1))
    return B.mesh(name,vertices,faces,mat,uv,deform=role)


def barramundi(folder):
    skin=maps_material('Barramundi_NaturalSilver',body_maps('bass',folder),.18,.38)
    build_body('bass',skin);eyes('bass');head_details('bass');fm=fin_material('bass',folder)
    fan('Caudal_RoundedRayMembrane',lambda u:(1.36,0,(u-.5)*.15),lambda u:(2.00+.045*math.cos((u-.5)*PI*1.6)+.012*math.sin(u*17),0,.41*math.sin((u-.5)*PI*.94)),fm,flutter=.035)
    spine_x=[-.81,-.65,-.48,-.28,-.08,.10,.25,.34];spine_z=[.49,.60,.67,.65,.59,.53,.47,.40]
    def edge(u):
        t=u*7;i=min(6,int(t));f=t-i
        return ((1-f)*spine_x[i]+f*spine_x[i+1],0,(1-f)*spine_z[i]+f*spine_z[i+1]-.035*math.sin(PI*f))
    fan('Dorsal_FirstEightSpines',lambda u:(-.81+1.15*u,0,B.interp(B.PROFILES['bass'][0],-.81+1.15*u)*.99),edge,fm,flutter=.010,role='dorsal')
    raymat=B.material('Dorsal_BoneMuted',(.10,.12,.085),.48)
    for i,(x,z) in enumerate(zip(spine_x,spine_z)):
        B.tube('Dorsal_Spine',[(x,0,B.interp(B.PROFILES['bass'][0],x)*.97),(x-.014,0,z)],.0018,raymat,'dorsal')
    fan('Dorsal_SecondSoftRays',lambda u:(.20+.98*u,0,B.interp(B.PROFILES['bass'][0],.20+.98*u)),lambda u:(.17+1.04*u,0,B.interp(B.PROFILES['bass'][0],.17+1.04*u)+.30*math.sin(PI*u)**.66+.06*(1-u)*math.sin(PI*u)),fm,flutter=.04,role='dorsal',phase=.7)
    fan('Anal_NaturalFold',lambda u:(.35+.80*u,0,B.interp(B.PROFILES['bass'][1],.35+.80*u)),lambda u:(.36+.88*u,0,B.interp(B.PROFILES['bass'][1],.36+.88*u)-.24*math.sin(PI*u)**.73),fm,flutter=.033,role='anal',phase=2)
    for side in [-1,1]:
        fan('Pectoral_'+str(side),lambda u:(-.68,side*.23,-.23+(u-.5)*.055),lambda u:(-.20+.20*math.sin(PI*u),side*(.27+.12*math.sin(PI*u)),-.25+(u-.5)*.22),fin_material('clear',folder),n=100,m=28,flutter=.025,role='pectoral',phase=side)
        fan('Pelvic_'+str(side),lambda u:(-.39,side*.10,-.42),lambda u:(-.10+.34*u,side*(.12+.06*math.sin(PI*u)),-.42-.12*math.sin(PI*u)),fm,n=90,m=26,flutter=.02,role='anal')


def betta(folder):
    skin=maps_material('Betta_IndividualIridescentScales',body_maps('betta',folder),.22,.39)
    build_body('betta',skin);eyes('betta');head_details('betta');fm=fin_material('betta',folder)
    def edge(u):
        a=-PI*.46+PI*.94*u;r=.98*(1+.038*math.sin(u*PI*5+.8)+.018*math.sin(u*PI*17+2))
        return (.76+r*math.cos(a),.035*math.sin(a*2+.3),r*math.sin(a)*(1-.05*u))
    fan('Caudal_HalfmoonPleatedMembrane',lambda u:(.70,0,(u-.5)*.16),edge,fm,n=230,m=48,flutter=.105,phase=.6)
    dorsal_points=[(-.47,.30),(-.28,.59),(.02,.76),(.37,.82),(.68,.66),(.85,.25)]
    anal_points=[(-.67,-.20),(-.39,-.56),(-.04,-.71),(.39,-.80),(.79,-.65),(.99,-.10)]
    def outline(points,u):
        t=u*(len(points)-1);x,z=smooth_curve(points,180)[min(179,int(u*179))];return (x,0,z)
    fan('Dorsal_SoftFlowingFin',lambda u:(-.47+1.20*u,0,B.interp(B.PROFILES['betta'][0],-.47+1.20*u)),lambda u:outline(dorsal_points,u),fm,n=180,m=44,flutter=.065,role='dorsal',phase=1.3)
    fan('Anal_LongFlowingFin',lambda u:(-.67+1.40*u,0,B.interp(B.PROFILES['betta'][1],-.67+1.40*u)),lambda u:outline(anal_points,u),fm,n=190,m=44,flutter=.080,role='anal',phase=3.0)
    for side in [-1,1]:
        fan('Pectoral_'+str(side),lambda u:(-.64,side*.13,-.02),lambda u:(-.40+.11*math.sin(PI*u),side*(.20+.025*math.sin(PI*u)),-.03+(u-.5)*.17),fin_material('clear',folder),n=90,m=24,flutter=.025,role='pectoral',phase=side)
        fan('Pelvic_SlenderRibbon_'+str(side),lambda u:(-.66,side*.065,-.14),lambda u:(-.50+.15*u,side*(.085+.016*math.sin(PI*u)),-.20-.57*math.sin(PI*u)**1.7),fm,n=100,m=32,flutter=.03,role='anal',phase=side)


def ray_maps(folder):
    w=h=1536;u,v=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h));x=-1.5+3.2*u;y=-1.5+3*v
    broad=noise(u,v,12,14,61);mottle=noise(u,v,61,58,62);micro=noise(u,v,410,380,63);rng=np.random.default_rng(69)
    color=np.zeros((h,w,3))+np.array([.31,.30,.225]);color+=(broad-.5)[...,None]*.15+(mottle-.5)[...,None]*.075+(micro-.5)[...,None]*.026
    for i in range(105):
        px,py=rng.uniform(-1.15,1.00),rng.uniform(-1.06,1.06)
        if abs(py)>1.08-.35*abs(px) or (px+.68)**2+(abs(py)-.22)**2<.035:continue
        radius=rng.uniform(.012,.057);ratio=rng.uniform(.65,1.45);angle=rng.uniform(-PI,PI)
        dx=(x-px)*math.cos(angle)+(y-py)*math.sin(angle);dy=-(x-px)*math.sin(angle)+(y-py)*math.cos(angle)
        a=np.arctan2(dy,dx);d=np.sqrt((dx*ratio)**2+(dy/ratio)**2)
        threshold=radius*(1+.055*np.sin(a*3+i)+.035*np.cos(a*5+i*2)+.04*(mottle-.5))
        alpha=1-smoothstep(threshold*.80,threshold*1.17,d)
        pigment=np.array([.035,.27,.48])+rng.uniform(-.015,.015)
        color=color*(1-alpha[...,None])+pigment*alpha[...,None]
    mask=np.exp(-((x+.66)/.23)**4-((np.abs(y)-.20)/.13)**4)*(.45+.25*mottle)
    color*=1-mask[...,None]
    freckles=smoothstep(.72,.84,micro)*smoothstep(.52,.65,mottle)
    color*=1-freckles[...,None]*.24
    height=(micro-.5)*.14+(mottle-.5)*.04
    return {'color':image_file('ray_mottled_pigment',np.clip(color,0,1),folder),'normal':image_file('ray_dermal_granules',normals(height,4),folder,True),'rough':image_file('ray_matte_variable_roughness',.53+(mottle-.5)*.12+(micro-.5)*.10,folder,True)}


ORIGINAL_RAY=B.stingray

def stingray(folder):
    ORIGINAL_RAY(folder)
    skin=bpy.data.materials['Maskray_SandAndBluePigment'];skin.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.015
    body=bpy.data.objects['Ray_ContinuousCamberedDisc']
    for vertex in body.data.vertices:
        x,y,z=vertex.co;t=min(1,math.sqrt((x/1.3)**2+(y/1.4)**2))
        vertex.co.x-=.10*math.exp(-(y/.22)**2)*max(0,min(1,(-x-.7)/.5))
        wave=.065*t**4*math.sin(x*2.8+y*1.7)
        if vertex.index<len(body.data.vertices)//2:
            vertex.co.z+=wave+.003*t**3*math.sin(math.atan2(y,x)*75+x*3)
        else:vertex.co.z=vertex.co.z*.58+wave
    for obj in list(B.ROOT.children_recursive):
        if obj.name.startswith(('Ray_Eye','Ray_Iris','Ray_Pupil','Ray_UpperEye','Ray_Spiracle')):bpy.data.objects.remove(obj,do_unlink=True)
    eye=B.material('Ray_QuietDarkEye',(.008,.012,.008),.28);eye.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.4
    cavity=B.material('Ray_OrganicSpiracle',(.005,.004,.003),.95);cavity.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.05
    hood=B.material('Ray_DermalEyelid',(.075,.065,.035),.64)
    for side in [-1,1]:
        B.sphere('Ray_Eye',(-.723,side*.205,.211),(.034,.044,.018),eye)
        B.sphere('Ray_Spiracle',(-.47,side*.225,.158),(.079,.031,.004),cavity)
        pts=[(-.47+.081*math.cos(a),side*.225+.033*math.sin(a),.158+.004*math.sin(a)) for a in np.linspace(.10,PI*.9,37)]
        B.tube('Ray_IncompleteSoftSpiracleLip',pts,.0025,hood)
    for obj in [bpy.data.objects['Ray_TaperedWhipTail'],bpy.data.objects['Ray_TailBarb']]:
        for v in obj.data.vertices:
            oldx,oldy,oldz=v.co;t=max(0,min(1,(oldx-.70)/3.25));oldcenter_y=.10*math.sin(t*PI)+.28*t*t;oldcenter_z=.02-.13*t+.15*t*t
            v.co.x=.70+3.15*t-.36*t*t*t;v.co.y=.61*math.sin(t*PI*1.34)-.20*t*t+(oldy-oldcenter_y)*.75;v.co.z=.02+.035*math.sin(t*PI)+(oldz-oldcenter_z)*.75
        obj.data.update()



def studio(kind,folder):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.time_limit=70;scene.cycles.use_denoising=True
    scene.render.threads_mode='FIXED';scene.render.threads=6;scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=3;scene.cycles.transparent_max_bounces=6
    scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
    scene.render.resolution_x=1280;scene.render.resolution_y=854;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('NeutralPhotographicWorld');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.055,.065,.055,1);bg.inputs[1].default_value=.30
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
    for name,location,power,size,color in [('Soft_Window',(-2,-3,4),500,3.5,(.93,1,.96)),('Weak_Fill',(-1,-5,.5),170,3,(.88,.92,1)),('Rim_Back',(2,2.5,3),320,2.5,(.95,.97,1))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=location;B.aim(obj,(0,0,0))
    floor=B.material('STUDIO_MatteBackdrop',(.030,.041,.035),.85)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.35 if kind!='ray' else -.60));bpy.context.object.name='STUDIO_Floor';bpy.context.object.data.materials.append(floor)
    data=bpy.data.cameras.new('ReviewCamera');camera=bpy.data.objects.new('ReviewCamera',data);scene.collection.objects.link(camera);scene.camera=camera
    if kind=='bass':camera.location=(-.20,-8,1.1);target=(.05,0,.0);scale=4.8
    elif kind=='betta':camera.location=(-.25,-7,.7);target=(.31,0,0);scale=3.55
    else:camera.location=(-2.6,-5.2,6.0);target=(.85,0,0);scale=5.9
    B.aim(camera,target);data.type='ORTHO';data.ortho_scale=scale;scene.render.filepath=str(folder/'preview.png')
    scene['review_status']='Revision 02; awaiting owner visual approval; not published';scene['photo_reference_only']='Photos were visually studied, never embedded as textures'
    return camera


B.image_file=image_file;B.maps_material=maps_material;B.body_maps=body_maps;B.build_body=build_body;B.eyes=eyes;B.head_details=head_details
B.fin_material=fin_material;B.fan=fan;B.barramundi=barramundi;B.betta=betta;B.ray_maps=ray_maps;B.stingray=stingray;B.studio=studio
if __name__=='__main__':
    slugs=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['barramundi','stingray','betta']
    for slug in slugs:
        FIN_CACHE.clear();B.main(slug)

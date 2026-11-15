"""Build the chibi visitor in an isolated Blender background process (5.1.2)."""
from pathlib import Path
import os
import sys
import math as m
import bpy
from mathutils import Vector

if not bpy.app.background:
    raise RuntimeError("Use a fresh Blender --background --factory-startup process.")
OUT = Path(os.environ.get("CHIBI_OUT", Path(__file__).resolve().parent))
OUT.mkdir(exist_ok=True, parents=True)
DRAFT = os.environ.get("CHIBI_DRAFT") == "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from face_sculpt import cheek_volume, sculpt_head
from hair_sculpt import sculpt_fringe

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
TAU = 2*m.pi
def group(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
head=group("01 | Face"); hairgroup=group("02 | Hair"); outfit=group("03 | Hoodie and shorts")
limbs=group("04 | Limbs"); shoes=group("05 | Sneakers"); extras=group("06 | Accessories"); studio=group("Studio | excluded from GLB")
active=head
def put(o,name,mat):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    active.objects.link(o)
    if mat: o.data.materials.append(mat)
    if o.type=="MESH":
        o.data.name=name
        for p in o.data.polygons:p.use_smooth=True
    return o

def rgb(h):
    t=tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
    return tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in t)
def mat(name,h,rough=.62,metal=0):
    c=rgb(h); a=bpy.data.materials.new(name); a.diffuse_color=(*c,1); a.use_nodes=True
    b=a.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value=(*c,1)
    b.inputs["Roughness"].default_value=rough; b.inputs["Metallic"].default_value=metal
    return a
skin=mat("Peach porcelain","FFCA9F",.54); inner=mat("Warm recessed ear","EA9B7D")
hair=mat("Roasted chestnut","49312C",.49); hairlight=mat("Warm chestnut locks","533933",.47); hairmid=mat("Cocoa locks","4E352E",.5)
ink=mat("Warm lash","372320"); iris=mat("Amber iris","805235",.26); pupil=mat("Velvet pupil","281C1D",.25)
ivory=mat("Porcelain white","FFFBF4",.43); brow=mat("Brows","4C322A")
blue=mat("Cornflower fleece","416EE1"); cuff=mat("Royal blue ribbing","3457BD"); seam=mat("Tonal topstitch","6F97EE"); lining=mat("Hood lining","314D9C")
navy=mat("Midnight twill","30334A"); roll=mat("Indigo cuffs","454962"); shoe=mat("Ink blue canvas","3A487E")
rubber=mat("Ivory rubber","F4F1F0"); outsole=mat("Tread","BCBDCD"); tan=mat("Honey canvas","DAAA72"); piping=mat("Saddle leather","AB794C")
brown=mat("Cocoa webbing","694935"); gold=mat("Antique brass","D6AA68",.33,.55); watch=mat("Graphite silicone","303047"); glass=mat("Watch glass","485770",.19,.38)
def mesh(name,v,f,material,sub=0):
    data=bpy.data.meshes.new(name); data.from_pydata(v,[],f); data.update()
    o=bpy.data.objects.new(name,data); put(o,name,material)
    if sub:
        mod=o.modifiers.new("Tailored surface","SUBSURF"); mod.levels=mod.render_levels=sub
    return o
def ell(name,xyz,s,material,rot=None,detail=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=detail,ring_count=detail//2,location=xyz)
    o=put(bpy.context.object,name,material);o.scale=s
    if rot:o.rotation_euler=rot
    return o
def box(name,xyz,size,bevel,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object
    for v in o.data.vertices:
        for k in range(3):v.co[k]*=size[k]
    put(o,name,material)
    mo=o.modifiers.new("Rolled edges","BEVEL");mo.width=bevel;mo.segments=5
    mo=o.modifiers.new("Broad panels","WEIGHTED_NORMAL");return o
def sp(n,e):return m.copysign(abs(n)**e,n)
# ring row: z, x radius, y radius, center x, center y. Closed surfaces with
# adjustable cross sections keep the jaw, garment hems and soles intentional.
def loft(name,rows,material,e=1,n=32,sub=1):
    v=[];f=[]
    for z,a,b,x,y in rows:
        for j in range(n):
            t=j*TAU/n;v.append((x+a*sp(m.cos(t),e),y+b*sp(m.sin(t),e),z))
    for i in range(len(rows)-1):
        for j in range(n):
            k=i*n+j;l=i*n+(j+1)%n;f.append((k,l,l+n,k+n))
    f+=[tuple(reversed(range(n))),tuple(range(len(v)-n,len(v)))]
    return mesh(name,v,f,material,sub)
def sample(points,steps=5):
    p=[Vector(q) for q in points];out=[]
    for j in range(len(p)-1):
        a,b,c,d=p[max(0,j-1)],p[j],p[j+1],p[min(j+2,len(p)-1)]
        for k in range(steps):
            t=k/steps;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3))
    return out+[p[-1]]
def strand(name,points,widths,depths,material,axis=(0,-1,0),n=10,steps=5,capnorm=False):
    path=sample(points,steps);wd=sample([(a,b) for a,b in zip(widths,depths)],steps)
    v=[];f=[]
    for i,(c,size) in enumerate(zip(path,wd)):
        d=(path[min(i+1,len(path)-1)]-path[max(i-1,0)]).normalized()
        normal=Vector(axis) if not capnorm else Vector((c.x/.62**2,(c.y-.018)/.49**2,(c.z-2.018)/.56**2)).normalized()
        if abs(normal.dot(d))>.98:normal=Vector((1,0,0)) if abs(d.x)<.9 else Vector((0,1,0))
        across=normal.cross(d).normalized(); normal=d.cross(across).normalized()
        for j in range(n):
            t=j*TAU/n; v.append(c+across*(max(.0004,size.x)*m.cos(t))+normal*(max(.0004,size.y)*m.sin(t)))
    for i in range(len(path)-1):
        for j in range(n):
            k=i*n+j;l=i*n+(j+1)%n;f.append((k,l,l+n,k+n))
    f.extend([tuple(reversed(range(n))),tuple(range(len(v)-n,len(v)))])
    return mesh(name,v,f,material)
def tube(name,points,r,material,n=10):
    return strand(name,points,[r]*len(points),[r]*len(points),material,n=n)
def stripe(name,points,ws,th,material):
    return strand(name,points,ws,[th]*len(points),material,n=12)
# Face silhouette: full temples, soft jaw and a shallow chin, rather than a ball.
profile = [
    (1.454, .041, .073, -.015),
    (1.466, .138, .170, -.019),
    (1.498, .257, .273, -.022),
    (1.564, .370, .342, -.022),
    (1.651, .450, .388, -.017),
    (1.752, .509, .412, -.002),
    (1.900, .524, .427,  .008),
    (2.050, .515, .430,  .016),
    (2.220, .494, .423,  .020),
    (2.360, .432, .380,  .022),
    (2.470, .310, .290,  .024),
    (2.530, .120, .130,  .024),
    (2.540, .022, .021,  .024),
]
# Smooth interpolation is shared by the head and the features projected onto it.
prof=sample(profile,4)
def surface(x,z):
    for a,b in zip(prof,prof[1:]):
        if a.x<=z<=b.x:
            l=a.lerp(b,(z-a.x)/(b.x-a.x))
            front = max(0, 1 - (abs(x) / l.y) ** 2.6) ** (1/2.6)
            return l.w - front * (l.z + cheek_volume(x, z))
    return -.23
sculpt_head(prof, surface, mesh, skin, mat, rgb)
# Each facial applique follows the head curvature. The convex profile produces
# real parallax from oblique views without floating spherical eyeballs.
def patch(name,x,z,outline,material,offset,dome=0):
    n=len(outline);v=[(x,surface(x,z)-offset-dome,z)];f=[]
    for r in (.25,.50,.75,1):
        for dx,dz in outline:
            X=x+r*dx;Z=z+r*dz;v.append((X,surface(X,Z)-offset-dome*(1-r*r),Z))
    for j in range(n):f.append((0,1+j,1+(j+1)%n))
    for i in range(3):
        for j in range(n):
            a=1+i*n+j;b=1+i*n+(j+1)%n;f.append((a,a+n,b+n,b))
    return mesh(name,v,f,material)
def oval(a,b,n=48):return [(a*m.cos(t*TAU/n),b*m.sin(t*TAU/n)) for t in range(n)]
def facial_line(name,xzs,ws,material,offset,th):
    return stripe(name,[(x,surface(x,z)-offset,z) for x,z in xzs],ws,th,material)
for side,tag in [(-1,"R"),(1,"L")]:
    x=side*.209;z=1.81
    ell("Pinna."+tag,(side*.493,-.002,1.69),(.102,.080,.123),skin,(0,side*.3,0))
    ell("Concha."+tag,(side*.528,-.066,1.691),(.05,.023,.076),inner,(0,side*.30,side*.23))
    ell("Tragus."+tag,(side*.505,-.086,1.676),(.030,.016,.046),skin)
    # A heavier upper lash and pale lower edge leave the eye open at the bottom.
    patch("Sclera."+tag,x,z-.005,oval(.119,.102),ivory,.012,.020)
    patch("Limbal ring."+tag,x-side*.005,z-.004,oval(.079,.094),ink,.029,.012)
    ir=patch("Amber iris."+tag,x-side*.005,z-.005,oval(.074,.089),iris,.035,.015)
    shade=ir.data.color_attributes.new(name="IrisGradient",type="FLOAT_COLOR",domain="POINT")
    for v in ir.data.vertices:
        t=max(0,min(1,(z+.052-v.co.z)/.135))
        shade.data[v.index].color=(*[a*(1-t)+b*t for a,b in zip(rgb("422E28"),rgb("9B6A46"))],1)
    if not iris.node_tree.nodes.get("IrisGradient"):
        nd=iris.node_tree.nodes.new("ShaderNodeVertexColor");nd.name=nd.layer_name="IrisGradient"
        iris.node_tree.links.new(nd.outputs["Color"],iris.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    patch("Pupil."+tag,x-side*.005,z+.009,oval(.050,.064),pupil,.047,.011)
    patch("Studio glint."+tag,x-.026,z+.043,oval(.015,.017,24),ivory,.063,.004)
    patch("Lower glint."+tag,x+.024,z-.051,oval(.004,.003,16),mat("Honey glint."+tag,"F4CD9D"),.055,.002)
    facial_line("Upper lash."+tag,[(x+side*a,z+b) for a,b in [(-.115,-.01),(-.099,.060),(-.042,.106),(.037,.112),(.098,.075),(.119,.024),(.12,-.010)]],[.002,.009,.014,.015,.011,.005,.001],ink,.017,.004)
    facial_line("Eyebrow."+tag,[(side*a,b) for a,b in [(.121,1.991),(.158,2.01),(.205,2.024),(.255,2.021),(.294,2.006)]],[.008,.021,.023,.017,.002],brow,.015,.007)
ell("Button nose",(0,surface(0,1.708),1.708),(.031,.027,.024),skin)
active=hairgroup
# The rounded-square forehead can project through an ellipsoid at the temples.
# Follow the actual head cross-section beneath the locks to keep a continuous
# dark hairline even where the render engine culls single-sided surfaces.
base_v=[]; base_f=[]; M=64
for i in range(18):
    u=i/17
    for j in range(M):
        t=TAU*j/M;z0=1.685+.585*max(0,m.cos(t))**1.65+.039*m.cos(9*t+.4)*(1-max(0,m.cos(t)))
        z=z0+u*(2.534-z0)
        for a,b in zip(prof,prof[1:]):
            if a.x<=z<=b.x:
                l=a.lerp(b,(z-a.x)/(b.x-a.x));break
        base_v.append(((l.y+.018)*sp(m.sin(t),2/2.6),l.w-(l.z+.021)*sp(m.cos(t),2/2.6),z+.006))
for i in range(17):
    for j in range(M):
        a=i*M+j;b=i*M+(j+1)%M;base_f.append((a,b,b+M,a+M))
base_f.append(tuple(range(17*M,18*M)));mesh("Hair | continuous underlayer",base_v,base_f,hair)
v=[(0,.025,2.575)];f=[];N=72;R=28
for i in range(1,R+1):
    for j in range(N):
        t=TAU*j/N;s=m.cos(t)
        edge=1.65+.57*max(0,s)**1.35+.025*m.cos(5*t+.7)
        a=m.acos((edge-2.018)/.557)*i/R
        v.append((.558*m.sin(a)*m.sin(t),.025-.481*m.sin(a)*m.cos(t),2.018+.557*m.cos(a)))
for j in range(N):f.append((0,1+j,1+(j+1)%N))
for i in range(R-1):
    for j in range(N):
        a=1+i*N+j;b=1+i*N+(j+1)%N;f.append((a,a+N,b+N,b))
f.append(tuple(reversed(range(1+(R-1)*N,1+R*N))))
mesh("Hair | fitted scalp",v,f,hair)
# Longitudinal rear and temple pieces overlap from the crown to a layered nape.
for j in range(13):
    t=.96+j*(TAU-1.92)/12;points=[]
    for a,turn,puff in [(.31,-.46,.0),(.78,-.38,.018),(1.27,-.28,.036),(1.74,-.14,.048),(2.03,-.028,.028),(2.28,.105,.010)]:
        t2=t+turn;alpha=a+.06*m.sin(3*t)*a/2+.11*max(0,-m.cos(t))*a/2
        points.append(((.558+puff)*m.sin(alpha)*m.sin(t2),.025-(.481+puff)*m.sin(alpha)*m.cos(t2),2.018+.557*m.cos(alpha)))
    strand("Feathered nape %02d"%j,points,[.02,.079,.096,.084,.057,.002],[.012,.026,.039,.030,.016,.0005],[hairmid,hair,hairlight][j%3],n=14,capnorm=True)
sculpt_fringe(mesh, sample, mat, rgb, surface)
def tuft(name,pts,ws,ma):return strand(name,pts,ws,[max(.001,w*.60) for w in ws],ma,n=16,capnorm=True)
tuft("Crown | lifted quiff",[(.15,-.23,2.445),(.114,-.15,2.526),(.054,-.045,2.598),(-.035,.015,2.639),(-.127,.018,2.645),(-.213,.00,2.633)],[.025,.071,.077,.057,.03,.001],hairmid)
tuft("Crown | little flick",[(.14,-.18,2.436),(.21,-.14,2.503),(.308,-.078,2.528),(.403,-.017,2.508),(.463,-.015,2.456)],[.02,.052,.051,.03,.002],hairlight)
for s in (-1,1):
    for z,w in [(2.015,.077)]:
        tuft("Temple | outward flick",[(s*.40,-.17,z+.19),(s*.484,-.158,z+.10),(s*.55,-.14,z+.03),(s*.617,-.12,z+.008),(s*.661,-.095,z+.035)],[.018,w*1.1,w,w*.48,.001],hairmid)
active=limbs
loft("Neck",[(1.308,.100,.098,0,.022),(1.328,.108,.099,0,.022),(1.44,.102,.105,0,.01),(1.516,.119,.12,0,0)],skin)
active=outfit
loft("Pullover | torso",[(.787,.241,.15,0,0),(.80,.298,.198,0,0),(.841,.31,.21,0,0),(.902,.315,.207,0,0),(1.01,.288,.196,0,0),(1.14,.263,.177,0,.009),(1.249,.264,.177,0,.009),(1.303,.252,.159,0,.012),(1.337,.175,.132,0,.01),(1.359,.11,.098,0,.012)],blue,.79)
loft("Pullover | ribbed hem",[(.788,.292,.19,0,0),(.792,.306,.202,0,0),(.813,.31,.205,0,0),(.845,.31,.208,0,0),(.851,.306,.206,0,0)],cuff,.79)
ell("Hood | folded back",(0,.124,1.292),(.269,.154,.167),blue)
for s in (-1,1):
    strand("Hood | folded collar",[(s*.071,.148,1.397),(s*.164,.135,1.398),(s*.229,.021,1.35),(s*.205,-.085,1.325),(s*.13,-.145,1.312),(s*.022,-.169,1.248)],[.029,.046,.054,.051,.039,.011],[.024,.040,.041,.04,.03,.013],blue,n=14,axis=(0,0,1))
stripe("Hood | inset neckline",[(-.105,-.15,1.347),(0,-.177,1.284),(.103,-.15,1.347)],[.007,.015,.007],.009,ivory)
for s in (-1,1):
    tube("Hood cord",[(s*.103,-.154,1.314),(s*.1,-.183,1.27),(s*.105,-.184,1.195),(s*.100,-.183,1.13)],.009,ivory)
    ell("Cord end",(s*.10,-.185,1.129),(.012,.012,.019),rubber)
# Stitched trapezoidal kangaroo pocket curves around the sweatshirt.
pts=[(-.202,-.183,.897),(-.196,-.191,.918),(-.129,-.19,1.001),(-.125,-.195,1.014),(.124,-.195,1.014),(.131,-.19,1.001),(.197,-.191,.918),(.202,-.183,.897),(.158,-.20,.875),(-.158,-.20,.875)]
v=[(0,-.218,.943)]+pts;mesh("Kangaroo pocket",v,[(0,1+(i+1)%len(pts),i+1) for i in range(len(pts))],blue)
tube("Pocket | topstitch",pts[:8],.0028,seam)
for s in (-1,1):
    def leg(name,rows,material,e=.9):
        return loft(name,[(z,rx,ry,s*x,y) for z,rx,ry,x,y in rows],material,e)
    leg("Shorts | tailored leg",[(.532,.144,.147,.171,.005),(.541,.153,.16,.171,.005),(.60,.151,.157,.167,.006),(.731,.148,.158,.156,.014),(.82,.137,.143,.137,.014),(.852,.118,.126,.126,.015)],navy,.8)
    leg("Shorts | turned cuff",[(.529,.143,.15,.173,.003),(.533,.154,.157,.173,.003),(.562,.156,.159,.17,.003),(.574,.151,.157,.169,.003)],roll,.8)
    tube("Shorts | pocket welt",[(s*.249,-.121,.755),(s*.275,-.107,.714),(s*.287,-.09,.687)],.003,roll)
    active=limbs
    leg("Bare leg",[(.239,.077,.075,.193,0),(.262,.088,.086,.195,0),(.331,.09,.094,.194,.004),(.429,.103,.101,.185,.006),(.546,.111,.113,.177,.01),(.60,.107,.105,.17,.011)],skin)
    sleevepath=[(s*.213,.0,1.256),(s*.253,0,1.252),(s*.31,.001,1.202),(s*.35,-.002,1.138),(s*.365,-.005,1.108)]
    active=outfit
    strand("Short raglan sleeve",sleevepath,[.083,.103,.103,.103,.097],[.102,.118,.125,.115,.103],blue,n=28)
    strand("Sleeve | binding",[(s*.348,-.001,1.135),(s*.358,-.004,1.12),(s*.369,-.006,1.105)],[.102,.103,.098],[.114,.116,.108],cuff,n=28)
    active=limbs
    strand("Forearm",[(s*.339,-.002,1.152),(s*.367,-.006,1.092),(s*.407,-.01,1.019),(s*.443,-.026,.96),(s*.463,-.040,.904)],[.076,.076,.068,.065,.056],[.077,.074,.069,.060,.052],skin,n=22)
    ell("Palm",(s*.478,-.046,.85),(.060,.064,.086),skin,(0,-s*.17,0))
    for j in range(4):
        yy=-.086+j*.026;xx=s*(.486+.010*m.sin(j))
        strand("Curled finger",[(xx,yy,.85),(xx+s*.007,yy-.002,.812),(xx-s*.004,yy-.004,.786+.007*abs(1-j)),(xx-s*.022,yy-.004,.786+.007*abs(1-j))],[.025,.025,.019,.007],[.020,.019,.017,.007],skin,n=12)
    strand("Thumb",[(s*.462,-.087,.875),(s*.444,-.10,.857),(s*.44,-.109,.831),(s*.447,-.111,.824)],[.027,.026,.019,.008],[.027,.023,.018,.008],skin,n=14)
    active=shoes
    leg("Crew sock",[(.177,.083,.082,.193,0),(.215,.091,.09,.193,0),(.321,.096,.097,.193,0),(.347,.097,.098,.193,0),(.35,.093,.094,.193,0)],ivory)
    leg("Sock rib",[(.324,.094,.096,.193,0),(.327,.099,.10,.193,0),(.346,.099,.10,.193,0),(.35,.096,.097,.193,0)],rubber)
    leg("Sneaker | outsole",[(.006,.124,.186,.194,-.055),(.009,.148,.216,.194,-.055),(.018,.152,.219,.194,-.055),(.027,.152,.22,.194,-.055)],outsole,.65)
    leg("Sneaker | foxing",[(.019,.15,.219,.194,-.055),(.024,.155,.222,.194,-.055),(.061,.156,.224,.194,-.055),(.076,.153,.223,.194,-.055),(.08,.146,.218,.194,-.055)],rubber,.65)
    leg("Sneaker | upper",[(.067,.15,.218,.194,-.055),(.079,.152,.217,.194,-.055),(.111,.148,.21,.194,-.053),(.145,.139,.192,.194,-.039),(.179,.124,.146,.194,-.004),(.225,.103,.108,.194,.013),(.246,.097,.099,.194,.018)],shoe,.76)
    ell("Sneaker | shell toe",(s*.194,-.196,.086),(.143,.08,.058),rubber)
    ell("Sneaker | tongue",(s*.194,-.075,.196),(.070,.051,.065),shoe,(-.55,0,0))
    for j in range(3):
        yy=-.184+j*.038;zz=.158+j*.027
        tube("Flat cotton lace",[(s*(.194-.064),yy+.005,zz-.007),(s*.194,yy-.012,zz+.009),(s*(.194+.064),yy+.003,zz-.004)],.012,ivory)
    for j in range(2):
        stripe("Canvas | side stripe",[(s*.338,-.088+j*.037,.102),(s*.333,-.063+j*.037,.131),(s*.32,-.034+j*.037,.15)],[.008,.009,.006],.003,ivory)
    active=outfit
active=extras
def ribbon(name,path,width,material,normal):
    pts=sample(path,6);v=[];f=[]
    for i,p in enumerate(pts):
        d=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized()
        outward=Vector(normal);across=outward.cross(d).normalized()
        for a,b in [(-1,0),(-.9,.004),(.9,.004),(1,0),(.9,-.004),(-.9,-.004)]:
            v.append(p+across*(a*width/2)+outward*b)
    for i in range(len(pts)-1):
        for j in range(6):
            k=i*6+j;l=i*6+(j+1)%6;f.append((k,l,l+6,k+6))
    f+=[tuple(reversed(range(6))),tuple(range(len(v)-6,len(v)))]
    return mesh(name,v,f,material)
pack=box("Daypack | body",(0,.21,1.055),(.416,.218,.405),.080,shoe)
box("Daypack | pocket",(0,.321,1.004),(.307,.061,.166),.028,navy)
tube("Daypack | hanging loop",[(-.04,.204,1.252),(-.035,.208,1.297),(.03,.208,1.297),(.04,.204,1.252)],.009,navy)
for sign in (-1,1):
    ribbon("Daypack | shoulder strap",[(sign*.173,.16,1.231),(sign*.201,.117,1.325),(sign*.202,.022,1.35),(sign*.206,-.080,1.325),(sign*.222,-.138,1.235),(sign*.239,-.130,1.143),(sign*.271,-.085,1.036),(sign*.29,.008,.959),(sign*.24,.143,.921),(sign*.166,.184,.901)],.045,shoe,(0,-1,0))
ribbon("Satchel | front webbing",[(.202,.014,1.382),(.190,-.124,1.359),(.131,-.196,1.261),(.061,-.211,1.173),(-.005,-.226,1.088),(-.073,-.226,1.008),(-.127,-.202,.951)],.052,brown,(0,-1,0))
ribbon("Satchel | rear webbing",[(.202,.014,1.382),(.214,.106,1.353),(.14,.230,1.276),(.066,.24,1.215),(-.026,.202,1.111),(-.163,.191,.981),(-.275,.148,.871),(-.337,.050,.855),(-.365,-.084,.929),(-.354,-.228,1.020)],.047,brown,(0,1,0))
bagroot=bpy.data.objects.new("Canvas satchel",None);extras.objects.link(bagroot);bagroot.location=(-.274,-.205,.819);bagroot.scale=(1.22,1.19,1.45);bagroot.rotation_euler=(.02,.22,.32)
def attach(o):
    o.parent=bagroot;return o
attach(box("Satchel | gusset",(0,0,0),(.248,.143,.231),.048,piping))
attach(box("Satchel | pouch",(0,-.023,.003),(.244,.131,.22),.044,tan))
attach(box("Satchel | flap",(0,-.071,.053),(.248,.067,.12),.028,tan))
attach(box("Satchel | fastening tab",(-.039,-.104,.006),(.038,.012,.066),.009,piping))
attach(ell("Satchel | snap",(-.039,-.114,.003),(.008,.004,.008),gold))
attach(tube("Satchel | seam",[(-.101,-.10,.055),(-.1,-.101,.027),(-.086,-.102,.014),(.086,-.102,.014),(.101,-.10,.028),(.102,-.1,.054)],.0028,piping))
for x in (-.101,.102):
    attach(box("Satchel | loop",(x,0,.11),(.026,.059,.045),.009,brown))
    attach(tube("Antique brass loop",[(x,-.024,.12),(x,-.024,.14),(x,.022,.14),(x,.022,.12)],.005,gold))
# Band follows the arm; the broad watch face sits on its outside.
strand("Watch | silicone band",[(.437,-.024,.974),(.444,-.027,.958),(.453,-.031,.937)],[.071,.071,.069],[.066,.068,.063],watch,n=28)
wa=box("Watch | case",(.454,-.081,.953),(.08,.034,.077),.012,watch);wa.rotation_euler[1]=-.48
wa=box("Watch | glass",(.455,-.100,.953),(.061,.009,.058),.008,glass);wa.rotation_euler[1]=-.48
# A single root on the gallery floor makes the entire visitor easy to place.
root=bpy.data.objects.new("ChibiMallVisitor",None);scene.collection.objects.link(root)
character=[o for c in (head,hairgroup,outfit,limbs,shoes,extras) for o in c.objects]
for o in character:
    if not o.parent:o.parent=root
for o in head.objects[:]+hairgroup.objects[:]:
    o.location.z-=.052
    o.location.x*=1.08
    o.scale.x*=1.08
    if o.users_collection[0]==head and not any(o.name.startswith(k) for k in ("Porcelain","Pinna","Concha","Tragus","Button nose","Smile |")):
        for v in o.data.vertices:
            v.co.y+=(surface(v.co.x,v.co.z)-v.co.y)*.72
for o in character:
    if o.name.startswith(("Bare leg","Crew sock","Sock rib","Sneaker","Flat cotton lace","Canvas | side stripe","Shorts |","Pullover |","Kangaroo pocket","Pocket | topstitch","Short raglan sleeve","Sleeve |","Curled finger","Thumb","Palm","Forearm","Watch |")):
        factor=1.15
        o.location.x*=factor;o.scale.x*=factor
    if o.name.startswith(("Sneaker","Flat cotton lace","Canvas | side stripe")):
        o.location.z*=1.12;o.scale.z*=1.12
active=studio
floor=mat("Studio | lilac paper","DFD9EB")
platform=mat("Studio | lavender plinth","BDB6DB")
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.093));put(bpy.context.object,"Seamless paper",floor)
loft("Display plinth",[( -.09,.91,.75,0,0),(-.087,.929,.767,0,0),(-.077,.938,.773,0,0),(-.012,.938,.773,0,0),(-.004,.931,.766,0,0),(0,.917,.754,0,0)],platform,1,96,1)
world=bpy.data.worlds.new("Soft studio");scene.world=world;world.use_nodes=True;bg=world.node_tree.nodes["Background"];bg.inputs[0].default_value=(.86,.85,.99,1);bg.inputs[1].default_value=.31
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat("-Z","Y").to_euler()
def area(name,loc,energy,size,color):
    bpy.ops.object.light_add(type="AREA",location=loc);o=put(bpy.context.object,name,None)
    o.data.energy=energy;o.data.shape="DISK";o.data.size=size;o.data.color=color;aim(o,(0,0,1.4))
area("Key | warm",(-2.8,-4,5.8),360,4,(1,.86,.77))
area("Fill | cool",(3.1,-2.3,3.2),165,3.2,(.79,.85,1))
area("Softbox | crown",(-1.7,2.1,4.5),430,3,(1,.87,.77))
area("Softbox | eyes",(0,-4,2.24),56,2.1,(1,.95,.89))
bpy.ops.object.camera_add(location=(.46,-6.8,2.23));cam=put(bpy.context.object,"Portrait",None);scene.camera=cam;aim(cam,(0,-.012,1.277));cam.data.type="ORTHO";cam.data.ortho_scale=2.98
scene.render.engine="CYCLES";scene.cycles.samples=6 if DRAFT else 28;scene.cycles.use_denoising=True
scene.render.resolution_x=580 if DRAFT else 940;scene.render.resolution_y=660 if DRAFT else 1080;scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX";scene.view_settings.look="AgX - Medium High Contrast"
scene.render.image_settings.file_format="PNG";scene.render.filepath="//preview.png"
bpy.ops.object.select_all(action="DESELECT");root.select_set(True);bpy.context.view_layer.objects.active=root
for screen in bpy.data.screens:
    for area_ in screen.areas:
        if area_.type=="VIEW_3D":
            spc=area_.spaces.active;spc.region_3d.view_perspective="CAMERA";spc.shading.color_type="MATERIAL";spc.overlay.show_overlays=False
if not DRAFT:
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"scene.blend"),compress=True)
    for o in character:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/"chibi-mall-visitor.glb"),export_format="GLB",use_selection=True,export_apply=True,export_texcoords=False,export_yup=True,export_animations=False)
scene.render.filepath=str(OUT/"preview.png")
bpy.ops.render.render(write_still=True)

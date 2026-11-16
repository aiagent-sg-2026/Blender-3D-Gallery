"""Fitted quad head with inset eye and mouth loops, a painted iris and mobile eyelids."""
import math
from mathutils import Vector
from config import LANDMARKS
from meshkit import Part, TAU, clamp, mix, signed, loft, ellipsoid, section_tube

from skull_profile import PROFILE, skull

EYE_X,EYE_Z=.084,LANDMARKS["iris"]

def detail(x,z):
    cheeks=.016*math.exp(-((abs(x)-.124)/.056)**2-((z-.924)/.047)**2)
    nose=.018*math.exp(-(x/.023)**2-((z-.913)/.017)**2)
    bridge=.008*math.exp(-(x/.023)**2-((z-.940)/.038)**2)
    muzzle=.005*math.exp(-(x/.067)**2-((z-.868)/.025)**2)
    return cheeks+nose+bridge+muzzle

def face_y(x,z):
    rx,ry,cy=skull(z)
    return cy-ry*max(.00001,1-(abs(x)/rx)**2.32)**(1/2.32)-detail(x,z)

def face_uv(co):
    return clamp(.5+co[0]/.448),clamp((co[2]-.8)/.448)

def skin_keys(co):
    x,y,z=co
    if y>-.06: return {}
    lift=math.exp(-((abs(x)-.116)/.05)**2-((z-.917)/.033)**2)
    keys={"cheeks":(math.copysign(.0018,x)*lift,-.002*lift,.006*lift)}
    if z<.901 and abs(x)<.18:
        # The lower outer face ring follows the jaw so the laughing aperture
        # can descend below its neutral boundary without folding the chin skin.
        heights=(.800,.808,.823,.843,.854,.875,.901)
        shifts=(.011,.015,.022,.028,.024,.009,0)
        h=min(range(len(heights)-1),key=lambda i:abs(max(heights[i],min(z,heights[i+1]))-z))
        t=clamp((z-heights[h])/(heights[h+1]-heights[h]))
        dz=-mix(shifts[h],shifts[h+1],t)*math.exp(-(abs(x)/.105)**4)
        keys["open"]=(0,(face_y(x,z+dz)-face_y(x,z))*.30,dz)
    return keys

def mouth(u,v,mode="",depth=0):
    smile=float(mode=="smile"); opened=float(mode=="open"); rounded=float(mode=="round"); asym=float(mode=="asym")
    x=u*(.046+.014*smile-.025*rounded)+.007*asym
    z=.866+(.009+.008*smile-.010*rounded)*u*u+.005*asym*u-.009*opened
    z+=v*(.0017+.036*opened-.011*rounded)
    base=.866+.009*u*u+.0017*v
    surface=face_y(x,z) if not opened else .72*face_y(x,base)+.28*face_y(x,z)
    return Vector((x,surface+depth,z))

def build_skull():
    p=Part("Face","Head","Skin")
    n=32; half=n//2
    ring=[]
    # Boundary indices are polar on the head, with index 'half' facing the camera.
    coarse_rows={0,2,3,6,8,10,12,14,16,17,18}
    for level,(z,rx,ry,cy) in enumerate(PROFILE):
        row=[]
        for j in range(n):
            steps=abs(j-half)
            if (steps>=10 and level not in coarse_rows) or level==15:
                row.append(None);continue
            degrees=9*min(steps,5)+max(0,steps-5)*135/(half-5)
            a=math.copysign(math.radians(degrees),j-half)
            x=rx*math.sin(a)
            y=cy+(-1 if math.cos(a)>0 else 1)*ry*max(.000001,1-abs(math.sin(a))**2.32)**(1/2.32)
            if math.cos(a)>0:
                y-=detail(x,z)
                # The temporal plane turns inward immediately ahead of the ear.
                # Its recess gives the short side lock the reference's clearance
                # in the front and profile together.
                angle=math.atan2(abs(x),max(.001,cy-y))
                recess=.030*math.exp(-((angle-1.08)/.29)**2-((z-.931)/.049)**2)
                x-=math.copysign(recess*math.sin(angle),x)
                y+=recess*math.cos(angle)
            back=max(0.,-math.cos(a))
            lift=.065*back**.75*math.exp(-((z-.81)/.073)**2)
            # The lower occiput turns in behind the ear toward the neck.
            # The separate ear cup keeps its full outline over this transition.
            height=z+lift
            occiput=clamp((y-.009)/.049)*clamp((.209-y)/.056)
            occiput*=clamp((height-.805)/.056)*clamp((1.023-height)/.069)
            occiput*=clamp((abs(x)-.070)/.068)
            occiput=occiput*occiput*(3-2*occiput)
            x-=math.copysign(.043*occiput,x)
            y-=.010*occiput
            # Give the overlapping crown roots clearance above the visible forehead.
            crown=clamp((height-1.150)/.105)
            crown=crown*crown*(3-2*crown)
            x*=1-.057*crown
            y=cy+(y-cy)*(1-.057*crown)
            co=(x,y,height-.019*crown)
            row.append(p.vert(co,"head",skin_keys(co)))
        ring.append(row)
    holes=[(half-2,half+2,3,6,"mouth",0),
           (half+1,half+5,7,11,"eye",1),(half-5,half-1,7,11,"eye",-1)]
    def skinface(ids):
        p.face(ids,"face",[face_uv(p.xyz[k]) for k in ids])
    for j in range(n):
        k=(j+1)%n
        left=[i for i in range(len(PROFILE)) if ring[i][j] is not None]
        right=[i for i in range(len(PROFILE)) if ring[i][k] is not None]
        a=b=0
        while a<len(left)-1 and b<len(right)-1:
            i,h=left[a],right[b];next_a,next_b=left[a+1],right[b+1]
            if next_a==next_b:
                ids=[ring[i][j],ring[h][k],ring[next_b][k],ring[next_a][j]];a+=1;b+=1
                if any(l<=j<r and low<=i<high for l,r,low,high,_,_ in holes):continue
            elif next_a<next_b:
                ids=[ring[i][j],ring[h][k],ring[next_a][j]];a+=1
            else:
                ids=[ring[i][j],ring[h][k],ring[next_b][k]];b+=1
            skinface(ids)
    skinface(list(reversed(ring[0]))); skinface(ring[-1])
    for l,r,b,t,kind,sign in holes:
        edges=([ring[b][j] for j in range(l,r)] + [ring[i][r] for i in range(b,t)] +
               [ring[t][j] for j in range(r,l,-1)] + [ring[i][l] for i in range(t,b,-1)])
        cx,cz=(0,.869) if kind=="mouth" else (sign*EYE_X,EYE_Z)
        mid=[]; inner=[]
        for step,index in enumerate(edges):
            x,_,z=p.xyz[index]
            angle=math.atan2((z-cz)/(.034 if kind=="mouth" else .056),(x-cx)/(.061 if kind=="mouth" else .057))
            if kind=="mouth":
                if step==0:start_angle=angle
                angle=start_angle+TAU*step/len(edges)
            u,v=math.cos(angle),math.sin(angle)
            if kind=="mouth":
                co=mouth(u,v,depth=.0007)
                keys={k:mouth(u,v,k,.0007)-co for k in ("smile","open","round","asym")}
                outer=Vector(p.xyz[index]); m=co.lerp(outer,.38)
                m.y=face_y(m.x,m.z)-.0008
                outer_keys=skin_keys(outer)
                mid.append(p.vert(m,"head",{k:d*.62+Vector(outer_keys.get(k,(0,0,0)))*.38 for k,d in keys.items()}))
            else:
                x=cx+.046*u; z=cz+.046*v+.002*u*sign
                co=Vector((x,face_y(x,z)+.0005,z)); keys=skin_keys(co)
                outer=Vector(p.xyz[index]); m=co.lerp(outer,.35)
                m.y=face_y(m.x,m.z)
                mid.append(p.vert(m,"head",skin_keys(m)))
            inner.append(p.vert(co,"head",keys))
        for a,d in ((edges,mid),(mid,inner)):
            for j in range(len(a)):
                k=(j+1)%len(a); skinface([a[j],a[k],d[k],d[j]])
        if kind=="eye":
            co=(cx,face_y(cx,cz)-.0005,cz); center=p.vert(co,"head",skin_keys(co))
            for j in range(len(inner)):
                skinface([inner[j],inner[(j+1)%len(inner)],center])
        else:
            # The cavity is built against the actual boundary to stay sealed through every smile.
            co=mouth(0,0,depth=.0038)
            center=p.vert(co,"head",{key:mouth(0,0,key,.0038)-co for key in ("smile","open","round","asym")})
            for j in range(len(inner)):
                k=(j+1)%len(inner)
                a=start_angle+TAU*j/len(inner);b=start_angle+TAU*k/len(inner)
                p.face([inner[j],inner[k],center],"lip",[(.5+.48*math.cos(a),.5+.48*math.sin(a)),(.5+.48*math.cos(b),.5+.48*math.sin(b)),(.5,.5)])
    # Small surface rings shape the subtle button nose, merging flush into the face at the base.
    loops=[]
    for scale,bulge in ((1.,-.0026),(.68,.0013),(.32,.0030)):
        loop=[]
        for j in range(16):
            a=TAU*j/16
            x=.020*math.cos(a)*scale; z=.914+.0115*math.sin(a)*scale
            co=(x,face_y(x,z)-bulge,z); loop.append(p.vert(co,"head"))
        loops.append(loop)
    for outer,inside in zip(loops,loops[1:]):
        for j in range(16):
            k=(j+1)%16; skinface([outer[j],outer[k],inside[k],inside[j]])
    skinface(loops[-1])
    p.face_surface_count=len(p.xyz)
    # Ear cups slope towards the front. The concha is a depression inside the fleshy outer rim.
    for sign in (-1,1):
        layers=[]
        for rad,yd in ((.57,.021),(1.,.004),(.89,-.016),(.62,-.022),(.35,-.008)):
            loop=[]
            for j in range(12):
                a=TAU*j/12
                xx=sign*(.193+.035*rad*math.cos(a)-.72*yd)
                zz=.926+.055*rad*math.sin(a)+.005*rad*math.cos(a)
                co=(xx,.001+.045*rad*math.cos(a)+.69*yd,zz)
                loop.append(p.vert(co,"head"))
            layers.append(loop)
        for layer,(out,inside) in enumerate(zip(layers,layers[1:])):
            for j in range(12):
                k=(j+1)%12; ids=[out[j],out[k],inside[k],inside[j]]
                p.face(ids,"ear" if layer>=2 else "skin",[(.5+sign*(p.xyz[q][0]-.193*sign)/.079,.5+(p.xyz[q][2]-.926)/.111) for q in ids])
        p.face(layers[-1],"ear")
        p.face(reversed(layers[0]),"skin")
    return p


def build_eyes():
    eyes=Part("Iris_and_sclera","Eyes","Eyes")
    lines=Part("Eyelids_and_brows","Eyes","Hair")
    for sign,side in ((1,"L"),(-1,"R")):
        blink="blink_"+side
        def surface(u,v,mode="",rim=0):
            x=sign*EYE_X+u*.057
            arc=max(0,1-u*u)
            upper=max(v,0)
            z=EYE_Z + .0025*sign*u + .052*v - .011*upper**2 - .002*upper*arc
            if mode=="blink":
                x=sign*EYE_X+u*.0525
                z=EYE_Z-.007+.0205*arc+.0025*sign*u+.00015*v
            elif mode=="wide":
                z+=.006*v+.009*upper**2
            elif mode=="cheeks":
                z+=.0018*arc
            depth=.0018+.003*max(0,1-u*u-v*v)
            depth-=.0025*clamp((v-.88)/.12)
            if mode=="wide":depth+=.004*max(0,v)
            if mode=="blink": depth=.0025
            return Vector((x,face_y(x,z)-depth-rim,z))
        def eye_vert(part,u,v,rim=0):
            co=surface(u,v,rim=rim)
            return part.vert(co,"head",{name:surface(u,v,mode,rim)-co for name,mode in
                                       ((blink,"blink"),("wide","wide"),("cheeks","cheeks"))})
        loops=[]; uv={}
        for rad in (.50,1.):
            loop=[]
            for j in range(24):
                a=TAU*j/24
                u=rad*math.cos(a)
                v=rad*math.sin(a)*(1-.075*abs(math.cos(a)))
                index=eye_vert(eyes,u,v); loop.append(index); uv[index]=(.5+.5*u,.5+.5*v)
            loops.append(loop)
        c=eye_vert(eyes,0,0); uv[c]=(.5,.5)
        for j in range(24):
            k=(j+1)%24
            for ids in ([c,loops[0][j],loops[0][k]],[loops[0][j],loops[1][j],loops[1][k],loops[0][k]]):
                eyes.face(ids,"eye",[uv[i] for i in ids])
        # Sweep the upper lash around the eye, flaring very gently at the outer corner.
        rows=[]
        for j in range(15):
            t=j/14; a=math.pi*(1-t)
            u=math.cos(a); v=.965*math.sin(a)*(1-.075*abs(u))
            center=surface(u,v,rim=.005)
            lash=.0018+.0092*math.sin(math.pi*t)**.65+.0022*((1+sign*u)/2)**3
            row=[]
            for h in (-.65,.65):
                co=center.copy(); co.z+=h*lash
                co.y=face_y(co.x,co.z)-.0076
                delta={}
                for name,mode in ((blink,"blink"),("wide","wide"),("cheeks","cheeks")):
                    alt=surface(u,v,mode,.005)
                    alt.z+=h*(lash*.84 if mode=="blink" else lash)
                    alt.y=face_y(alt.x,alt.z)-(.0084 if mode=="wide" else .0076)
                    delta[name]=alt-co
                row.append(lines.vert(co,"head",delta))
            rows.append(row)
        for a,b in zip(rows,rows[1:]):
            lines.face([a[0],b[0],b[1],a[1]],"lash")
        # Eyebrows are rounded, tapering strips that remain clear of the eyelids.
        rows=[]
        for j in range(11):
            t=j/10; x=sign*(.048+.085*t)
            z=1.028+.006*math.sin(math.pi*t)-.002*t
            wat=(.0045+.0100*(1-t)**.65)*min(1,.42+4*t)
            row=[]
            for h,d in ((-1,0),(0,.003),(1,0)):
                zz=z+h*wat; co=Vector((x,face_y(x,zz)-.003-d,zz))
                keys={}
                for key,shift in (("browUp",.013),("browTilt",sign*.006+(.5-t)*.012)):
                    keys[key]=(0,face_y(x,zz+shift)-face_y(x,zz),shift)
                row.append(lines.vert(co,"head",keys))
            rows.append(row)
        for a,b in zip(rows,rows[1:]):
            for j in range(2):
                ids=[a[j],b[j],b[j+1],a[j+1]]
                lines.face(ids if sign>0 else list(reversed(ids)),"brow")


def build_mouth():
    p=Part("Teeth_and_tongue","Mouth","Skin")
    for tile,span,upper in (("teeth",.91,True),("tongue",.84,False)):
        rows=[]
        for j in range(15):
            u=span*(j/7-1); h=math.sqrt(max(0,1-u*u))
            inner=(.58+.13*u*u if upper else -.09-.34*u*u)*h
            vs=(inner,.93*h) if upper else (-.91*h,inner)
            row=[]
            for v in vs:
                depth=.0002 if upper else .001
                neutral=mouth(u,v,depth=depth)
                co=neutral.copy()
                # Park behind the upper/lower lip, leaving the tongue and teeth
                # at their normal depth as soon as the jaw starts to open.
                co.z+=.0032 if upper else -.0041
                co.y=face_y(co.x,co.z)+(.0014 if upper else .0018)
                keys={k:mouth(u,v,k,depth)-mouth(u,v,depth=depth) for k in ("smile","open","round","asym")}
                keys["round"].y+=.0053 if upper else .0010
                keys["open"]+=neutral-co
                if not upper:keys["open"].y-=.0016
                row.append(p.vert(co,"head",keys))
            rows.append(row)
        for a,b in zip(rows,rows[1:]):
            p.face([a[0],b[0],b[1],a[1]],tile)

def build():
    build_skull(); build_eyes(); build_mouth()


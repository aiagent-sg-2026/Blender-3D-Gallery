"""Tailored shirt and bifurcated jeans share a single skin across their seams."""
import math
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree
from config import LANDMARKS, SOCKETS, PICKUP_PRODUCT_SIZE, PICKUP_ROTATION_DEG
from meshkit import Part, loft, section_tube, ellipsoid, joint, TAU, clamp, mix, signed, reduce_surface

def spine(z):
    if z<.51: return joint("pelvis","spine",(z-.44)/.07)
    return joint("spine","chest",(z-.53)/.11)

def arm_weights(z,side):
    if z>.625: return "upperarm."+side
    if z>.556: return joint("forearm."+side,"upperarm."+side,(z-.556)/.069)
    if z>.480: return "forearm."+side
    return joint("hand."+side,"forearm."+side,(z-.453)/.027)

def leg_weights(z,side):
    if z>.356: return joint("thigh."+side,"pelvis",(z-.356)/.064)
    return joint("shin."+side,"thigh."+side,(z-.222)/.071)

def fit_grasp_surface(hand,rotation,center,half_size):
    """Wrap entire palm and digit faces around the test product at contact."""
    changes=hand.keys["pickup_grasp_R"]
    at=[rotation@(Vector(p)+Vector(changes.get(i,(0,0,0)))-center) for i,p in enumerate(hand.xyz)]
    sides=[(axis,direction) for axis in range(3) for direction in (-1,1)]
    guard=[{} for p in at]
    margin=.00035
    updated=True
    while updated:
        updated=False
        for face in hand.faces:
            if any(all(sign*at[i][axis]>=half_size[axis]+margin-1e-7 for i in face) for axis,sign in sides):
                continue
            # Separating the full polygon also separates both possible diagonals
            # of a quad. Merely pushing its vertices out can cut across a corner.
            def cost(side):
                axis,sign=side
                if any(guard[i].get(axis,sign)!=sign for i in face):return math.inf
                return sum(max(0,half_size[axis]+margin-sign*at[i][axis])**2 for i in face)
            updated=True
            axis,sign=min(sides,key=cost)
            if not math.isfinite(cost((axis,sign))):raise ValueError("Incompatible grasp constraints")
            for i in face:
                guard[i][axis]=sign
                at[i][axis]=sign*max(sign*at[i][axis],half_size[axis]+margin)
    inverse=rotation.inverted()
    for i,point in enumerate(at):
        if guard[i]:changes[i]=tuple(center+inverse@point-Vector(hand.xyz[i]))

    # The hand approaches from the character's right (-X). Every open
    # face must clear the product during that lateral insertion. Retain a
    # separating plane shared with its closed pose throughout finger curl.
    open_sides=[s for s in sides if s!=(0,1)]
    open_guard=[{} for p in at]
    for face in hand.faces:
        choices=[s for s in (*open_sides,(0,1)) if all(
            s[1]*at[i][s[0]]>=half_size[s[0]]+margin-1e-7 for i in face)]
        axis,sign=choices[0]
        for i in face:open_guard[i][axis]=sign
    opened=[v.copy() for v in at]
    for i,v in enumerate(opened):
        if hand.xyz[i][2]<.444:
            v.y*=1.15
            v.z*=1.09
    updated=True
    while updated:
        updated=False
        for face in hand.faces:
            if any(all(sign*opened[i][axis]>=half_size[axis]+margin-1e-7 for i in face) for axis,sign in open_sides):
                continue
            def open_cost(side):
                axis,sign=side
                if any(open_guard[i].get(axis,sign)!=sign for i in face):return math.inf
                cost=sum(max(0,half_size[axis]+margin-sign*opened[i][axis])**2 for i in face)
                return cost*(.75 if side==(2,1) else 1.)
            axis,sign=min(open_sides,key=open_cost)
            if not math.isfinite(open_cost((axis,sign))):raise ValueError("No collision-free insertion for grasp")
            for i in face:
                open_guard[i][axis]=sign
                opened[i][axis]=sign*max(sign*opened[i][axis],half_size[axis]+margin)
            updated=True
    open_key={}
    for i,point in enumerate(opened):
        delta=center+inverse@point-Vector(hand.xyz[i])
        if delta.length>1e-6:open_key[i]=tuple(delta)
    hand.keys["pickup_open_R"]=open_key

def body():
    skin=Part("Arms_neck","Body","Skin")
    grip_rotation=Euler(tuple(math.radians(v) for v in PICKUP_ROTATION_DEG)).to_quaternion()
    grip_center=Vector(SOCKETS["Socket_Palm_R"][1])
    sx,sy,sz=PICKUP_PRODUCT_SIZE
    grip_half=Vector((sx,sz,sy))*.5
    def fit_pad(rest,grasped):
        local=grip_rotation@(grasped-grip_center)
        depths=[grip_half[i]-abs(local[i]) for i in range(3)]
        axis=min(range(3),key=depths.__getitem__)
        if depths[axis]>-.00035:
            local[axis]=math.copysign(grip_half[axis]+.00035,local[axis])
            grasped=grip_center+grip_rotation.inverted()@local
        return grasped-Vector(rest)
    loft(skin,[(0,0,.718,.066,.057),(0,0,.75,.058,.055),(0,-.001,.786,.052,.052),
               (0,-.007,.821,.060,.058),(0,-.005,.854,.064,.062)],12,"skin",lambda c,i,j:joint("neck","head",(c[2]-.778)/.04))
    for s,side in ((1,"L"),(-1,"R")):
        def arm(co,i,j): return arm_weights(co[2],side)
        rows=[(.203,-.029,.459,.029,.027),(.201,-.025,.486,.030,.028),
              (.194,-.020,.519,.033,.031),(.180,-.011,.566,.035,.036),
              (.172,-.005,.590,.034,.036),(.163,-.001,.622,.036,.038),
              (.154,-.001,.633,.036,.037)]
        hand=Part("Hand_"+side,"Hands","Skin")
        name="hand."+side
        # The last three fingers share one fleshy outline. Index and thumb can articulate distinctly.
        palm=[(.222,-.038,.367,.012,.013),(.219,-.040,.374,.024,.020),
              (.215,-.035,.392,.032,.026),(.214,-.032,.414,.035,.028),
              (.209,-.028,.444,.034,.027),(.205,-.028,.464,.030,.026),(.202,-.027,.484,.029,.026)]
        def grip(co,i,j):
            t=clamp((.435-co[2])/.064)
            keys={"grip_"+side:(-s*.017*t,-.010*t,.017*t)}
            # The three joined fingers flex under the product. Preserve the
            # wrist and forearm when the right hand closes around the box.
            if side=="R":
                at=Vector(co)
                if i<4:
                    closed=[(-.182,-.054,.378),(-.193,-.051,.378),
                            (-.216,-.045,.390),(-.218,-.031,.416)]
                    x,y,z=palm[i][:3]
                    at+=Vector(closed[i])-Vector((-x,y,z))
                keys["pickup_grasp_R"]=fit_pad(co,at)
            return keys
        chain=palm[:-1]+rows[1:]
        loft(hand,[(s*x,y,z,rx,ry) for x,y,z,rx,ry in chain],8,"skin",arm,keys=grip)
        for label,coords,ww,dd in [
            ("index",[(.204,-.047,.423),(.203,-.055,.405),(.205,-.056,.382),(.210,-.051,.371)],
             [.014,.013,.012,.006],[.013,.012,.011,.006]),
            ("thumb",[(.193,-.032,.433),(.183,-.044,.422),(.177,-.051,.408),(.178,-.052,.398)],
             [.017,.016,.013,.006],[.015,.015,.012,.006])]:
            rest=[Vector((s*x,y,z)) for x,y,z in coords]
            grasp={"index":[(-.204,-.047,.423),(-.208,-.067,.409),
                            (-.202,-.078,.394),(-.185,-.0828,.390)],
                   "thumb":[(-.193,-.032,.433),(-.177,-.039,.435),
                            (-.1585,-.048,.428),(-.153,-.060,.412)]}
            closed=[Vector(v) for v in grasp[label]]
            def finger(co,i,j):
                t=i/(len(coords)-1)
                keys={"grip_"+side:(-s*.012*t,-.012*t,.018*t),
                      "point_"+side:(s*.002*t,-.008*t,-.033*t) if label=="index" else (s*.006*t,-.003*t,.006*t)}
                if side=="R":
                    lo,hi=max(0,i-1),min(len(rest)-1,i+1)
                    turn=(rest[hi]-rest[lo]).rotation_difference(closed[hi]-closed[lo])
                    keys["pickup_grasp_R"]=fit_pad(co,closed[i]+turn@(Vector(co)-rest[i]))
                return keys
            section_tube(hand,rest,ww,dd,(1,0,0),"skin",name,7,keys=finger,tip_extension=.0048)
        if side=="R":
            fit_grasp_surface(hand,grip_rotation,grip_center,grip_half)

def shirt():
    p=Part("Crewneck_shirt","Shirt","Cloth")
    n=20
    rows=[(LANDMARKS["hem"]-.002,.139,.104),(.455,.146,.108),(.481,.147,.104),(.53,.14,.095),
          (.595,.135,.089),(.656,.134,.087),(.704,.126,.082),(.739,.112,.074),(.767,.075,.071)]
    rings=[]
    def row_uv(i,j): return ((j/n+.5)%1,(rows[i][0]-.448)/.312)
    for i,(z,rx,ry) in enumerate(rows):
        row=[]
        for j in range(n):
            a=TAU*j/n
            hem=(.009*math.cos(3*a+.4)+.004*math.sin(5*a)) * math.exp(-((z-.448)/.060)**2)
            folds=(1+(.025*math.cos(5*a)+.022*math.sin(3*a))*math.exp(-((z-.465)/.07)**2))
            x=rx*math.sin(a)*folds; y=-ry*math.cos(a)*folds
            h=z+hem+(.010*(1-abs(math.sin(a))) if i==7 else 0)
            if i<3:h+=.011*math.exp(-((x+.028)/.038)**2)*max(0,math.cos(a))
            if i==8:h-=.023*max(0.,math.cos(a))
            weights=spine(h)
            if i>=5 and abs(x)>.086:
                side="L" if x>0 else "R"
                weights=joint("chest","clavicle."+side,.45*clamp((abs(x)-.086)/.03))
            row.append(p.vert((x,y,h),weights))
        rings.append(row)
    holes=[(3,7,"L",1),(13,17,"R",-1)]
    for i in range(len(rows)-1):
        for j in range(n):
            if 4<=i<7 and any(l<=j<r for l,r,_,_ in holes):continue
            k=(j+1)%n
            ids=[rings[i][j],rings[i][k],rings[i+1][k],rings[i+1][j]]
            p.face(ids,"shirt",[(b/n,(rows[a][0]-.448)/.312) for a,b in ((i,j),(i,j+1),(i+1,j+1),(i+1,j))])
    # Return the hem into the garment; the back remains intact when the backpack is hidden.
    inside=[]
    for i in rings[0]:
        x,y,z=p.xyz[i]; inside.append(p.vert((x*.95,y*.95,z+.005),spine(z)))
    for j in range(n):
        k=(j+1)%n; p.face([inside[j],inside[k],rings[0][k],rings[0][j]],"shirt")
    neck=rings[-1]
    for radius,height in ((.069,.768),(.062,.769),(.057,.764)):
        inner=[]
        for j in range(n):
            a=TAU*j/n; inner.append(p.vert((radius*math.sin(a),-radius*.88*math.cos(a),height-.024*max(0,math.cos(a))),"chest"))
        for j in range(n):
            k=(j+1)%n; p.face([neck[j],neck[k],inner[k],inner[j]],"knit",[(j/n,0),((j+1)/n,0),((j+1)/n,1),(j/n,1)])
        neck=inner
    # Each armhole shares its perimeter with the sleeve. Carry its angular order out along the arm.
    for l,r,side,s in holes:
        ring=([rings[4][j] for j in range(l,r)]+[rings[i][r] for i in range(4,7)]
              +[rings[7][j] for j in range(r,l,-1)]+[rings[i][l] for i in range(7,4,-1)])
        center=Vector((s*.124,0,.663))
        tangent=Vector((s*.47,0,-.88)).normalized()
        across=Vector((s*.88,0,.47)).normalized()
        angles=[math.atan2((Vector(p.xyz[i])-center).dot(across),p.xyz[i][1]) for i in ring]
        for xx,zz,depth,radius,t in ((.144,.669,.065,.052,.65),(.178,.619,.057,.050,1),(.184,.607,.059,.052,1),
                                    (.184,.605,.055,.048,1)):
            new=[]
            for a in angles:
                co=Vector((s*xx,0,zz))+Vector((0,depth*math.cos(a),0))+across*(radius*math.sin(a))
                new.append(p.vert(co,joint("clavicle."+side,"upperarm."+side,t)))
            for j in range(len(ring)):
                k=(j+1)%len(ring)
                p.face([ring[j],ring[k],new[k],new[j]],"knit" if zz<.609 else "shirt",[(j/len(ring),.18),(k/len(ring),.18),(k/len(ring),.82),(j/len(ring),.82)])
            ring=new

def jeans():
    p=Part("Straight_denim","Jeans","Cloth")
    # Before the crotch both panels share an inseam. Above it they meet their opposite side at centre front/back.
    rows=[(.081,.091,.070,.077),(.148,.092,.080,.081),(.158,.093,.081,.085),
          (.172,.093,.078,.080),(.186,.092,.074,.077),(.207,.090,.070,.074),(.244,.088,.071,.072),
          (.255,.088,.077,.078),(.277,.086,.077,.080),
          (.30,.084,.071,.077),(.345,.078,.072,.081),(.365,.074,.074,.083),
          (.404,0,.146,.091),(.443,0,.145,.095),(.466,0,.142,.088)]
    reg={}; n=7; crotch={}
    for side,s in (("L",1),("R",-1)):
        for back in (False,True):
            layers=[]
            for i,(z,cx,rx,ry) in enumerate(rows):
                row=[]
                for j in range(n+1):
                    u=j/n
                    if z<=.365:
                        x=cx+rx*math.cos(math.pi*u)
                        y=ry*math.sin(math.pi*u)
                        if z==.365:y+=.046*u**8
                    else:
                        x=rx*math.cos(math.pi*u/2)
                        y=ry*math.sin(math.pi*u/2)
                    zz=z
                    if .13<=z<=.35:
                        zz+=.003*math.sin(math.pi*u)*math.sin(i*1.73+.75*s)
                        y*=1+.020*math.cos(math.pi*u*2+i*.9)
                        y+=.0012*math.sin(math.pi*u)*math.cos(5*u+.6*s+i*.9)*(
                            math.exp(-((z-.18)/.045)**2)+.6*math.exp(-((z-.26)/.035)**2))
                    co=(s*x,.006+(1 if back else -1)*y,zz)
                    key=tuple(round(v,6) for v in co)
                    if key not in reg:reg[key]=p.vert(co,leg_weights(z,side))
                    row.append(reg[key])
                layers.append(row)
            crotch[side,back]=(layers[-5][-1],layers[-4][-1])
            for i in range(len(rows)-1):
                for j in range(n):
                    ids=[layers[i][j],layers[i][j+1],layers[i+1][j+1],layers[i+1][j]]
                    uvs=[(b/n,(rows[a][0]-.081)/.385) for a,b in ((i,j),(i,j+1),(i+1,j+1),(i+1,j))]
                    if (s>0) != back: ids.reverse(); uvs.reverse()
                    p.face(ids,"jeanBack" if back else ("jeanFront" if side=="L" else "jeanPlain"),uvs)
        cuff=[(.093,.005,.092,.074,.081),(.093,.004,.096,.079,.084),(.093,.005,.126,.081,.085),
              (.092,.006,LANDMARKS["cuff"]+.004,.079,.082),(.092,.006,.132,.075,.079)]
        cuff_rings=loft(p,[(s*x,y,z,rx,ry) for x,y,z,rx,ry in cuff],12,"cuff","shin."+side,tilt=-.032*s,close=False)
        for row in cuff_rings:
            for j,index in enumerate(row):
                x,y,z=p.xyz[index];a=TAU*j/12
                p.xyz[index]=(x,y,z+.0035*math.sin(3*a+.6*s)+.002*math.sin(5*a))
    # A broad saddle closes the inner-leg junction instead of pinching both panels to one point.
    for side in ("L","R"):
        lower,front=crotch[side,False];_,back=crotch[side,True]
        p.face([lower,front,back] if side=="L" else [lower,back,front],"jeanPlain")

def shoes():
    for s,side in ((1,"L"),(-1,"R")):
        p=Part("Sneaker_"+side,"Shoes","Leather"); bone="foot."+side; x=s*.096
        outsole=[(x,-.033,.000,.071,.116,2.9),(x,-.034,.004,.078,.124,2.8),
                 (x,-.034,.030,.079,.125,2.8),
                 (x,-.033,.035,.076,.122,2.8)]
        sides=14
        loft(p,outsole,sides,"sole",bone)
        vamp=[(x,-.031,.031,.076,.122,2.7),
              (x,-.030,.057,.072,.116,2.6),(x,-.025,.071,.068,.106,2.5),
              (x,-.012,.082,.064,.092,2.4),(x,.002,.099,.059,.074,2.3),
              (x,.011,.111,.056,.066,2.2),(x,.011,.114,.051,.060,2.2)]
        def upper_uv(i,j,corners):
            start=((j+sides//2)%sides)/sides
            return "shoe",[(start+(b-j)/sides,a/(len(vamp)-1)) for a,b in corners]
        loft(p,vamp,sides,"shoe",bone,uv=upper_uv,close=False)
        def section_at(front_y):
            for low,high in zip(vamp,vamp[1:]):
                a,b=low[1]-low[4],high[1]-high[4]
                if front_y<=b:
                    t=clamp((front_y-a)/(b-a))
                    return tuple(mix(a,b,t) for a,b in zip(low,high))
            return vamp[-1]
        def upper_point(dx,front_y,lift):
            _,cy,z,rx,ry,power=section_at(front_y)
            y=cy-ry*max(0,1-(abs(dx)/rx)**power)**(1/power)
            return x+dx,y,z+lift
        # A raised toe overlay creates a real panel boundary above the continuous upper.
        cap=[]
        for _,cy,z,rx,ry,power in vamp[:4]:
            row=[]
            for j in range(9):
                a=-math.pi/2+math.pi*j/8
                row.append(p.vert((x+(rx+.002)*signed(math.sin(a),2/power),
                                   cy-(ry+.002)*signed(math.cos(a),2/power),z+.001),bone))
            cap.append(row)
        for i,(a,b) in enumerate(zip(cap,cap[1:])):
            for j in range(8):
                p.face([a[j],a[j+1],b[j+1],b[j]],"shoe",[(.25+j/16,i/6),(.25+(j+1)/16,i/6),
                       (.25+(j+1)/16,(i+1)/6),(.25+j/16,(i+1)/6)])
        # Keep these layers separate while the shoe upper is faired to its final silhouette.
        p=Part("Lacing_"+side,"Shoes","Leather");p.fit_lifts={}
        def fitted_vertex(dx,front_y,lift):
            index=p.vert(upper_point(dx,front_y,lift),bone)
            p.fit_lifts[index]=lift
            return index
        rows=[]
        for i,(cy,w) in enumerate(((-.130,.040),(-.119,.044),(-.108,.044),(-.096,.043),(-.081,.039))):
            row=[]
            for j in range(7):
                u=j/6; dx=w*(u*2-1)
                row.append(fitted_vertex(dx,cy,.0015+.0035*(1-(2*u-1)**2)))
            rows.append(row)
        for i in range(4):
            for j in range(6):
                p.face([rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]],"laces",
                       [(j/6,i/4),((j+1)/6,i/4),((j+1)/6,(i+1)/4),(j/6,(i+1)/4)])


        for sign in (-1,1):
            rows=[]
            for i in range(5):
                front_y=mix(-.136,-.074,i/4);row=[]
                for j in range(3):
                    u=j-1;dx=sign*(.047+.007*u)
                    row.append(fitted_vertex(dx,front_y,.0015+.0015*(1-u*u)))
                rows.append(row)
            for i,(a,b) in enumerate(zip(rows,rows[1:])):
                for j in range(2):
                    face=[a[j],b[j],b[j+1],a[j+1]]
                    uv=[(j/2,i/4),(j/2,(i+1)/4),((j+1)/2,(i+1)/4),((j+1)/2,i/4)]
                    p.face(face[::-1] if sign>0 else face,"eyelets",uv[::-1] if sign>0 else uv)
        for k,cy in enumerate((-.122,-.110,-.098,-.086)):
            for direction in (-1,1):
                grid=[]
                for j in range(4):
                    u=j/1.5-1;row=[]
                    for dv in (-.0017,.0017):
                        front_y=cy+dv+.006*u*direction
                        lift=.006+.001*(1-u*u)+(.0008 if direction>0 else 0)
                        row.append(fitted_vertex(.050*u,front_y,lift))
                    grid.append(row)
                for a,b in zip(grid,grid[1:]):p.face([a[0],b[0],b[1],a[1]],"teeth")


def fit_lacing(objects):
    uppers={obj.name:obj for obj in objects if obj.name.startswith("Sneaker_")}
    for obj in objects:
        if not obj.name.startswith("Lacing_"):continue
        reduce_surface(obj,92)
        shoe=uppers[obj.name.replace("Lacing_","Sneaker_")]
        shoe.data.calc_loop_triangles()
        tree=BVHTree.FromPolygons([v.co for v in shoe.data.vertices],
                                 [tuple(t.vertices) for t in shoe.data.loop_triangles],all_triangles=True)
        group=obj.vertex_groups["Surface lift"]
        for vertex in obj.data.vertices:
            lift=next(g.weight*.01 for g in vertex.groups if g.group==group.index)
            point=tree.ray_cast(Vector((vertex.co.x,vertex.co.y,.30)),Vector((0,0,-1)))[0]
            if point is None:raise ValueError(f"{obj.name}: lacing extends outside the shoe upper")
            vertex.co.z=point.z+lift
        obj.vertex_groups.remove(group)
        obj.data.update()

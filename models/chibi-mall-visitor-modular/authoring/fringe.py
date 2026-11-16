"""The two sides of each fringe lock were plotted on the main front-view crop.
Coordinates are construction guides only. All exported surfaces and texels are original.
"""
import math
import bpy
from mathutils import Vector
import guides
from head import skull,face_y
from config import HAIR_RADII
from meshkit import spline,clamp

# Paired silhouettes in original sheet pixels, beginning at the off-centre part.
OUTLINES={
 "Sweep at part":(
 [(419,86),(412,68),(393,65),(374,76),(356,96),(345,120),(330,143),(314,156)],
 [(419,102),(407,87),(391,88),(378,103),(366,126),(351,145),(331,157),(314,157)]),
 "Forehead sweep":(
 [(416,92),(408,77),(393,77),(378,88),(365,108),(356,131),(341,158)],
 [(418,107),(409,99),(398,104),(389,116),(376,131),(359,144),(341,160)]),
 "Falling fringe":(
 [(418,101),(411,82),(392,79),(377,89),(367,107),(366,126),(375,144),(383,149)],
 [(420,108),(415,97),(407,96),(400,106),(395,121),(391,135),(388,146),(385,151)]),
 "Central curl":(
 [(413,103),(407,89),(398,86),(389,97),(385,112),(386,127),(394,143)],
 [(415,109),(407,101),(401,100),(396,111),(394,123),(397,135),(395,143)]),
 "Part return":(
 [(421,100),(425,83),(438,81),(451,90),(462,107),(465,126),(457,144),(451,151)],
 [(419,108),(426,105),(435,109),(442,121),(444,135),(445,144),(449,150),(451,151)]),
 "Long outer sweep":(
 [(421,78),(413,61),(395,54),(376,56),(355,67),(338,79),(319,88),(301,114),(295,119)],
 [(419,92),(407,78),(390,74),(373,82),(354,96),(338,108),(321,119),(304,124),(295,120)]),
 "Left sweep":(
 [(421,82),(431,74),(445,79),(458,91),(469,107),(477,124),(484,132)],
 [(420,96),(431,89),(442,95),(451,108),(460,125),(473,134),(484,133)]),
 "Crown swoop":(
 [(416,67),(407,56),(390,52),(372,55),(356,63),(342,73),(322,80),(319,78)],
 [(417,76),(406,66),(392,62),(375,65),(359,73),(343,80),(329,84),(319,80)]),
}

BACK_OUTLINES={
 "Lower back fan":(
 [(1071,78),(1043,103),(1029,133),(1036,153),(1050,164),(1064,182),(1072,207),(1082,223)],
 [(1078,86),(1060,112),(1048,143),(1030,171),(1040,188),(1052,205),(1070,218),(1082,223)]),
 "Occipital sweep":(
 [(1072,66),(1092,82),(1110,118),(1114,141),(1105,164),(1087,190),(1075,212)],
 [(1075,74),(1082,102),(1082,143),(1074,163),(1068,183),(1067,201),(1075,212)]),
 "Back crown":(
 [(1079,77),(1070,68),(1059,74),(1048,91),(1044,111),(1049,130),(1055,140)],
 [(1085,85),(1078,87),(1070,100),(1063,116),(1059,130),(1057,137),(1055,140)]),
 "Back left arc":(
 [(1072,76),(1052,77),(1034,88),(1021,108),(1014,127),(1006,139)],
 [(1071,87),(1057,95),(1044,110),(1033,128),(1019,140),(1006,140)]),
 "Back right arc":(
 [(1081,80),(1102,76),(1121,85),(1138,104),(1149,127),(1156,144)],
 [(1084,94),(1101,101),(1114,117),(1128,135),(1143,147),(1156,145)]),
 "Upper back left":(
 [(1042,95),(1027,107),(1016,128),(1010,150),(1017,168),(1026,175)],
 [(1043,113),(1038,130),(1037,148),(1037,161),(1031,172),(1026,175)]),
 "Upper back right":(
 [(1081,70),(1097,77),(1106,108),(1104,128),(1092,146),(1075,156)],
 [(1070,85),(1072,99),(1067,128),(1066,142),(1069,152),(1075,157)]),
 "Nape left":(
 [(1072,76),(1052,91),(1040,114),(1040,131),(1055,145),(1061,167),(1058,188),(1067,212)],
 [(1078,83),(1065,101),(1053,123),(1038,146),(1041,165),(1044,183),(1055,201),(1067,213)]),
 "Nape middle":(
 [(1076,77),(1091,91),(1096,111),(1081,131),(1097,145),(1100,165),(1091,184),(1082,198)],
 [(1081,88),(1087,108),(1081,128),(1077,146),(1080,161),(1079,177),(1080,190),(1082,198)]),
 "Nape right":(
 [(1078,77),(1102,88),(1124,106),(1137,127),(1147,149),(1143,173),(1126,198),(1109,218)],
 [(1084,84),(1107,101),(1120,126),(1128,144),(1129,163),(1123,181),(1116,202),(1109,218)]),
 "Nape overlap":(
 [(1108,160),(1118,178),(1112,198),(1097,215),(1087,225)],
 [(1098,176),(1097,191),(1094,207),(1089,219),(1087,225)]),
}

SIDE_OUTLINES={
 "Upper cascade":(
 [(838,68),(854,70),(870,83),(884,102),(892,114),(901,120)],
 [(835,80),(840,97),(854,112),(872,120),(889,123),(901,120)]),
 "Middle cascade":(
 [(833,79),(821,83),(815,96),(819,111),(835,124),(856,131),(865,128)],
 [(838,84),(836,96),(839,110),(847,120),(856,124),(863,127),(865,128)]),
 "Ear sweep":(
 [(818,99),(807,109),(803,125),(810,140),(826,148),(844,151),(852,149)],
 [(825,109),(820,125),(825,137),(835,144),(844,147),(849,149),(852,149)]),
 "Rear curtain":(
 [(856,69),(873,78),(890,100),(907,124),(922,149),(928,164)],
 [(862,81),(870,103),(882,126),(900,148),(917,160),(928,164)]),
 "Lower cascade":(
 [(870,116),(887,129),(899,151),(899,173),(889,192),(873,211)],
 [(858,133),(869,150),(876,170),(875,188),(872,202),(873,211)]),
}

def location(px,rear=False,side=0):
    scale=1.30/451
    x=((1082-px[0]) if rear else (px[0]-390))*scale;z=(505-px[1])*scale
    lat=clamp((z-1.062)/HAIR_RADII[2],-.99,.99)
    c=(1-lat*lat)**.41
    rx=HAIR_RADII[0]*c;ry=HAIR_RADII[1]*c
    if side:
        y=(px[0]-856)*scale
        x=side*rx*math.sqrt(max(.012,1-((y-.008)/ry)**2))
        sx,sy,cy=skull(z)
        if abs(y-cy)<sy:
            x=side*max(abs(x),sx*max(.00001,1-(abs(y-cy)/sy)**2.32)**(1/2.32)+.013)
        return Vector((x,y,z))
    y=.008+(-1 if not rear else 1)*ry*math.sqrt(max(.012,1-(x/rx)**2))
    if abs(x)<skull(z)[0] and z<1.26:
        if rear:
            sx,sy,cy=skull(z)
            y=max(y,cy+sy*max(.00001,1-(abs(x)/sx)**2.32)**(1/2.32)+.030)
        else:y=min(y,face_y(x,z)-.007)
    return Vector((x,y,z))

def add(p,name,collection,rear=False,side=0,scalp_tree=None):
    edges=SIDE_OUTLINES[name] if side else BACK_OUTLINES[name] if rear else OUTLINES[name]
    guide_name=("Left " if side>0 else "Right ")+name if side else name
    if rear:
        expanded=[[],[]]
        for a,b in zip(*edges):
            a,b=Vector(a),Vector(b);center=(a+b)*.5
            expanded[0].append(tuple(center+(a-center)*1.08))
            expanded[1].append(tuple(center+(b-center)*1.08))
        edges=expanded
    steps=max(12,len(edges[0])*2)
    section=((0,0),(.03806,.38268),(.14645,.7071),(.30866,.92388),(.5,1.),
             (.69134,.92388),(.85355,.7071),(.96194,.38268),(1.,0),
             (.85355,-.38891),(.5,-.55),(.14645,-.38891))
    for index,points in enumerate(edges):
        curve=bpy.data.curves.new(guide_name+" outline","CURVE");curve.dimensions="3D"
        shape=curve.splines.new("POLY");shape.points.add(len(points)-1)
        for dest,xy in zip(shape.points,points):dest.co=(*location(xy,rear,side),1)
        obj=bpy.data.objects.new(guide_name+(" inner" if index else " outer"),curve);collection.objects.link(obj)
        obj.hide_render=True
        guides.bind(obj,len(p.xyz),steps+1,[u if index else 1-u for u,_ in section])
    axis=0 if side else 1
    direction=side if side else 1 if rear else -1
    outward=Vector((0,0,0));outward[axis]=direction
    path=[];widths=[];edge_vectors=[]
    for i in range(steps+1):
        a,b=[spline(points,i/steps) for points in edges]
        co=location((a+b)*.5,rear,side)
        if scalp_tree:
            origin=co.copy();origin[axis]=float(direction)
            hit,*_=scalp_tree.ray_cast(origin,-outward,1.)
            if hit is not None:co[axis]=hit[axis]
        path.append(co)
        widths.append(max(.001,(a-b).length*(1.30/451)*.5))
        edge_vectors.append(location(b,rear,side)-location(a,rear,side))
    rings=[]
    for i,center in enumerate(path):
        t=i/steps
        tangent=(path[min(steps,i+1)]-path[max(0,i-1)]).normalized()
        up=(outward-tangent*outward.dot(tangent)).normalized()
        across=up.cross(tangent).normalized()
        if across.dot(edge_vectors[i])<0:across=-across
        ridge=min(.035,.80*widths[i]) if rear or side else min(.047,1.2*widths[i])
        if rear and name in ("Back crown","Upper back right"):ridge+=.018*math.exp(-((t-.28)/.27)**2)
        if rear and name=="Occipital sweep":ridge+=.012*math.sin(math.pi*t)**1.2
        lift=(.016 if rear or side else .009)*math.sin(math.pi*t)**.6
        root=.006*(1-clamp(t/.12))**2
        row=[]
        for u,h in section:
            transverse=(2*u-1)*widths[i]
            depth=h*ridge+max(0,h)*lift-.60*transverse*transverse/.22-root
            depth-=.004*abs(2*u-1)**6
            if rear:depth-=.008*t**8
            row.append(p.vert(center+across*transverse+up*depth,"head"))
        rings.append(row)
    a,b,c=[Vector(p.xyz[k]) for k in (rings[steps//2][2],rings[steps//2][3],rings[steps//2+1][3])]
    reverse=(b-a).cross(c-a).dot(outward)<0
    n=len(section)
    for i in range(steps):
        for j in range(n):
            k=(j+1)%n;ids=[rings[i][j],rings[i][k],rings[i+1][k],rings[i+1][j]]
            uv=[(j/n,1-i/steps),((j+1)/n,1-i/steps),((j+1)/n,1-(i+1)/steps),(j/n,1-(i+1)/steps)]
            p.face(ids[::-1] if reverse else ids,"hair",uv[::-1] if reverse else uv)
    p.face(rings[0] if reverse else rings[0][::-1],"hair")
    p.face(rings[-1][::-1] if reverse else rings[-1],"hair")

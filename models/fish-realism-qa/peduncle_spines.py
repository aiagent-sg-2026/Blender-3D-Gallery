"""Small original forward-curving peduncle thorns for the triggerfish study."""
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build_peduncle_spines(builder,config,profile,flank):
 if not config.get('peduncle_thorns'):return
 body=next(o for o in builder.ROOT.children_recursive if o.name.startswith('Skin_AnatomicalProfile'));tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 material=builder.material('Peduncle_ThornSkin',(.20,.23,.12),.57)
 for side in [-1,1]:
  for row in range(5):
   for index in range(3):
    x=.82+index*.095;hi,lo,width=profile(x);z=(hi+lo)/2+(row-2)*(hi-lo)*.11
    point=Vector((x,flank(x,z,side),z));hit,normal,_,_=tree.find_nearest(point);root=hit-normal*.002;vertices=[];uv=[];faces=[]
    for ring in range(5):
     t=ring/4;p=root+Vector((-.025*t*t,side*.011*t,.002*t));radius=max(.00012,.0025*(1-t))
     for j in range(7):
      a=2*math.pi*j/6;vertices.append(p+Vector((radius*math.cos(a),0,radius*math.sin(a))));uv.append((j/6,t))
    for ring in range(4):
     for j in range(6):k=ring*7+j;faces.append((k,k+1,k+8,k+7))
    faces.extend([tuple(range(5,-1,-1)),tuple(28+j for j in range(6))]);builder.mesh('Peduncle_Thorn_%s_%d_%d'%(side,row,index),vertices,faces,material,uv)

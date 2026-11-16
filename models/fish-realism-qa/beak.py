"""Small fused dental plates projected onto a closed parrotfish lip surface."""
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build_beak(builder,config):
 if not config.get('dental_plates'):return
 body=next(o for o in builder.ROOT.children_recursive if o.name.startswith('Skin_AnatomicalProfile'))
 tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 material=builder.material('DentalPlate_Ivory',(.69,.66,.52),.41)
 center=config.get('mouth_start_z',-.07)
 for sign in [-1,1]:
  vertices=[];uv=[];faces=[];rings=12;segments=48
  for i in range(rings+1):
   r=max(.00001,i/rings)
   for j in range(segments+1):
    angle=2*math.pi*j/segments;y=.036*r*math.cos(angle);z=center+sign*.013+.009*r*math.sin(angle)
    hit,_,_,_=tree.ray_cast(Vector((-2,y,z)),Vector((1,0,0)),1)
    assert hit is not None,'Dental plates must meet the real closed snout'
    vertices.append((hit.x-.002-.005*(1-r*r),y,z));uv.append((.5+.5*r*math.cos(angle),.5+.5*r*math.sin(angle)))
  for i in range(rings):
   for j in range(segments):
    k=i*(segments+1)+j;faces.append((k,k+1,k+segments+2,k+segments+1))
  builder.mesh('DentalPlate_'+str(sign),vertices,faces,material,uv)

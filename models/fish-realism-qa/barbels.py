"""Create tapered anatomical mouth barbels; body skinning keeps their bases attached."""
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build_barbels(builder,config,profile):
 definitions=config.get('barbels',[])
 if not definitions:return
 material=builder.material('Barbel_Skin',tuple(config.get('barbel_color',[.23,.24,.21])),.43)
 body=next(o for o in builder.ROOT.children_recursive if o.type=='MESH' and o.name.startswith('Skin_AnatomicalProfile'));tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 for side in [-1,1]:
  for index,definition in enumerate(definitions):
   x=definition['root_x'];hi,lo,width=profile(x);height=definition['root_height'];root=Vector((x,side*width*math.sqrt(1-height*height)*.999,(hi+lo)/2+(hi-lo)/2*height));point,normal,_,_=tree.find_nearest(root);root=point-normal*.0006;target=Vector(definition['tip']);target.y*=side;delta=target-root;control=root+delta*.45+Vector((.025,side*.025,.025));vertices=[];uv=[];faces=[];rings=24;sections=10
   for i in range(rings+1):
    t=i/rings;p=root*(1-t)**2+control*2*t*(1-t)+target*t*t;tangent=((control-root)*(1-t)+(target-control)*t).normalized();a=tangent.cross(Vector((0,0,1))).normalized();b=tangent.cross(a).normalized();radius=max(.00022,definition.get('radius',.0026)*(1-t)**.85)
    for j in range(sections+1):
     angle=2*math.pi*j/sections;vertices.append(p+radius*(a*math.cos(angle)+b*math.sin(angle)));uv.append((j/sections,t))
   for i in range(rings):
    for j in range(sections):a=i*(sections+1)+j;faces.append((a,a+1,a+sections+2,a+sections+1))
   faces.extend([tuple(range(sections-1,-1,-1)),tuple(rings*(sections+1)+j for j in range(sections))]);obj=builder.mesh('Barbel_%s_%d'%(side,index),vertices,faces,material,uv);obj['anatomy']='Tapered mouth barbel with a skin-intersecting root ring'

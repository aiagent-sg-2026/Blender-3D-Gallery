"""Small folded peduncle blades for the original blue-tang study."""
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build_scalpels(builder,config,profile,flank):
 if not config.get('peduncle_scalpels'):return
 body=next(o for o in builder.ROOT.children_recursive if o.name.startswith('Skin_AnatomicalProfile'));tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons]);material=builder.material('Scalpel_FoldedIvory',(.60,.56,.29),.52)
 for side in [-1,1]:
  point=Vector((1.05,flank(1.05,0,side),0));hit,normal,_,_=tree.find_nearest(point);root=hit-normal*.0006
  vertices=[root+Vector((x,side*y,z)) for x,y,z in [(-.045,0,-.004),(.035,0,-.004),(.035,0,.004),(-.045,0,.004),(-.030,.004,0)]]
  builder.mesh('Peduncle_Scalpel_'+str(side),vertices,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],material,[(0,0),(1,0),(1,1),(0,1),(.2,.5)])

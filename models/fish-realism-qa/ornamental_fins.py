"""Anatomical fin variants for the selected original ornamental-fish studies."""
import math,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def outline_edge(points,u):
 i=next((i for i in range(len(points)-1) if u<=points[i+1][0]),len(points)-2);a,b=points[i],points[i+1];span=b[0]-a[0];t=max(0,min(1,(u-a[0])/span));values=[]
 for axis in [1,2]:
  before=points[max(0,i-1)];after=points[min(len(points)-1,i+2)];da=(b[axis]-before[axis])/(b[0]-before[0]);db=(after[axis]-a[axis])/(after[0]-a[0]);values.append((2*t**3-3*t*t+1)*a[axis]+(t**3-2*t*t+t)*span*da+(-2*t**3+3*t*t)*b[axis]+(t**3-t*t)*span*db)
 return (values[0],0,values[1])

def build_variants(builder,config,profile):
 if not (config.get('double_caudal') or config.get('gonopodium')):return
 body=next(o for o in builder.ROOT.children_recursive if o.name.startswith('Skin_AnatomicalProfile'));tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 def split(name,prefix,spread):
  original=next(o for o in builder.ROOT.children_recursive if o.name==name);uv=original.data.uv_layers.active;coordinates={loop.vertex_index:uv.data[loop.index].uv.copy() for loop in original.data.loops};roots={round(c.x,6):original.data.vertices[i].co.copy() for i,c in coordinates.items() if c.y<1e-7}
  for side in [-1,1]:
   obj=original.copy();obj.data=original.data.copy();obj.name=prefix+str(side);bpy.context.collection.objects.link(obj);obj.parent=builder.ROOT
   for vertex in obj.data.vertices:
    u,t=coordinates[vertex.index];root=roots[round(u,6)]+Vector((0,side*.018,0));hit,normal,_,_=tree.find_nearest(root);delta=hit-normal*.0007-root;vertex.co+=Vector((0,side*(.018+spread*t),0))+delta*(1-t)**2
   obj.data.update()
  bpy.data.objects.remove(original,do_unlink=True)
 if config.get('double_caudal'):
  split('Caudal_Membrane','Caudal_Twin_',config.get('tail_split_spread',.34));split('Anal_SoftMembrane','Anal_Paired_',.055)
 if config.get('gonopodium'):
  for obj in list(builder.ROOT.children_recursive):
   if obj.name.startswith('Anal_') and obj.type=='MESH':bpy.data.objects.remove(obj,do_unlink=True)
  x=config.get('gonopodium_root_x',-.10);candidate=Vector((x,0,profile(x)[1]));hit,normal,_,_=tree.find_nearest(candidate);root=hit-normal*.0018;vertices=[];uv=[];faces=[]
  for i in range(21):
   t=i/20;p=root+Vector((.24*t,0,-.055*math.sin(math.pi*t)-.03*t));radius=.0024*(1-t)**.8+.0002
   for j in range(9):angle=2*math.pi*j/8;vertices.append(p+Vector((0,radius*math.cos(angle),radius*math.sin(angle))));uv.append((j/8,t))
  for i in range(20):
   for j in range(8):k=i*9+j;faces.append((k,k+1,k+10,k+9))
  faces.extend([tuple(range(7,-1,-1)),tuple(180+j for j in range(8))]);builder.mesh('Anal_Gonopodium',vertices,faces,builder.material('Gonopodium_PaleFin',(.49,.48,.40),.52),uv,deform='anal')

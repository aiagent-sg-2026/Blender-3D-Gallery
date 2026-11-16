"""Closed cartilage-fin geometry; roots project into the actual shark skin."""
import math,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def build_shark_fins(builder,config,profile,flank,material):
 body=next(o for o in builder.ROOT.children_recursive if o.name.startswith('Skin_AnatomicalProfile'))
 tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(p.vertices) for p in body.data.polygons])
 def wing(name,root,edge,normal,role,kind):
  n,m=56,16;vertices=[];uv=[];faces=[];normal=Vector(normal)
  for side in [-1,1]:
   for i in range(n+1):
    u=i/n;r=Vector(root(u));e=Vector(edge(u));candidate=r+side*.012*normal;hit,no,_,_=tree.find_nearest(candidate);offset=hit-no*.0007-candidate
    for j in range(m+1):
     v=j/m;p=r*(1-v)+e*v+side*(.012*(1-v)**1.5+.00035)*normal+offset*(1-v)**2;vertices.append(p);uv.append((u,v))
  size=(n+1)*(m+1)
  for i in range(n):
   for j in range(m):
    k=i*(m+1)+j;faces.extend([(k,k+1,k+m+2,k+m+1),(k+size+m+1,k+size+m+2,k+size+1,k+size)])
  for i in range(n):
   for j in [0,m]:
    k=i*(m+1)+j;faces.append((k,k+m+1,k+m+1+size,k+size))
  for j in range(m):
   for i in [0,n]:
    k=i*(m+1)+j;faces.append((k,k+size,k+size+1,k+1))
  obj=builder.mesh(name,vertices,faces,material(kind,root,edge),uv,deform=role)
  span=obj.data.attributes.new('fin_span','FLOAT','POINT')
  for datum,coordinate in zip(span.data,uv):datum.value=coordinate[1]
  # Closed cap UVs need an independent footprint without changing root weights.
  for polygon in list(obj.data.polygons)[2*n*m:]:
   for index in polygon.loop_indices:
    p=obj.data.vertices[obj.data.loops[index].vertex_index].co;obj.data.uv_layers.active.data[index].uv=(.02+.06*p.x+.01*p.y,.15+.03*p.z+.04*p.y)
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
 def curve(points,u):return builder.interp(points,u)
 start,end=config['shark_dorsal_span']
 wing('Dorsal_Main',lambda u:(start+(end-start)*u,0,profile(start+(end-start)*u)[0]),lambda u:(start+(end-start)*u+.06*math.sin(math.pi*u),0,profile(start+(end-start)*u)[0]+max(.003,curve(config['shark_dorsal_height'],u))),(0,1,0),'dorsal','shark_dorsal')
 start,end=config.get('shark_second_dorsal_span',[.82,1.11])
 wing('Dorsal_Second',lambda u:(start+(end-start)*u,0,profile(start+(end-start)*u)[0]),lambda u:(start+(end-start)*u+.025*math.sin(math.pi*u),0,profile(start+(end-start)*u)[0]+.003+config.get('shark_second_dorsal_height',.095)*math.sin(math.pi*u)**1.2),(0,1,0),'dorsal','shark_second_dorsal')
 start,end=config.get('shark_anal_span',[.82,1.11])
 wing('Anal_Small',lambda u:(start+(end-start)*u,0,profile(start+(end-start)*u)[1]),lambda u:(start+(end-start)*u+.025*math.sin(math.pi*u),0,profile(start+(end-start)*u)[1]-.003-.075*math.sin(math.pi*u)**1.2),(0,1,0),'anal','shark_anal')
 for side in [-1,1]:
  x=config['gill_x']+.10;z=config.get('pectoral_root_z',-.08);w=abs(flank(x,z,side))
  def pectoral_edge(u):
   return (x+curve([[0,.008],[.57,.52],[1,.43]],u),side*(w+curve([[0,.003],[.57,config.get('shark_pectoral_span',.60)],[1,.02]],u)),z-curve([[0,.003],[.57,config.get('shark_pectoral_drop',.16)],[1,.065]],u))
  wing('Pectoral_Swept_'+str(side),lambda u:(x,flank(x,z+(u-.5)*.055,side),z+(u-.5)*.055),pectoral_edge,(0,0,1),'pectoral','shark_pectoral')
  px=config.get('shark_pelvic_x',.43);pz=profile(px)[1]*.72;pw=abs(flank(px,pz,side))
  wing('Pelvic_Small_'+str(side),lambda u:(px+.04*(u-.5),flank(px+.04*(u-.5),pz,side),pz),lambda u:(px+curve([[0,.02],[.45,.28],[1,.33]],u),side*(pw+curve([[0,.003],[.45,.18],[1,.025]],u)),pz-curve([[0,.025],[.45,config.get('shark_pelvic_drop',.10)],[1,.04]],u)),(0,0,1),'anal','shark_pelvic')
 points=config['shark_tail_outline']
 wing('Caudal_Heterocercal',lambda u:(1.18,0,(u-.5)*.14),lambda u:(curve([[a,b] for a,b,c in points],u),0,curve([[a,c] for a,b,c in points],u)),(0,1,0),'tail','shark_tail')
 if config.get('shark_kind')=='whale':
  vertices=[];uv=[];faces=[]
  for i in range(65):
   u=i/64;y=(u-.5)*.48;z=-.035+.025*(2*u-1)**2
   for side in [-1,1]:
    hit,_,_,_=tree.ray_cast(Vector((-2,y,z+side*.003)),Vector((1,0,0)),1)
    assert hit is not None,'The closed anterior lip must meet the real broad snout'
    vertices.append((hit.x-.001,y,z+side*.003));uv.append((u,(side+1)/2))
  for i in range(64):k=i*2;faces.append((k,k+1,k+3,k+2))
  builder.mesh('Mouth_ClosedAnterior',vertices,faces,builder.material('Mouth_ClosedLip',(.018,.023,.024),.57),uv)

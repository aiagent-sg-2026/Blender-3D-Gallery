"""Build an opaque, fleshy adipose fin without teleost membrane-ray textures."""
import math

def build_adipose(builder,config,profile):
 if not config.get('adipose_fin'):return
 pigment=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in config['back_color'])
 material=builder.material('Adipose_FleshySkin',pigment,.46)
 if not config.get('adipose_span'):
  # Preserve the previously reviewed pangasius geometry exactly.
  x0,x1,peak=.72,1.03,.84;h0=profile(x0)[0]-.002;h1=profile(x1)[0]-.002;hp=profile(peak)[0]+.10;hr=profile(.98)[0]+.025
  vertices=[(x0,-.008,h0),(x0,.008,h0),(x1,-.006,h1),(x1,.006,h1),(peak,-.002,hp),(peak,.002,hp),(.98,-.002,hr),(.98,.002,hr)];uv=[(0,0),(.1,0),(.9,0),(1,0),(.25,1),(.35,1),(.75,.25),(.85,.25)]
  return builder.mesh('Dorsal_AdiposeFin',vertices,[(0,4,5,1),(4,6,7,5),(6,2,3,7),(0,2,6,4),(1,5,7,3)],material,uv,deform='dorsal')
 start,end=config['adipose_span'];vertices=[];uv=[];faces=[];segments=40
 for index in range(segments+1):
  u=index/segments;x=start+(end-start)*u;h=max(.002,config.get('adipose_height',.15)*math.sin(math.pi*u)**.85);width=.001+.007*math.sin(math.pi*u)**.5;base=profile(x)[0]-.002
  vertices.extend([(x,-width,base),(x,width,base),(x,width*.25,base+h),(x,-width*.25,base+h)]);uv.extend([(u,0),(u,0),(u,1),(u,1)])
 for index in range(segments):
  a=4*index;b=a+4
  for j in range(4):faces.append((a+j,a+(j+1)%4,b+(j+1)%4,b+j))
 faces.extend([(3,2,1,0),tuple(segments*4+j for j in range(4))]);obj=builder.mesh('Dorsal_AdiposeFin',vertices,faces,material,uv,deform='dorsal')
 span=obj.data.attributes.new('fin_span','FLOAT','POINT')
 for vertex,datum in zip(obj.data.vertices,span.data):datum.value=0 if vertex.index%4<2 else 1
 for polygon in list(obj.data.polygons)[-2:]:
  for loop in polygon.loop_indices:
   p=obj.data.vertices[obj.data.loops[loop].vertex_index].co;obj.data.uv_layers.active.data[loop].uv=(.035+.08*p.y,.50+.12*p.z)
 return obj

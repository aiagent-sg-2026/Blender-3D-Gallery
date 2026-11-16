"""Original lionfish radial fins with body-embedded bases and distal free rays."""
import math
import bpy
from mathutils import Vector

def build_lion_fins(builder,fan,config,profile,flank,membrane,ray_material):
 if not config.get('lion_radial_fins'):return
 for obj in list(builder.ROOT.children_recursive):
  if obj.type=='MESH' and obj.name in ['Pectoral_-1','Pectoral_1']:
   bpy.data.objects.remove(obj,do_unlink=True)

 def ray(name,root,tip,radius,role,flag=False):
  root=Vector(root);tip=Vector(tip);delta=tip-root;a=delta.normalized().cross(Vector((0,1,0))).normalized();b=delta.normalized().cross(a);verts=[];uv=[];faces=[];rings=16;sections=6
  for i in range(rings+1):
   t=i/rings;p=root+delta*t+Vector((.045*math.sin(math.pi*t),0,.018*math.sin(math.pi*t)));r=max(.00025,radius*(1-t)**.75)
   for j in range(sections+1):
    angle=2*math.pi*j/sections;extra=radius*6.5*math.sin(math.pi*t)**1.4 if flag and math.cos(angle)>0 else 0
    verts.append(p+(r+extra)*a*math.cos(angle)+r*b*math.sin(angle));uv.append((j/sections,t))
  for i in range(rings):
   for j in range(sections):
    k=i*(sections+1)+j;faces.append((k,k+1,k+sections+2,k+sections+1))
  faces.extend([tuple(range(sections-1,-1,-1)),tuple(rings*(sections+1)+j for j in range(sections))])
  return builder.mesh(name,verts,faces,ray_material,uv,deform=role)

 for i in range(13):
  u=i/12;x=-1.05+1.40*u;z=profile(x)[0];height=(.52+.57*math.sin(math.pi*u)**.7)*(1+.085*math.sin(i*2.43))
  ray('Dorsal_FreeSpine_%02d'%i,(x,0,z-.009),(x-.14+.44*u+.08*math.sin(i*2.1),.025*math.sin(i*1.4),z+height),.0055,'dorsal',True)
 for side in [-1,1]:
  x=config['gill_x']+.10;root_z=config.get('pectoral_root_z',-.05)
  def root(u):
   z=root_z+(u-.5)*.11
   return (x,flank(x,z,side,-.008),z)
  def tip(u):
   angle=-1.22+2.44*u;length=.90+.18*math.sin(math.pi*u)
   return (x+.72+.20*math.sin(math.pi*u),side*(.30+length*.57*math.cos(angle)),root_z+length*.88*math.sin(angle))
  def web(u):
   r=Vector(root(u));d=Vector(tip(u))-r;notch=abs(math.sin(math.pi*u*13))**.55
   return r+d*(.93-.27*notch)
  fan('Pectoral_RadialWeb_'+str(side),root,web,membrane,n=130,m=20,flutter=.009,role='pectoral',phase=side)
  for i in range(14):ray('Pectoral_FreeRay_%s_%02d'%(side,i),root(i/13),tip(i/13),.0045,'pectoral')
 # Supraorbital cirri are skin appendages, not extra dorsal or mouth barbels.
 for side in [-1,1]:
  ex,ez,er=config['eye'];x=ex-.005;z=ez+er*.84
  ray('Supraorbital_Cirrus_'+str(side),(x,flank(x,z,side,-.004),z),(x-.08,side*.29,z+.20),.009,'body',True)

 for side in [-1,1]:
  for index,x in enumerate([-1.48,-1.28]):
   hi,lo,w=profile(x);z=lo+.04
   ray('Skin_ChinCirrus_%s_%d'%(side,index),(x,flank(x,z,side,-.006),z),(x-.035,side*(w+.045),z-.13-index*.025),.0055,'body',True)

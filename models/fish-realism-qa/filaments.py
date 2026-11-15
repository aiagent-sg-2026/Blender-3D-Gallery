"""Build four separate, tapered sensory pectoral rays on each threadfin flank."""
import math
from mathutils import Vector

def build_filaments(B, config, profile, flank):
 count=config.get('pectoral_filaments',0)
 if not count:return
 mat=B.material('SensoryPectoralFilaments',tuple(config.get('filament_color',[.49,.50,.42])),.50,.02)
 for side in [-1,1]:
  for ray in range(count):
   x=config['gill_x']+.11+.006*ray;z=config.get('pectoral_root_z',-.18)-.035-.012*ray;y=flank(x,z,side,.001)
   length=config.get('filament_lengths',[.32,.46,.60,.72])[ray];drop=.16+.035*ray
   points=[Vector((x+length*t,y+side*(.025*t+.022*math.sin(math.pi*t)),z-drop*t+.045*math.sin(math.pi*t))) for t in [i/32 for i in range(33)]]
   vertices=[];uv=[];faces=[];rings=8
   for i,p in enumerate(points):
    t=i/32;direction=(points[min(32,i+1)]-points[max(0,i-1)]).normalized();normal=direction.cross(Vector((0,0,1))).normalized();binormal=direction.cross(normal).normalized();radius=.0032*(1-.82*t)
    for j in range(rings):
     angle=2*math.pi*j/rings;vertices.append(tuple(p+radius*(math.cos(angle)*normal+math.sin(angle)*binormal)));uv.append((j/rings,t))
   for i in range(32):
    for j in range(rings):a=i*rings+j;b=i*rings+(j+1)%rings;faces.append((a,b,b+rings,a+rings))
   faces.extend([tuple(range(rings-1,-1,-1)),tuple(32*rings+j for j in range(rings))])
   obj=B.mesh('Pectoral_Filament_%s_%d'%(side,ray+1),vertices,faces,mat,uv,deform='pectoral');obj['anatomy']='One free sensory pectoral ray; root follows body, distal weights feather pectoral motion'

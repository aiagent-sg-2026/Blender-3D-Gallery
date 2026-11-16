"""Original shark relief and pigment; no teleost operculum or ray textures."""
import numpy as np

def paint_skin(color,height,x,z,u,v,config,smoothstep):
 flank=np.abs(np.cos(v*2*np.pi))**4
 slit=np.zeros_like(x);centers=config['shark_gill_x'];assert len(centers)==5
 for i,center in enumerate(centers):
  half=config.get('shark_gill_half_height',.12);curve=center+.025*((z+.02)/half)**2
  mark=np.exp(-((x-curve)/.0028)**2)*smoothstep(-half,-half+.035,z)*(1-smoothstep(half*.65,half,z))*flank
  slit=np.maximum(slit,mark)
 color*=1-slit[...,None]*.54;height-=slit*.0010
 if config.get('shark_kind')=='reef':
  lower=np.sin(v*2*np.pi);target=-1.45+.22*np.abs(np.cos(v*2*np.pi))**1.8
  mouth=np.exp(-((x-target)/.0035)**2)*(1-smoothstep(-.65,-.48,lower))
  color*=1-mouth[...,None]*.75;height-=mouth*.0008
  stripe=np.exp(-((z+.075+.022*np.sin(x*2.4))/.022)**2)*smoothstep(-.45,-.17,x)*(1-smoothstep(.72,.92,x))*flank
  color*=1-stripe[...,None]*.43
 if config.get('shark_kind')=='whale':
  pu=42*u+2*(1-np.exp(-u*8))+.12*np.sin(v*11+u*7)+.08*np.sin(v*37+u*3);pv=24*v+.20*np.sin(u*13+v*4)+.12*np.sin(u*31+v*7)
  row=np.floor(pv);column=np.floor(pu)
  a=np.mod(np.sin(row*127.1+column*311.7)*43758.5453,1);b=np.mod(np.sin(row*269.5+column*183.3)*18371.173,1)
  distance=np.sqrt((np.mod(pu,1)-.5-(a-.5)*.60)**2+(np.mod(pv,1)-.5-(b-.5)*.60)**2)
  dots=(1-smoothstep(.085+.07*a,.14+.09*a,distance))*(.65+.30*b)*smoothstep(.035,.075,a)
  lines=np.maximum(np.exp(-(np.sin(np.pi*pu)/.075)**2),np.exp(-(np.sin(np.pi*pv)/.065)**2))
  upper=smoothstep(-.65,-.25,np.sin(v*2*np.pi));pigment=np.maximum(dots*.88,lines*smoothstep(-.85,-.45,x)*.25)*upper
  color=color*(1-pigment[...,None])+np.array([.83,.86,.81])*pigment[...,None]
 return color,height

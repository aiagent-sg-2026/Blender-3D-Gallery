"""Original adult emperor-angelfish pigment; shared body and median-fin stripes."""
import numpy as np

def paint_stripes(color,x,z,smoothstep,face=False):
 stripes=np.zeros_like(x)
 for i,level in enumerate(np.arange(-.85,.96,.081)):
  curve=level+.024*np.sin((x+.9)*2.2)+.008*np.sin(x*10+i*.7)+.002*np.sin(x*61+i)
  stripes=np.maximum(stripes,1-smoothstep(.008,.013,np.abs(z-curve)))
 stripes*=smoothstep(-.94,-.73,x)*(1-smoothstep(1.18,1.29,x))
 color=color*(1-stripes[...,None]*.94)+np.array([.92,.76,.055])*stripes[...,None]*.94
 if face:
  frontal=1-smoothstep(-1.12,-.99,x);color=color*(1-frontal[...,None])+np.array([.19,.48,.46])*frontal[...,None]
  for cx,cz,rx,rz in [(-1.24,.24,.13,.31),(-.88,.05,.17,.43)]:
   d=np.sqrt(((x-cx-.18*(z-cz))/rx)**2+((z-cz)/rz)**2)
   rim=(1-smoothstep(.98,1.10,d))*smoothstep(.83,.95,d);black=1-smoothstep(.83,.94,d)
   color=color*(1-rim[...,None]*.9)+np.array([.10,.31,.82])*rim[...,None]*.9
   color=color*(1-black[...,None]*.97)+np.array([.012,.018,.042])*black[...,None]*.97
 return color

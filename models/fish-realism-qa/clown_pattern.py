"""Share the same curved clownfish bands between skin and dorsal textures."""
import numpy as np

def paint_bands(color,x,z,smoothstep):
 result=color.copy()
 for center,width,curve in [(-1.06,.115,.045),(-.06,.185,.095),(1.08,.075,.015)]:
  rng=np.random.default_rng(1783+int((center+2)*100));irregularity=np.interp(z,np.linspace(-1.2,1.2,113),rng.normal(0,.0012,113));local_width=width+.006*np.sin(z*11+center);distance=np.abs(x-center-curve*np.sin(z*3.2)-irregularity);outer=1-smoothstep(local_width+.012,local_width+.033,distance);inner=1-smoothstep(local_width-.006,local_width+.006,distance)
  grain=.007*np.sin(x*587+z*419)*np.sin(x*173-z*263)+.004*np.sin(x*127+z*637);white=np.array([.86,.87,.79])*(1-.045*smoothstep(-.1,.6,z)[...,None])+grain[...,None]
  result=result*(1-outer[...,None])+np.array([.022,.025,.019])*outer[...,None];result=result*(1-inner[...,None])+white*inner[...,None]
 return result

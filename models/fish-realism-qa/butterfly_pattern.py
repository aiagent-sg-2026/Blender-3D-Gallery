"""Original curved eight-band pigment shared by body and median fin maps."""
import numpy as np

def paint_bands(color,x,z,smoothstep):
 axis=x-.43*z-.035*z*z
 mask=np.zeros_like(axis)
 for i,center in enumerate([-1.59,-1.36,-.98,-.60,-.22,.16,.54,.92]):
  curve=center+.005*np.sin(z*21+i*1.7)+.002*np.sin(z*47+i)
  distance=np.abs(axis-curve);width=.030 if i==0 else .036
  mask=np.maximum(mask,1-smoothstep(width,width+.009,distance))
 spot=1-smoothstep(.80,1.05,np.sqrt(((x-1.16)/.085)**2+(z/.10)**2));mask=np.maximum(mask,spot)
 return color*(1-mask[...,None]*.96)+np.array([.014,.018,.015])*mask[...,None]*.96

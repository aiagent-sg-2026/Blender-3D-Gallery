"""Four original anatomical-coordinate bars shared by tiger-barb skin and fins."""
import numpy as np

def paint_bars(color,x,z,smoothstep):
 mask=np.zeros_like(x)
 for i,(center,width) in enumerate([(-1.35,.055),(-.60,.115),(.43,.105),(1.10,.045)]):
  curve=center+([.16,.02,-.08,0][i])*z+.004*np.sin(z*23+i)
  mask=np.maximum(mask,1-smoothstep(width,width+.014,np.abs(x-curve)))
 return color*(1-mask[...,None]*.97)+np.array([.014,.019,.016])*mask[...,None]*.97

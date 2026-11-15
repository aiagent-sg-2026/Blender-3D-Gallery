"""Use paired positive targets so reimporters cannot clamp signed swim weights."""
import bpy

def make_portable(o):
 keys=o.data.shape_keys
 if not keys or any(k.name.endswith('_Negative') for k in keys.key_blocks):return
 original=list(keys.key_blocks)[1:];samples={}
 for f in range(1,98,2):
  bpy.context.scene.frame_set(f);samples[f]=[float(k.value) for k in original]
 basis=keys.key_blocks[0]
 pairs=[]
 for key in original:
  opposite=o.shape_key_add(name=key.name+'_Negative');opposite.slider_min=0;opposite.slider_max=1
  for i,p in enumerate(key.data):opposite.data[i].co=2*basis.data[i].co-p.co
  key.slider_min=0;key.slider_max=1;pairs.append((key,opposite))
 for f,values in samples.items():
  for (positive,negative),value in zip(pairs,values):
   positive.value=max(0,value);negative.value=max(0,-value);positive.keyframe_insert('value',frame=f);negative.keyframe_insert('value',frame=f)
 # Linear samples retain the crossing velocity instead of easing each half-wave.
 action=keys.animation_data.action
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for curve in bag.fcurves:
     for point in curve.keyframe_points:point.interpolation='LINEAR'


def restore_independent_wave_bases(o):
 """Each quadrature starts from Basis, never the current mixed pose."""
 import math
 keys=o.data.shape_keys;basis=keys.key_blocks[0]
 for key in list(keys.key_blocks)[1:]:
  if not key.name.startswith(('Left_','Right_')):continue
  side=-1 if key.name.startswith('Left_') else 1;quadrature=0 if 'Sine' in key.name else 1;sign=-1 if key.name.endswith('_Negative') else 1
  for i,point in enumerate(basis.data):
   x,y,z=point.co;t=max(0,min(1,(abs(y)-.25)/.95));span=t*t*(3-2*t);envelope=math.sin(math.pi*max(.001,min(.999,(x+1.21)/2.24)))**.60
   amplitude=.245*span**1.5*envelope*(1 if side<0 else .96)
   if y*side<=0:amplitude=0
   phase=-2*math.pi*1.05*(x+1.21)/2.24+(0 if side<0 else .09);wave=math.sin(phase) if quadrature==0 else math.cos(phase)
   key.data[i].co=point.co.copy();key.data[i].co.z+=sign*amplitude*wave

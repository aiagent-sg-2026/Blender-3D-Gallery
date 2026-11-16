"""Retiming keeps an authored cyclic action's values and normalized phase."""

def retime_swim(rig,seconds):
 action=rig.animation_data.action;start,end=map(float,action.frame_range);frames=int(round(seconds*24/2))*2;factor=frames/(end-start)
 if abs(factor-1)>1e-9:
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for curve in bag.fcurves:
      for point in curve.keyframe_points:
       point.co.x=1+(point.co.x-start)*factor;point.handle_left.x=1+(point.handle_left.x-start)*factor;point.handle_right.x=1+(point.handle_right.x-start)*factor
      curve.update()
 return frames+1

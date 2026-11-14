import math,json
from pathlib import Path
R=.05715/2;rod=.009;height=.0089;required=math.sqrt((R+rod)**2-(R-height)**2)
hull=[(0,0),(4*R*math.sqrt(3),-4*R),(4*R*math.sqrt(3),4*R)]
def analyze(vertices):
 planes=[];breaks={0,2*math.pi}
 for a,b in zip(vertices,vertices[1:]+vertices[:1]):
  dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
  planes.append((nx,ny,nx*a[0]+ny*a[1],length))
  for i in range(3):
   for j in range(i):
    x,y=hull[i][0]-hull[j][0],hull[i][1]-hull[j][1];A=nx*x+ny*y;B=-nx*y+ny*x
    angle=math.atan2(-A,B)
    for shift in range(-2,4):
     t=angle+shift*math.pi
     if 0<t<2*math.pi:breaks.add(t)
 breaks=sorted(breaks);candidates=list(breaks)
 for low,high in zip(breaks,breaks[1:]):
  mid=(low+high)/2;co,si=math.cos(mid),math.sin(mid);A=B=0
  for nx,ny,c,length in planes:
   x,y=max(hull,key=lambda p:nx*(p[0]*co-p[1]*si)+ny*(p[0]*si+p[1]*co))
   A+=length*(nx*x+ny*y);B+=length*(-nx*y+ny*x)
  t=(math.atan2(B,A)+math.pi)%(2*math.pi)
  if low<t<high:candidates.append(t)
 def support(t):
  co,si=math.cos(t),math.sin(t)
  return sum(length*max(nx*(x*co-y*si)+ny*(x*si+y*co) for x,y in hull) for nx,ny,c,length in planes)
 angle=min(candidates,key=support);perimeter=sum(p[3] for p in planes)
 maximum=(sum(c*l for nx,ny,c,l in planes)-support(angle))/perimeter
 return dict(centerline_vertices=vertices,maximum_uniform_horizontal_ball_center_clearance_m=maximum,required_horizontal_clearance_m=required,full_size_pack_possible_under_circular_bar_model=maximum>=required,best_rotation_deg=math.degrees(angle),clearance_surplus_m=maximum-required,candidate_extrema=len(candidates))
side=.350
report=dict(ball_diameter_m=2*R,bar_radius_m=rod,bar_axis_above_cloth_m=height,method='Exact piecewise trigonometric support-function extrema over all rotations of the five-row touching-ball hull. Outward edge normals weighted by edge length cancel translation; three inward-offset halfplanes are feasible iff their weighted constants sum nonnegative. Circular bar cross-section provides a conservative fit criterion for the inscribed12-sided mesh. Actual GLB triangle/sphere checks independently reproduce baseline overlap and verify final clearance.',before=analyze([(.48,.27),(.78,.435),(.78,.105)]),after=analyze([(.68-side*math.sqrt(3)/3,.27),(.68+side*math.sqrt(3)/6,.27+side/2),(.68+side*math.sqrt(3)/6,.27-side/2)]))
inner=rod*math.cos(math.pi/12)
minimum=math.sqrt((R+inner)**2-(R-height)**2)
report.update(inscribed_cylinder_radius_m=inner,required_clearance_even_for_inscribed_cylinder_m=minimum,baseline_inscribed_cylinder_clearance_deficit_m=minimum-report['before']['maximum_uniform_horizontal_ball_center_clearance_m'],scope_note='The circular-bar calculation is a geometric model. Final acceptance also requires direct sphere-to-actual-exported-triangle checks; native witness spheres are diagnostic only, not product geometry.')
Path('docs/model-qa/MODEL-0004/capacity-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print('Capacity model before:',report['before']['full_size_pack_possible_under_circular_bar_model'],'after:',report['after']['full_size_pack_possible_under_circular_bar_model'])

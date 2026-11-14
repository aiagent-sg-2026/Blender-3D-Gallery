"""Check simple bounding-plane relationships; not a mesh-intersection test."""
import json, math
from pathlib import Path
p=Path(__file__).resolve().parent; data=json.loads((p/'measurements.json').read_text()); rec={o['name']:o for o in data['objects']}
def box(name): return rec[name]['bounds_min_blender_m'],rec[name]['bounds_max_blender_m']
def gap(a,b,axis): return box(b)[0][axis]-box(a)[1][axis]
checks=[]
def check(name,value,expected,tolerance=.002):
 checks.append({'name':name,'measured_m':value,'expected_m':expected,'tolerance_m':tolerance,'pass':abs(value-expected)<=tolerance})
xs=[-1.8,-.6,.6,1.8]; ys=[-2.4,-1.2,0,1.2]
for y in ys:
 for x1,x2 in zip(xs,xs[1:]): check(f'floor X seam {x1} {x2} y={y}',gap(f'Floor_{x1}_{y}',f'Floor_{x2}_{y}',0),0)
for x in xs:
 for y1,y2 in zip(ys,ys[1:]): check(f'floor Y seam {y1} {y2} x={x}',gap(f'Floor_{x}_{y1}',f'Floor_{x}_{y2}',1),0)
check('left partition to door',gap('Partition_Left','Door',0),0)
check('door to right partition',gap('Door','Partition_Right',0),0)
check('door head to ceiling underside',3-box('Door')[1][2],.6)
check('column top to ceiling underside',3-box('Column')[1][2],0)
check('column edge to ceiling opening left',box('Column')[0][0]-(-2.4),.3)
check('column edge to ceiling opening right',(-1.2)-box('Column')[1][0],.3)
check('floor surface to door',box('Door')[0][2]-box('Floor_-0.6_-1.2')[1][2],0)
for base,fascia in [('Door','Fascia_Door'),('Partition_Left','Fascia_Left'),('Partition_Right','Fascia_Right')]:
 check(base+' top to fascia base',gap(base,fascia,2),0)
 check(fascia+' top to ceiling grid',3-box(fascia)[1][2],0)
check('fascia left seam',gap('Fascia_Left','Fascia_Door',0),0)
check('fascia right seam',gap('Fascia_Door','Fascia_Right',0),0)
check('collar underside to ceiling grid',box('Ceiling_Collar')[0][2]-3,0)
check('collar outer width',box('Ceiling_Collar')[1][0]-box('Ceiling_Collar')[0][0],1.2)
result={'method':'World-axis bounding boxes from Blender imported GLBs; contact is not an intersection or visual seam test. Ceiling opening derived from omitted 1.2 m module grid.','checks':checks}
(p/'join-results.json').write_text(json.dumps(result,indent=2)+'\n')
for c in checks: print(('PASS' if c['pass'] else 'FAIL'),c['name'],round(c['measured_m'],6))
assert all(c['pass'] for c in checks)

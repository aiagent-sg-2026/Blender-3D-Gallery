"""Build the dimensioned Foundation whitebox contract; no existing assets are edited."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
parts=[]
def box(name,center,size,kind,collision=True):
 parts.append(dict(id=name,center=center,size=size,kind=kind,collision=collision))
def wall(name,x1,z1,x2,z2):
 assert x1==x2 or z1==z2
 box(name,[(x1+x2)/2,1.5,(z1+z2)/2],[max(abs(x2-x1),.12),3,max(abs(z2-z1),.12)],'wall')
regions=[dict(id='entrance',name='Entrance apron',bounds=[-2.4,2.4,16.8,19.2]),dict(id='atrium',name='Atrium',bounds=[-4.8,4.8,9.6,16.8]),dict(id='corridor',name='Main corridor',bounds=[-2.4,2.4,-12,9.6]),dict(id='newmoon',name='New Moon',bounds=[-9.6,-2.4,-4.8,4.8]),dict(id='sample',name='Sample Store',bounds=[2.4,9.6,-4.8,4.8])]
for r in regions:
 x1,x2,z1,z2=r['bounds'];box(r['id']+'_floor',[(x1+x2)/2,-.1,(z1+z2)/2],[x2-x1,.2,z2-z1],'floor_'+r['id'])
# A low arrival boundary stops the capsule without squeezing the follow camera.
box('entry_boundary',[0,.3,19.2],[4.8,.6,.12],'fixture')
for s in (-1,1):
 side='west' if s<0 else 'east'
 wall(side+'_apron',s*2.4,16.8,s*2.4,19.2)
 wall(side+'_arrival',s*1.2,16.8,s*4.8,16.8)
 wall(side+'_atrium',s*4.8,9.6,s*4.8,16.8)
 wall(side+'_atrium_shoulder',s*2.4,9.6,s*4.8,9.6)
 wall(side+'_corridor_south',s*2.4,4.8,s*2.4,9.6)
 wall(side+'_corridor_north',s*2.4,-12,s*2.4,-4.8)
 wall(side+'_front_north',s*2.4,-4.8,s*2.4,-1.05)
 wall(side+'_front_south',s*2.4,1.05,s*2.4,4.8)
 wall(side+'_store_back',s*9.6,-4.8,s*9.6,4.8)
 wall(side+'_store_north',s*2.4,-4.8,s*9.6,-4.8)
 wall(side+'_store_south',s*2.4,4.8,s*9.6,4.8)
 box(side+'_door_header',[s*2.4,2.7,0],[.12,.6,2.1],'header')
 for i,z in enumerate((-2.4,0,2.4)):
  box(side+'_shelf_'+str(i),[s*8.9,1,z],[.5,2,1.5],'shelf')
wall('corridor_end',-2.4,-12,2.4,-12)
box('entry_header',[0,2.7,16.8],[2.4,.6,.12],'header')
for s in (-1,1):box(('west' if s<0 else 'east')+'_bench',[s*3.7,.35,11.8],[.6,.7,2.4],'fixture')
box('directory_proxy',[-3.1,1,14.4],[.8,2,.5],'fixture')
box('planter_proxy',[3.6,.65,14.3],[.8,1.3,.8],'fixture')
box('bin_proxy',[3.7,.5,15.8],[.6,1,.6],'fixture')
layout=dict(version='1.0',units='metres',axes='Three.js/glTF +Y up; plan north is -Z',grid_m=1.2,wall_height_m=3,door_clear_width_m=2.1,door_clear_height_m=2.4,spawn=[0,.89,18],regions=regions,parts=parts,labels=[dict(text='ENTRANCE',position=[0,2.65,16.7],rotation=0),dict(text='ATRIUM',position=[0,.01,13],rotation=0),dict(text='NEW MOON',position=[-2.32,2.1,0],rotation=1.5707963267948966),dict(text='SAMPLE STORE',position=[2.32,2.1,0],rotation=-1.5707963267948966)],route_waypoints=[[0,18],[0,13],[0,6],[0,0],[-6,0],[0,0],[6,0],[0,0],[0,6],[0,13],[0,18]])
(HERE/'whitebox/layout.json').write_text(json.dumps(layout,indent=2)+'\n')
print('Created',len(parts),'parts;',len(regions),'regions')

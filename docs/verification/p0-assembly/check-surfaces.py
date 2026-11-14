"""Independent surface coverage and component-box overlap probe of saved GLB assembly."""
from pathlib import Path
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fit-study.blend'))
bpy.context.view_layer.update()
def children(name):return [o for o in bpy.data.objects[name].children_recursive if o.type=='MESH']
def tree(objects):
    verts=[];faces=[]
    for o in objects:
        base=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(base+i for i in f.vertices) for f in o.data.polygons])
    return BVHTree.FromPolygons(verts,faces,all_triangles=False)
def hit(bvh,origin,direction,distance):return bvh.ray_cast(Vector(origin),Vector(direction),distance)[0]
fascia=tree(children('Fascia_Door')+children('Fascia_Left')+children('Fascia_Right'))
collar=tree(children('Ceiling_Collar'))
misses=[];fascia_samples=0;collar_samples=0
for i in range(225):
    x=-2.24+i*.02
    for j in range(29):
        z=2.41+j*.02;fascia_samples+=1
        if hit(fascia,(x,-1.7,z),(0,1,0),.4) is None:misses.append(['fascia',x,z])
for i in range(60):
    x=-.59+i*.02
    for j in range(60):
        y=-.59+j*.02
        if abs(x)<.3 and abs(y)<.3:continue
        collar_samples+=1
        if hit(collar,(x-1.8,y,2.95),(0,0,1),.1) is None:misses.append(['collar',x,y])
# The central aperture must remain clear even though the original column fills it.
hole_samples=0;hole_blocked=[]
for x in [-.25,0,.25]:
    for y in [-.25,0,.25]:
        hole_samples+=1
        if hit(collar,(x-1.8,y,2.95),(0,0,1),.1) is not None:hole_blocked.append([x,y])
# New models consist of boxes. Positive intersections of their component boxes
# with surrounding imported components fail; zero-volume contact is permitted.
new=children('Fascia_Door')+children('Fascia_Left')+children('Fascia_Right')+children('Ceiling_Collar')
all_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
def bounds(o):
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]
bb={o:bounds(o) for o in all_meshes};overlaps=[];seen=set()
for a in new:
    for b in all_meshes:
        pair=tuple(sorted([a.name,b.name]))
        if a==b or pair in seen:continue
        seen.add(pair);al,ah=bb[a];bl,bh=bb[b];ext=[min(ah[i],bh[i])-max(al[i],bl[i]) for i in range(3)]
        if min(ext)>.00001:overlaps.append({'a':a.name,'b':b.name,'overlap_extents_m':ext})
ceilings=tree([o for n in bpy.data.objects if n.name.startswith('Ceiling_') and n.name!='Ceiling_Collar' for o in children(n.name)])
# Sample actual ceiling underside; trim meets grid at 3.0, panel recess gives 8 mm reveal.
gaps=[];edge_probes=[]
for x in [-2.1,-1.8,-1.5,-1.2,-.9,-.6,-.3,0,.3,.6,.9,1.2,1.5,1.8,2.1]:
    h=hit(ceilings,(x,-1.5,2.9999),(0,0,1),.05)
    if h is None:
        # An exact shared triangle/rail boundary can lie outside both sides by float rounding.
        probes=[hit(ceilings,(x+dx,-1.5,2.9999),(0,0,1),.05) for dx in [-.00001,.00001]]
        values=[None if q is None else float(q.z-3) for q in probes]
        edge_probes.append({'x_m':x,'original_hit':False,'offsets_m':[-.00001,.00001],'gaps_m':values})
        if all(v is not None and -.0001<=v<=.0081 for v in values):h=probes[0]
    gaps.append(None if h is None else float(h.z-3))
result={'fascia_samples':fascia_samples,'collar_samples':collar_samples,'surface_misses':misses,'hole_samples':hole_samples,'hole_blocked':hole_blocked,'new_component_box_overlaps':overlaps,'ceiling_reveal_samples_m':gaps,'exact_edge_rechecks':edge_probes,'limits':'Fixed-step rays and component boxes are bounded evidence, not a proof of every triangle or construction tolerances.'}
result['pass']=not misses and not hole_blocked and not overlaps and all(g is not None and -.0001<=g<=.0081 for g in gaps)
(P/'surface-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('SURFACES',result['pass'],fascia_samples,collar_samples,'misses',len(misses),'overlaps',len(overlaps),'reveal',gaps)
assert result['pass'],result

"""Two neutral stores and corridor; sample-only whitebox shell, existing asset instances."""
from pathlib import Path
import bpy, math, json, hashlib
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent; ROOT=P.parents[2]
SOURCES={
'floor':'models/mall-floor-tile/exports/mall-floor-tile-module.glb',
'ceiling':'models/mall-ceiling-panel/exports/mall-ceiling-panel-module.glb',
'column':'models/mall-structural-column/exports/mall-structural-column.glb',
'partition':'models/mall-glass-partition/exports/mall-glass-partition.glb',
'door':'models/mall-shopfront-door/exports/mall-shopfront-door.glb',
'fascia210':'models/mall-fit-finishes/exports/mall-shopfront-fascia-210.glb',
'fascia120':'models/mall-fit-finishes/exports/mall-shopfront-fascia-120.glb',
'collar':'models/mall-fit-finishes/exports/mall-column-ceiling-collar.glb',
'shelf':'models/mall-essentials/exports/mall-display-shelf.glb',
'bench':'models/gjh-mall-furniture/exports/gjh-lounge-bench.glb'}
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
cache={};records=[]
def add(kind,name,position,rotation=0):
 if kind not in cache:
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/SOURCES[kind]));objects=list(set(bpy.data.objects)-before);cache[kind]=objects
 else:
  originals=cache[kind];copies={o:o.copy() for o in originals}
  for o,c in copies.items():scene.collection.objects.link(c);c.parent=copies.get(o.parent)
  objects=list(copies.values())
 wrapper=bpy.data.objects.new(name,None);scene.collection.objects.link(wrapper);wrapper.location=position;wrapper.rotation_euler.z=rotation
 for o in objects:
  if o.parent not in objects:o.parent=wrapper
 bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(v) for o in objects if o.type=='MESH' for v in o.bound_box]
 records.append({'name':name,'kind':kind,'position_blender_m':position,'rotation_z':rotation,'bounds_min_blender_m':[min(v[i] for v in points) for i in range(3)],'bounds_max_blender_m':[max(v[i] for v in points) for i in range(3)]})
 return wrapper
# Central route is 3.6 x 7.2 m. Each shop has a 3.6 x 4.8 m floor.
centres=[(x,y) for x in [-1.2,0,1.2] for y in [-3,-1.8,-.6,.6,1.8,3]]
centres += [(x,y) for x in [-4.8,-3.6,-2.4,2.4,3.6,4.8] for y in [-1.8,-.6,.6,1.8]]
for n,(x,y) in enumerate(centres):
 add('floor',f'Floor_{n}',(x,y,-.03))
 add('ceiling',f'Ceiling_{n}',(x,y,3))
# The column occupies a reserved ceiling cell in the corridor arrival area.
# Replace that intact cassette with its collar; do not stack both geometries.
column_index=centres.index((-1.2,-3))
old=bpy.data.objects[f'Ceiling_{column_index}']
for o in list(old.children_recursive)+[old]:bpy.data.objects.remove(o,do_unlink=True)
records=[r for r in records if r['name']!=f'Ceiling_{column_index}']
add('column','Column',(-1.2,-3,0));add('collar','Ceiling_Collar',(-1.2,-3,3))
for label,x,rot in [('A',-1.8,math.pi/2),('B',1.8,-math.pi/2)]:
 add('door',f'Door_{label}',(x,0,0),rot)
 add('fascia210',f'Fascia_Door_{label}',(x,0,2.4),rot)
 for side,offset in [('Left',-1.65),('Right',1.65)]:
  v=Matrix.Rotation(rot,4,'Z')@Vector((offset,0,0))+Vector((x,0,0))
  add('partition',f'Partition_{label}_{side}',tuple(v),rot)
  add('fascia120',f'Fascia_{label}_{side}',(v.x,v.y,2.4),rot)
 add('shelf',f'Shelf_{label}',(-4.95 if label=='A' else 4.95,0,0),-rot)
 # Built-in Bfont neutral text converted to geometry; no client brand artwork.
 bpy.ops.object.text_add();text=bpy.context.object;text.name='Sign_'+label;text.data.body='SAMPLE '+label;text.data.align_x='CENTER';text.data.size=.16;text.data.extrude=.0003
 text.location=Matrix.Rotation(rot,4,'Z')@Vector((0,-.031,2.64))+Vector((x,0,0));text.rotation_euler=(math.pi/2,0,rot)
 bpy.ops.object.convert(target='MESH')
# Sample-only walls and narrow facade returns close the neutral room shell.
mat=bpy.data.materials.new('Whitebox warm ivory');mat.diffuse_color=(.58,.56,.48,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.58,.56,.48,1)
def wall(name,location,dimensions):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
for label,sign in [('A',-1),('B',1)]:
 wall('Shell_Back_'+label,(sign*5.37,0,1.5),(.06,4.8,3))
 for side,y in [('N',2.37),('S',-2.37)]:
  wall('Shell_Side_'+label+side,(sign*3.6,y,1.5),(3.6,.06,3))
 for y in [-2.31,2.31]:wall('Shell_Return_'+label+str(y),(sign*1.83,y,1.5),(.06,.12,3))
# Seating is beyond the two store approaches; not in a door sweep.
add('bench','Bench',(0,3,0))
scene.world=bpy.data.worlds.new('Study world');scene.world.color=(.3,.3,.3)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(P/'corridor.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
for name,loc,energy in [('Key',(2,-8,10),2500),('Fill',(-6,2,8),2000),('Interior',(0,0,2.8),900)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.size=8;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(12,-14,10));camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=16
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
# Cutaway is a viewing aid; complete ceiling remains in the GLB and saved scene.
ceilings=[o for o in scene.objects if o.name.startswith('Ceiling_') and o.parent is None]
for root in ceilings:
 for o in root.children_recursive:o.hide_render=True
camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'blender-cutaway.png');bpy.ops.render.render(write_still=True)
for root in ceilings:
 for o in root.children_recursive:o.hide_render=False
camera.location=(0,-6,1.7);camera.data.type='PERSP';camera.data.lens=22;camera.rotation_euler=(Vector((0,0,1.6))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'blender-corridor.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'corridor.blend'),compress=True)
(P/'layout.json').write_text(json.dumps({'units':'metres','corridorWidth':3.6,'corridorLength':7.2,'shopFloorDimensions':[3.6,4.8],'sources':{k:{'path':v,'sha256':hashlib.sha256((ROOT/v).read_bytes()).hexdigest()} for k,v in SOURCES.items()},'objects':records,'floorCells':centres,'limits':'Two neutral stores, static dressing, sample-only whitebox shell. Not Foundation v1 integration.'},indent=2)+'\n')
print('CORRIDOR_DONE',len(records))

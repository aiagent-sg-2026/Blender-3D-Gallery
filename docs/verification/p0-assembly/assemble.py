"""Build a non-production fit study from checked-in GLBs. Never modifies inputs."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
sources={
 'floor':'models/mall-floor-tile/exports/mall-floor-tile-module.glb',
 'column':'models/mall-structural-column/exports/mall-structural-column.glb',
 'ceiling':'models/mall-ceiling-panel/exports/mall-ceiling-panel-module.glb',
 'partition':'models/mall-glass-partition/exports/mall-glass-partition.glb',
 'door':'models/mall-shopfront-door/exports/mall-shopfront-door.glb',
 'fascia210':'models/mall-fit-finishes/exports/mall-shopfront-fascia-210.glb',
 'fascia120':'models/mall-fit-finishes/exports/mall-shopfront-fascia-120.glb',
 'collar':'models/mall-fit-finishes/exports/mall-column-ceiling-collar.glb'}
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
records=[]; wrappers=[]
def add(kind,name,loc):
 before=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(root/sources[kind]))
 new=set(bpy.data.objects)-before
 group=bpy.data.objects.new(name,None); scene.collection.objects.link(group); group.location=loc
 for o in new:
  if o.parent is None: o.parent=group
 wrappers.append(group); bpy.context.view_layer.update()
 meshes=[o for o in new if o.type=='MESH']; points=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
 if not points: raise RuntimeError(f'No meshes: {name}')
 lo=[min(p[i] for p in points) for i in range(3)]; hi=[max(p[i] for p in points) for i in range(3)]
 records.append({'kind':kind,'name':name,'location_blender_m':loc,'bounds_min_blender_m':lo,'bounds_max_blender_m':hi,'meshes':len(meshes)})
for x in [-1.8,-0.6,0.6,1.8]:
 for y in [-2.4,-1.2,0,1.2]:
  add('floor',f'Floor_{x}_{y}',(x,y,-0.03))
  if y!=-2.4 and not (x==-1.8 and y==0): add('ceiling',f'Ceiling_{x}_{y}',(x,y,3.0))
add('column','Column',(-1.8,0,0))
add('partition','Partition_Left',(-1.65,-1.5,0))
add('door','Door',(0,-1.5,0))
add('partition','Partition_Right',(1.65,-1.5,0))
add('fascia210','Fascia_Door',(0,-1.5,2.4))
add('fascia120','Fascia_Left',(-1.65,-1.5,2.4))
add('fascia120','Fascia_Right',(1.65,-1.5,2.4))
add('collar','Ceiling_Collar',(-1.8,0,3.0))
bpy.context.view_layer.update()
# Record the actual imported world bounds, not a model-manifest claim.
data={'axes':'Blender X/Y horizontal, Z up; metres','sources':{k:{'path':v,'sha256':hashlib.sha256((root/v).read_bytes()).hexdigest()} for k,v in sources.items()},'objects':records,'layout':'4 x 4 floor bays including door apron; 11 ceiling bays plus column collar; glazed wall and three fitted fascia modules','limits':'closed door only; no collision, material certification or physical device test'}
(out/'measurements.json').write_text(json.dumps(data,indent=2)+'\n')
# Export the actual assembled objects only. Save an editable scene with the same placements.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(out/'fit-study.glb'),export_format='GLB',use_selection=True,export_apply=False)
# Render inspection cameras and lighting; these are excluded from GLB.
world=bpy.data.worlds.new('Studio World') if not bpy.data.worlds else bpy.data.worlds[0]; scene.world=world; world.color=(0.45,0.45,0.45)
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA'); obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc; data.energy=power; data.shape='DISK'; data.size=size; obj.rotation_euler=(Vector((0,0,1.3))-obj.location).to_track_quat('-Z','Y').to_euler()
area('Key',(2,-5,7),1800,7); area('Fill',(-4,0,6),1200,6)
cdata=bpy.data.cameras.new('Inspection Camera'); cam=bpy.data.objects.new('Inspection Camera',cdata); scene.collection.objects.link(cam); scene.camera=cam; cdata.type='ORTHO'; cdata.ortho_scale=7.8
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def render(name,position,target):
 cam.location=position; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); scene.render.filepath=str(out/name); bpy.ops.render.render(write_still=True)
render('blender-front.png',(6,-9,5.1),(0,0,1.4))
render('blender-ceiling.png',(-5,-6,7.6),(-0.5,0,1.7))
render('blender-underside.png',(5,-8,1.3),(-0.2,-0.3,2.25))
cdata.ortho_scale=1.9
render('blender-collar.png',(-3.3,-2.4,1.0),(-1.8,0,3.0))
cdata.ortho_scale=3.0
render('blender-fascia.png',(2,-5,2.8),(0,-1.5,2.68))
cdata.ortho_scale=7.8
cam.location=(6,-9,5.1);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fit-study.blend'))
print('FIT_STUDY_DONE',len(records))

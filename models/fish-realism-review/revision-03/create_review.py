"""Isolated source-preserving fish review; never edits gallery assets."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
SOURCES=HERE.parent/'external-candidates'

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def bounds(objects):
 dg=bpy.context.evaluated_depsgraph_get(); pts=[]
 for o in objects:
  ev=o.evaluated_get(dg); pts.extend(ev.matrix_world@v.co for v in ev.data.vertices)
 return Vector([min(p[d] for p in pts) for d in range(3)]),Vector([max(p[d] for p in pts) for d in range(3)])

def studio(folder,ray=False):
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=20;s.cycles.use_denoising=True
 s.render.threads_mode='FIXED';s.render.threads=6;s.render.resolution_x=1120;s.render.resolution_y=740;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('NeutralStudio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.20,.24,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 for name,pos,power,size in [('Key',(-2,-4,5),650,5),('Fill',(1,3,2),350,4),('Rim',(3,1,4),500,3)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;aim(o,(0,0,0))
 d=bpy.data.cameras.new('ReviewCamera');o=bpy.data.objects.new('ReviewCamera',d);s.collection.objects.link(o);s.camera=o
 o.location=(-2.2,-6.8,6) if ray else (-.35,-9,1.05);aim(o,(0,0,0));d.type='ORTHO';d.ortho_scale=5.8 if ray else 5.05
 s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=str(folder/'preview.png')
 return s

def imported(slug):
 bpy.ops.wm.read_factory_settings(use_empty=True);folder=HERE/slug;folder.mkdir(exist_ok=True)
 bpy.ops.import_scene.gltf(filepath=str(SOURCES/slug/'original.glb'))
 mesh=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in ['Cube_0','Icosphere']]
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o not in mesh:o.hide_render=True;o.hide_set(True)
 root=bpy.data.objects.new('SourcePreservingReviewRoot',None);bpy.context.scene.collection.objects.link(root)
 for o in list(bpy.context.scene.objects):
  if o!=root and o.parent is None:o.parent=root
 root.rotation_euler.z=-math.pi/2;bpy.context.view_layer.update();lo,hi=bounds(mesh);scale=4/(hi.x-lo.x);root.scale=(scale,)*3;bpy.context.view_layer.update();lo,hi=bounds(mesh);root.location=-(lo+hi)/2;bpy.context.view_layer.update()
 for o in mesh:
  for p in o.data.polygons:p.use_smooth=True
 s=studio(folder);s.frame_set(24 if slug=='betta' else 1);s.frame_end=144 if slug=='betta' else 73
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(slug+'-review.blend')));bpy.ops.render.render(write_still=True)
 print('RENDER_COMPLETE',slug,flush=True)

if __name__=='__main__':
 for slug in sys.argv[sys.argv.index('--')+1:]:imported(slug)

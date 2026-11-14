"""Render five Cue 01 details with optional in-memory shading diagnosis; never save input."""
import argparse,bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--mode',choices=['source','flat-caps','sharp-caps'],default='source')
parser.add_argument('--glb')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert not args.glb or args.mode=='source', 'Candidate cap edits require source ngons'
if args.glb:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(Path(args.glb).resolve()))
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
source=Path(args.glb).resolve() if args.glb else Path(bpy.data.filepath)
digest=hashlib.sha256(source.read_bytes()).hexdigest()
root=bpy.data.objects['ASSET_Cue_01'];objects=[o for o in root.children_recursive if o.type=='MESH']
assert len(objects)==4
for ob in bpy.context.scene.objects:ob.hide_render=ob not in objects and ob!=root
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('QA cue neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
center=root.matrix_world.translation.copy()
for name,direction,power in [('Key',(-3,-4,5),600),('Fill',(4,2,3),400),('Bottom',(1,1,-4),200)]:
 light=bpy.data.lights.new('QA '+name,'AREA');light.energy=power;light.shape='DISK';light.size=4
 ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=center+Vector(direction);ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('QA cue camera');cam=bpy.data.objects.new(cam_data.name,cam_data);scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO';cam_data.clip_start=.001;cam_data.clip_end=100
views=[('butt-side',-.49,(0,-1,.2),.38),('butt-end',-.735,(-1,-.5,.2),.065),('joint',-.22,(0,-1,.4),.095),('ferrule',.714,(1,-2,1),.09),('tip-end',.735,(1,0,0),.02)]
report={'input_sha256':digest,'root':root.name,'no_source_save':True,'mode':args.mode,'diagnosis_only':'Non-source modes change only in-memory cap shading. Quad-axis metrics are N/A for triangulated GLB import; use exported geometric-normal tests.','states':{}}
for state in [args.mode]:
 folder=out/state;folder.mkdir(exist_ok=True)
 if state!='source':
  for ob in objects:
   for poly in ob.data.polygons:
    if len(poly.vertices)>4:
     poly.use_smooth=False
     if state=='sharp-caps':
      for li in poly.loop_indices:ob.data.edges[ob.data.loops[li].edge_index].use_edge_sharp=True
   ob.data.update()
 bpy.context.view_layer.update();stats=[]
 for ob in objects:
  mesh=ob.data;normals=[abs(mesh.corner_normals[li].vector.z) for p in mesh.polygons if len(p.vertices)==4 for li in p.loop_indices]
  stats.append({'mesh':ob.name,'smooth_cap_faces':sum(p.use_smooth for p in mesh.polygons if len(p.vertices)>4),'cap_faces':sum(len(p.vertices)>4 for p in mesh.polygons),'source_quad_axis_abs_min':min(normals) if normals else None,'source_quad_axis_abs_max':max(normals) if normals else None,'source_quad_axis_abs_mean':sum(normals)/len(normals) if normals else None})
 settings=[]
 for name,x,direction,scale in views:
  target=center+Vector((x,0,0));cam_data.ortho_scale=scale;cam.location=target+Vector(direction).normalized()*2;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
  settings.append({'name':name,'target':list(target),'camera':list(cam.location),'ortho_scale':scale})
 report['states'][state]={'meshes':stats,'views':settings}
assert digest==hashlib.sha256(source.read_bytes()).hexdigest()
(out/('diagnostic-'+state+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print('QA_DIAGNOSIS',json.dumps(report['states']),flush=True)

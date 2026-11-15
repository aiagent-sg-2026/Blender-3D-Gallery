"""Render the selected cue ball on its actual cloth; never save source."""
import argparse,bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--glb');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(args.glb).resolve() if args.glb else Path(bpy.data.filepath);digest=hashlib.sha256(source.read_bytes()).hexdigest()
if args.glb:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
bpy.context.view_layer.update();root=bpy.data.objects['ASSET_Ball_00'];body=[o for o in root.children_recursive if o.type=='MESH'];assert len(body)==1
cloth=[o for o in bpy.data.objects['ASSET_Table'].children_recursive if o.type=='MESH' and 'slate and green cloth' in o.name];assert len(cloth)==1;cloth=cloth[0]
points=[body[0].matrix_world@v.co for v in body[0].data.vertices];minimum=Vector([min(v[i] for v in points) for i in range(3)]);maximum=Vector([max(v[i] for v in points) for i in range(3)]);top=max((cloth.matrix_world@v.co).z for v in cloth.data.vertices);center=(minimum+maximum)/2
scene=bpy.context.scene
for ob in list(scene.objects):ob.hide_render=ob not in [*body,cloth]
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Cue ball contact QA');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
for direction,power in [((-1,-1,2),80),((2,1,1),60)]:
 light=bpy.data.lights.new('Cue ball QA light','AREA');light.energy=power;light.size=1;ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=center+Vector(direction);ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Cue ball QA camera');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=.12;data.clip_start=.001;data.clip_end=100
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);views=[]
for name,direction in [('front',(0,-1,.18)),('oblique',(1,-2,.5))]:
 cam.location=center+Vector(direction).normalized();cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);views.append(dict(name=name,camera=list(cam.location),target=list(center),ortho_scale=.12))
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'contact.json').write_text(json.dumps(dict(input_sha256=digest,no_source_save=True,root=root.name,cloth=cloth.name,ball_bottom_z=minimum.z,cloth_top_z=top,separation_m=minimum.z-top,views=views),indent=2)+'\n')

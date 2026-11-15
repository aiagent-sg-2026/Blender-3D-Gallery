"""Inspect and render chalk on its real rail in a disposable process."""
import argparse,bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--glb')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(args.glb).resolve() if args.glb else Path(bpy.data.filepath);digest=hashlib.sha256(source.read_bytes()).hexdigest()
if args.glb:
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
bpy.context.view_layer.update();root=bpy.data.objects['ASSET_Chalk'];chalk=[o for o in root.children_recursive if o.type=='MESH'];assert len(chalk)==2
def bounds(objects):
    points=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices]
    return [Vector([min(v[i] for v in points) for i in range(3)]),Vector([max(v[i] for v in points) for i in range(3)])]
lo,hi=bounds(chalk);rails=[]
for ob in bpy.data.objects['ASSET_Table'].children_recursive:
    if ob.type=='MESH' and ob.name.startswith('Long rail'):
        a,b=bounds([ob])
        if lo.x>=a.x and hi.x<=b.x and lo.y>=a.y and hi.y<=b.y:rails.append((ob,a,b))
assert len(rails)==1;rail,rail_lo,rail_hi=rails[0]
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
for ob in list(scene.objects):ob.hide_render=ob not in [*chalk,rail]
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Chalk contact QA');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
target=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,rail_hi.z+.013))
for direction,power in [((-1,-1,2),80),((2,1,1),60)]:
    light=bpy.data.lights.new('Chalk contact light','AREA');light.energy=power;light.size=1
    ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=target+Vector(direction);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Chalk contact camera');cam=bpy.data.objects.new(cam_data.name,cam_data);scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO';cam_data.ortho_scale=.060;cam_data.clip_start=.001;cam_data.clip_end=100
views=[]
for name,direction in [('front',(0,-1,.14)),('oblique',(1,-2,.5))]:
    cam.location=target+Vector(direction).normalized();cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);views.append(dict(name=name,camera=list(cam.location),target=list(target),ortho_scale=.060))
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'contact.json').write_text(json.dumps(dict(input_sha256=digest,no_source_save=True,root=root.name,rail=rail.name,chalk_bottom_z=lo.z,rail_top_z=rail_hi.z,separation_m=lo.z-rail_hi.z,footprint_covered_by_rail=True,views=views),indent=2)+'\n')

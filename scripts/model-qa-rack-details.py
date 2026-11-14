"""Render rack joints in a disposable process; candidate mode never saves."""
import argparse, bpy, hashlib, json, runpy, sys
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--candidate',action='store_true')
p.add_argument('--glb')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert not args.glb or not args.candidate
source=Path(args.glb).resolve() if args.glb else Path(bpy.data.filepath)
digest=hashlib.sha256(source.read_bytes()).hexdigest()
if args.glb:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
root=bpy.data.objects['ASSET_Triangle_Rack']
bars=sorted([ob for ob in root.children_recursive if ob.type=='MESH'],key=lambda ob:ob.name)
bpy.context.view_layer.update()
if args.candidate:
    helper=Path(__file__).resolve().parents[1]/'models/eight-ball-billiards/rack_geometry.py'
    runpy.run_path(str(helper))['close_rack_joints'](bars)
scene=bpy.context.scene
for ob in list(scene.objects): ob.hide_render=ob not in bars
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=650;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Rack QA neutral');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
center=root.matrix_world.translation
for direction,power in [((-3,-4,5),600),((4,2,3),400),((1,1,-4),200)]:
    light=bpy.data.lights.new('Rack QA area','AREA');light.energy=power;light.size=4
    ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob)
    ob.location=center+Vector(direction);ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data=bpy.data.cameras.new('Rack QA camera');cam=bpy.data.objects.new(cam_data.name,cam_data)
scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO';cam_data.clip_start=.001;cam_data.clip_end=100
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);views=[]
targets=[]
for ob,end in [(bars[0],False),(bars[0],True),(bars[1],True)]:
    ring=[]
    for vertex in ob.data.vertices:
        if (vertex.co.z>0)!=end:continue
        point=ob.matrix_world@vertex.co
        if not any((point-other).length<1e-7 for other in ring):ring.append(point)
    assert len(ring)==12
    targets.append(sum(ring,Vector())/len(ring))
for i,target in enumerate(targets):
    for name,direction in [('top',(0,0,1)),('oblique',(1,-2,2))]:
        cam_data.ortho_scale=.075;cam.location=target+Vector(direction).normalized()
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/f'joint-{i+1}-{name}.png');bpy.ops.render.render(write_still=True)
        views.append(dict(name=f'joint-{i+1}-{name}',target=list(target),camera=list(cam.location),ortho_scale=.075))
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'render-settings.json').write_text(json.dumps(dict(input_sha256=digest,candidate=args.candidate,no_source_save=True,views=views,samples=32),indent=2)+'\n')

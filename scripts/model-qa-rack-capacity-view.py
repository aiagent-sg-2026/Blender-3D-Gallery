"""Render a disposable fifteen-ball size witness; never save or export it."""
import argparse, bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--glb',required=True);p.add_argument('--output',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(args.glb).resolve();digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
root=bpy.data.objects['ASSET_Triangle_Rack'];bars=[o for o in root.children_recursive if o.type=='MESH'];assert len(bars)==3
bpy.context.view_layer.update();center=sum((o.matrix_world.translation for o in bars),Vector())/3
radius=.05715/2;centers=[]
mat=bpy.data.materials.new('Diagnostic balls only');mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.8,.8,.8,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.3
for row in range(5):
    for column in range(row+1):
        point=center+Vector(((row-8/3)*2*radius*math.sqrt(3)/2,(column-row/2)*2*radius,-.0089+radius))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=radius,location=point)
        ob=bpy.context.object;ob.name='Diagnostic size witness';ob.data.materials.append(mat)
        for face in ob.data.polygons:face.use_smooth=True
        centers.append(list(point))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
world=bpy.data.worlds.new('Capacity neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;scene.world=world
for direction,power in [((-3,-4,5),600),((4,2,3),400)]:
    light=bpy.data.lights.new('Capacity QA','AREA');light.energy=power;light.size=4
    ob=bpy.data.objects.new(light.name,light);scene.collection.objects.link(ob);ob.location=center+Vector(direction);ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.cameras.new('Capacity QA camera');cam=bpy.data.objects.new(camera.name,camera);scene.collection.objects.link(cam);scene.camera=cam;camera.type='ORTHO';camera.ortho_scale=.49
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);views=[]
for name,direction in [('top',(0,0,1)),('three-quarter',(3,-4,5))]:
    cam.location=center+Vector(direction).normalized();cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);views.append(dict(name=name,camera=list(cam.location),target=list(center),ortho_scale=.49))
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'render-settings.json').write_text(json.dumps(dict(input_sha256=digest,no_source_save=True,diagnostic_only='Fifteen temporary spheres are not added to any product file.',ball_diameter_m=2*radius,ball_centers=centers,views=views),indent=2)+'\n')

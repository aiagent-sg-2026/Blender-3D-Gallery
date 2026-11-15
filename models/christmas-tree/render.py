import bpy, math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(BASE/'exports/christmas-tree.glb'))
scene=bpy.context.scene
world=bpy.data.worlds.new('Studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.052,.066,.052,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
bpy.ops.object.camera_add(location=(4,-7,3.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,1.47))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.55;scene.camera=camera
for name,loc,power,size in [('Key',(4,-5,6),650,4),('Fill',(-4,-2,3.5),380,4),('Rim',(2,4,5),750,3)]:
    bpy.ops.object.light_add(type='AREA', location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((0,0,1.2))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=640;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(BASE/'previews/hero.png');bpy.ops.render.render(write_still=True)

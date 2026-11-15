"""Render the actual exported GLB for a faithful gallery thumbnail."""
import bpy
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(BASE/'exports/chinese-new-year-lion-dance-head.glb'))
scene=bpy.context.scene
world=bpy.data.worlds.new('Studio');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.052,.066,.052,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.75
bpy.ops.object.camera_add(location=(2.5,-7,2.3));camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,1.0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=2.65;scene.camera=camera
for name,location,power,size in [('Key',(4,-5,6),620,4),('Fill',(-4,-2,3.5),380,4),('Rim',(2,4,5),650,3)]:
    bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object
    light.name,light.data.energy,light.data.shape,light.data.size=name,power,'DISK',size
    light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
scene.render.filepath=str(BASE/'previews/hero.png');bpy.ops.render.render(write_still=True)

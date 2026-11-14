"""Render one reviewed cue card and the dependent scene without saving input."""
import bpy
from mathutils import Vector
from pathlib import Path


def render_previews(root_name, output):
    assert root_name in {'ASSET_Cue_01', 'ASSET_Cue_02'}
    scene = bpy.context.scene
    out = Path(output)
    out.mkdir(exist_ok=True)
    scene.render.filepath = str(out / 'scene.png')
    bpy.ops.render.render(write_still=True)
    cue = bpy.data.objects[root_name]
    objects = [o for o in cue.children_recursive if o.type == 'MESH']
    for ob in scene.objects:
        if ob.type == 'MESH':
            ob.hide_render = ob not in objects
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.background_type = 'WORLD'
    scene.world.color = (.12, .15, .15)
    scene.render.resolution_x = scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    for mat in bpy.data.materials:
        if mat.use_nodes and mat.node_tree.nodes.get('Principled BSDF'):
            mat.diffuse_color = mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
    coords = [ob.matrix_world @ Vector(corner) for ob in objects for corner in ob.bound_box]
    minimum = Vector([min(v[i] for v in coords) for i in range(3)])
    maximum = Vector([max(v[i] for v in coords) for i in range(3)])
    center = (minimum + maximum) / 2
    size = (maximum - minimum).length
    camera = scene.camera
    camera.location = center + Vector((3.3,-4.5,4.8)).normalized() * size * 3
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = size * 1.18
    scene.render.filepath = str(out / (root_name.removeprefix('ASSET_').lower() + '.png'))
    bpy.ops.render.render(write_still=True)
    # Do not save temporary render/camera/material display settings into source.

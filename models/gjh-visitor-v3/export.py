"""Export the GLB, save the source and render preview evidence."""
from pathlib import Path
import math
import bpy
from mathutils import Matrix, Vector



def render_and_export(scene, rig, root, material):
    root = Path(root)
    originals = [o for o in scene.objects if o.type == 'MESH']
    # Joining temporary copies by semantic slot and material cuts draw calls while
    # leaving the saved Blender source independently editable.
    groups = {}
    for source in originals:
        name = source.name.lower()
        if 'alternate hair' in name:
            slot = 'hair_alt'
        elif any(x in name for x in ('hair', 'fringe', 'quiff')):
            slot = 'hair'
        elif any(x in name for x in ('lanyard', 'badge')):
            slot = 'badge'
        elif 'backpack' in name:
            slot = 'backpack'
        elif 'watch' in name:
            slot = 'watch'
        elif any(x in name for x in ('sneaker', 'lace')):
            slot = 'shoes'
        elif any(x in name for x in ('trouser', 'chino')):
            slot = 'bottom'
        elif 'tee ' in name:
            slot = 'tee'
        elif 'hoodie' in name:
            slot = 'jacket'
        else:
            slot = 'body'
        material_name = source.data.materials[0].name if source.data.materials else 'none'
        copy = source.copy()
        copy.data = source.data.copy()
        scene.collection.objects.link(copy)
        groups.setdefault((slot, material_name), []).append(copy)
    exports = []
    for (slot, material_name), parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for part in parts:
            part.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        if len(parts) > 1:
            bpy.ops.object.join()
        parts[0].name = f'V3_{slot}_{material_name}'
        for layer in list(parts[0].data.uv_layers):
            parts[0].data.uv_layers.remove(layer)
        exports.append(parts[0])
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    for obj in exports:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(filepath=str(root / 'exports/gjh-visitor-v3.glb'),
        export_format='GLB', use_selection=True, export_yup=True, export_animations=True,
        export_animation_mode='NLA_TRACKS', export_merge_animation='NLA_TRACK',
        export_force_sampling=True, export_optimize_animation_keep_anim_object=True,
        export_apply=True, export_cameras=False, export_lights=False)
    for obj in exports:
        bpy.data.objects.remove(obj, do_unlink=True)
    # The source opens in its default look; both variants remain exportable.
    for obj in originals:
        if obj.name.startswith('Alternate '):
            obj.hide_render = True

    world = bpy.data.worlds.new('Visitor v3 studio')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (.4, .4, .4, 1)
    world.node_tree.nodes['Background'].inputs[1].default_value = .5
    scene.world = world
    floor = material('Studio floor', (207, 211, 205), 1)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.008))
    bpy.context.object.data.materials.append(floor)
    def aim(obj, point):
        obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    for loc, power, size in [((3, -4, 5), 450, 4), ((-3, -2, 3), 300, 3), ((2, 3, 4), 500, 3)]:
        bpy.ops.object.light_add(type='AREA', location=loc)
        light = bpy.context.object
        light.data.energy = power
        light.data.shape = 'DISK'
        light.data.size = size
        aim(light, (0, 0, .9))
    bpy.ops.object.camera_add(location=(2, -4, 2))
    scene.camera = bpy.context.object
    scene.camera.data.type = 'ORTHO'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 600
    scene.render.resolution_y = 800
    scene.view_settings.view_transform = 'AgX'
    bpy.ops.wm.save_as_mainfile(filepath=str(root / 'sources/gjh-visitor-v3.blend'), compress=True)
    for view, loc, clip, frame in [('front', (0, -4, 1.05), 'idle', 1),
                                   ('side', (4, 0, 1.05), 'idle', 1),
                                   ('back', (0, 4, 1.05), 'idle', 1),
                                   ('walk', (2, -4, 1.4), 'walk', 8),
                                   ('run', (2, -4, 1.4), 'run', 6)]:
        for track in rig.animation_data.nla_tracks:
            track.mute = track.name != clip
        scene.frame_set(frame)
        scene.camera.location = loc
        aim(scene.camera, (0, 0, .85))
        scene.camera.data.ortho_scale = 2.04
        scene.render.filepath = str(root / 'previews' / f'{view}.png')
        bpy.ops.render.render(write_still=True)

"""Export the GLB, save the source and render preview evidence."""
from pathlib import Path
import math
import bpy
from mathutils import Matrix, Vector



def setup_studio(scene, material):
    world = bpy.data.worlds.new('Visitor v3 studio')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (.4, .4, .4, 1)
    world.node_tree.nodes['Background'].inputs[1].default_value = .5
    scene.world = world
    floor = material('Studio floor', (207, 211, 205), 1)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.004))
    bpy.context.object.data.materials.append(floor)
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


def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()


VIEWS = [('front', (0, -4, 1.05), 'idle', 1), ('side', (4, 0, 1.05), 'idle', 1),
         ('back', (0, 4, 1.05), 'idle', 1), ('walk', (2, -4, 1.4), 'walk', 8),
         ('run', (2, -4, 1.4), 'run', 6)]


def render_views(scene, root, views, rig=None, prefix=''):
    for view, loc, clip, frame in views:
        if rig is not None and rig.animation_data:
            for track in rig.animation_data.nla_tracks:
                track.mute = track.name != clip
        scene.frame_set(frame)
        scene.camera.location = loc
        aim(scene.camera, (0, 0, .89))
        scene.camera.data.ortho_scale = 2.1
        scene.render.filepath = str(Path(root) / 'previews' / f'{prefix}{view}.png')
        bpy.ops.render.render(write_still=True)


def quick_render(scene, rig, root):
    from materials import mat
    for o in scene.objects:
        if o.name.startswith('Alternate '):
            o.hide_render = True
    setup_studio(scene, mat)
    scene.cycles.samples = 8
    render_views(scene, root, VIEWS[:3], prefix='quick-')
    scene.camera.data.type = 'PERSP'
    scene.camera.data.lens = 85
    scene.camera.location = (0, -1.4, 1.62)
    aim(scene.camera, (0, 0, 1.6))
    scene.render.filepath = str(Path(root) / 'previews' / 'quick-face.png')
    bpy.ops.render.render(write_still=True)


def classify(name):
    name = name.lower()
    if 'alternate hair' in name:
        return 'hair_alt'
    if 'hair' in name:
        return 'hair'
    if any(x in name for x in ('lanyard', 'badge')):
        return 'badge'
    if 'backpack' in name:
        return 'backpack'
    if 'watch' in name:
        return 'watch'
    if 'sneaker' in name:
        return 'shoes'
    if 'chino' in name:
        return 'bottom'
    if 'tee ' in name:
        return 'tee'
    if 'hoodie' in name:
        return 'jacket'
    return 'body'


def render_and_export(scene, rig, root, material):
    root = Path(root)
    originals = [o for o in scene.objects if o.type == 'MESH']
    # Joining temporary copies by semantic slot and material cuts draw calls while
    # leaving the saved Blender source independently editable.
    groups = {}
    for source in originals:
        slot = classify(source.name)
        copy = source.copy()
        copy.data = source.data.copy()
        scene.collection.objects.link(copy)
        pieces = [copy]
        if len(copy.data.materials) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            copy.select_set(True)
            bpy.context.view_layer.objects.active = copy
            bpy.ops.mesh.separate(type='MATERIAL')
            pieces = list(bpy.context.selected_objects)
        for piece in pieces:
            used = {p.material_index for p in piece.data.polygons}
            material_name = piece.data.materials[min(used) if used else 0].name if piece.data.materials else 'none'
            groups.setdefault((slot, material_name), []).append(piece)
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
    # glTF requires skinned meshes at the scene root. The armature modifier
    # retains the skin binding when the temporary copies are unparented.
    for obj in exports:
        world_matrix = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world_matrix
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

    setup_studio(scene, material)
    bpy.ops.wm.save_as_mainfile(filepath=str(root / 'sources/gjh-visitor-v3.blend'), compress=True)
    render_views(scene, root, VIEWS, rig)
    # Pose evidence: one mid-clip frame per contract action, three-quarter view.
    from animations import CLIPS
    scene.render.resolution_x, scene.render.resolution_y = 300, 400
    scene.cycles.samples = 8
    (root / 'previews' / 'poses').mkdir(exist_ok=True)
    poses = [(name, (2.4, -3.2, 1.3), name, max(1, int(frames * (.5 if not loops else .3)))) for name, frames, loops in CLIPS]
    render_views(scene, root, poses, rig, prefix='poses/')

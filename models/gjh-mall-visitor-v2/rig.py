"""Build the v2 armature, animation clips, export and render evidence."""
from pathlib import Path
import math
import bpy
from mathutils import Matrix, Vector


def build_rig(scene, root, body, head, limbs):
    bpy.context.view_layer.update()
    nodes = {'Body': body, 'Head': head}
    for label, joints in limbs.items():
        for suffix, node in zip(('Shoulder', 'Elbow', 'Hip', 'Knee', 'Foot'), joints):
            nodes[label + suffix] = node
    positions = {name: node.matrix_world.translation.copy() for name, node in nodes.items()}
    positions['Spine'] = positions['Body'] + Vector((0, 0, .14))
    positions['Neck'] = positions['Head'] + Vector((0, 0, -.04))
    parents = {'Spine': 'Body', 'Neck': 'Spine', 'Head': 'Neck'}
    for label in ('Left', 'Right'):
        for child, parent in [('Shoulder', 'Spine'), ('Elbow', label + 'Shoulder'),
                              ('Hip', 'Body'), ('Knee', label + 'Hip'), ('Foot', label + 'Knee')]:
            parents[label + child] = parent
        positions[label + 'Hand'] = limbs[label][1].matrix_world @ Vector((0, -.005, -.18))
        parents[label + 'Hand'] = label + 'Elbow'
        positions[label + 'Thumb'] = bpy.data.objects[label + 'Thumb'].matrix_world.translation.copy()
        parents[label + 'Thumb'] = label + 'Hand'
        for i in range(4):
            name = label + ' Finger ' + str(i)
            positions[label + 'Finger' + str(i)] = bpy.data.objects[name].matrix_world.translation.copy()
            parents[label + 'Finger' + str(i)] = label + 'Hand'

    data = bpy.data.armatures.new('VisitorV2Humanoid')
    rig = bpy.data.objects.new('GJHMallVisitorV2', data)
    scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, pos in positions.items():
        bone = data.edit_bones.new(name)
        bone.head = pos
        bone.tail = pos + Vector((0, 0, .08 if 'Finger' not in name else .025))
    for name, parent in parents.items():
        data.edit_bones[name].parent = data.edit_bones[parent]
        data.edit_bones[name].use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')

    objects = [o for o in scene.objects if o.type == 'MESH']
    for obj in objects:
        parent_name = obj.parent.name if obj.parent else None
        bone_name = parent_name
        for label in ('Left', 'Right'):
            if obj.name.startswith(label + ' Finger '):
                bone_name = label + 'Finger' + obj.name[len(label + ' Finger ')]
            elif obj.name.startswith(label + 'Thumb'):
                bone_name = label + 'Thumb'
            elif obj.name.startswith(label + ' Palm'):
                bone_name = label + 'Hand'
        if bone_name not in positions:
            raise RuntimeError(f'No bone for {obj.name}: {parent_name}')
        # Bake the authored rest transform before binding. Source components remain separate.
        transform = obj.matrix_world.copy()
        obj.data.transform(transform)
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        group = obj.vertex_groups.new(name=bone_name)
        child_bone = None
        if obj.name.endswith('Arm skin'):
            child_bone = bone_name.replace('Shoulder', 'Elbow')
        elif obj.name.endswith('Jeans'):
            child_bone = bone_name.replace('Hip', 'Knee')
        if child_bone:
            lower = obj.vertex_groups.new(name=child_bone)
            joint = positions[child_bone].z
            for vertex in obj.data.vertices:
                lower_weight = max(0.0, min(1.0, (joint + .035 - vertex.co.z) / .07))
                if lower_weight < 1:
                    group.add([vertex.index], 1 - lower_weight, 'REPLACE')
                if lower_weight > 0:
                    lower.add([vertex.index], lower_weight, 'REPLACE')
        else:
            group.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        modifier = obj.modifiers.new('Humanoid skin', 'ARMATURE')
        modifier.object = rig

    for obj in list(nodes.values()) + [root]:
        bpy.data.objects.remove(obj, do_unlink=True)
    rig.animation_data_create()
    bones = rig.pose.bones
    clips = [('idle', 60), ('walk', 30), ('sprint', 22), ('sit', 30),
             ('stand', 30), ('pickup', 36), ('place', 36), ('push', 30), ('elevator', 30)]
    scene.render.fps = 30
    for clip, duration in clips:
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        action = bpy.data.actions.new(clip)
        rig.animation_data.action = action
        for frame in list(range(1, duration + 1, 3)) + [duration + 1]:
            phase = (frame - 1) / duration * math.tau
            progress = (frame - 1) / duration
            ease = progress * progress * (3 - 2 * progress)
            for bone in bones:
                bone.rotation_mode = 'XYZ'
                bone.rotation_euler = (0, 0, 0)
                bone.location = (0, 0, 0)
            for label, sign in (('Left', 1), ('Right', -1)):
                swing = math.sin(phase) * sign
                shoulder = bones[label + 'Shoulder']
                elbow = bones[label + 'Elbow']
                hip = bones[label + 'Hip']
                knee = bones[label + 'Knee']
                if clip in ('walk', 'sprint', 'push'):
                    speed = {'walk': .36, 'sprint': .66, 'push': .22}[clip]
                    hip.rotation_euler.x = swing * speed
                    knee.rotation_euler.x = max(0, -swing) * speed * 1.1
                    shoulder.rotation_euler.x = -swing * speed if clip != 'push' else -.85
                    elbow.rotation_euler.x = -.2 if clip != 'push' else -.75
                elif clip in ('sit', 'stand'):
                    amount = ease if clip == 'sit' else 1 - ease
                    hip.rotation_euler.x = -1.2 * amount
                    knee.rotation_euler.x = 1.15 * amount
                elif clip in ('pickup', 'place', 'elevator') and label == 'Right':
                    amount = math.sin(math.pi * progress)
                    shoulder.rotation_euler.x = -.9 * amount
                    elbow.rotation_euler.x = -.8 * amount
                    for i in range(4):
                        bones[label + 'Finger' + str(i)].rotation_euler.x = .55 * amount
                else:
                    shoulder.rotation_euler.x = .025 * math.sin(phase)
            animated_names = [label + part for label in ('Left', 'Right')
                              for part in ('Shoulder', 'Elbow', 'Hip', 'Knee')]
            if clip in ('pickup', 'place', 'elevator'):
                animated_names += ['RightFinger' + str(i) for i in range(4)]
            for name in animated_names:
                bone = bones[name]
                bone.keyframe_insert(data_path='rotation_euler', frame=frame)
        if clip in ('walk', 'sprint', 'push'):
            # Correct the hips from evaluated shoe vertices, not joint positions.
            # Sampling at the export frame rate avoids the visible airborne gait.
            shoes = [o for o in objects if 'sneaker' in o.name.lower()]
            if not shoes:
                raise RuntimeError('No sneaker meshes for floor contact')
            for frame in range(1, duration + 2):
                scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                floor = math.inf
                for obj in shoes:
                    evaluated = obj.evaluated_get(depsgraph)
                    mesh = evaluated.to_mesh()
                    floor = min(floor, min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
                    evaluated.to_mesh_clear()
                body_bone = bones['Body']
                correction = body_bone.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, -floor))
                body_bone.location += correction
                body_bone.keyframe_insert(data_path='location', frame=frame)
        rig.animation_data.action = None
        track = rig.animation_data.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 1, action)
    for track in rig.animation_data.nla_tracks:
        track.mute = track.name != 'idle'
    scene.frame_set(1)
    return rig


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
        elif 'alternate hoodie' in name:
            slot = 'outfit_alt'
        elif 'glasses' in name:
            slot = 'glasses'
        elif any(x in name for x in ('hair', 'fringe', 'lock', 'crown', 'sweep')):
            slot = 'hair'
        elif 'backpack' in name:
            slot = 'backpack'
        elif 'watch' in name:
            slot = 'watch'
        elif any(x in name for x in ('sneaker', 'lace')):
            slot = 'shoes'
        elif any(x in name for x in ('polo', 'sleeve', 'collar', 'placket', 'button', 'denim', 'jeans', 'cuff', 'embroidery')):
            slot = 'outfit'
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
        parts[0].name = f'V2_{slot}_{material_name}'
        for layer in list(parts[0].data.uv_layers):
            parts[0].data.uv_layers.remove(layer)
        exports.append(parts[0])
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    for obj in exports:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(filepath=str(root / 'exports/gjh-mall-visitor-v2.glb'),
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

    world = bpy.data.worlds.new('Visitor v2 studio')
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
    bpy.ops.wm.save_as_mainfile(filepath=str(root / 'sources/gjh-mall-visitor-v2.blend'), compress=True)
    for view, loc, clip, frame in [('front', (0, -4, 1.05), 'idle', 1),
                                   ('side', (4, 0, 1.05), 'idle', 1),
                                   ('back', (0, 4, 1.05), 'idle', 1),
                                   ('walk', (2, -4, 1.4), 'walk', 8),
                                   ('sprint', (2, -4, 1.4), 'sprint', 6)]:
        for track in rig.animation_data.nla_tracks:
            track.mute = track.name != clip
        scene.frame_set(frame)
        scene.camera.location = loc
        aim(scene.camera, (0, 0, .85))
        scene.camera.data.ortho_scale = 2.04
        scene.render.filepath = str(root / 'previews' / f'{view}.png')
        bpy.ops.render.render(write_still=True)

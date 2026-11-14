"""Build the v3 humanoid armature, skin weights and bone naming."""
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
        positions[label + 'Hand'] = limbs[label][1].matrix_world @ Vector((0, -.005, -.27))
        parents[label + 'Hand'] = label + 'Elbow'
        positions[label + 'Thumb'] = bpy.data.objects[label + 'Thumb'].matrix_world.translation.copy()
        parents[label + 'Thumb'] = label + 'Hand'
        for i in range(4):
            name = label + ' Finger ' + str(i)
            positions[label + 'Finger' + str(i)] = bpy.data.objects[name].matrix_world.translation.copy()
            parents[label + 'Finger' + str(i)] = label + 'Hand'

    data = bpy.data.armatures.new('VisitorV3Humanoid')
    rig = bpy.data.objects.new('GJHVisitorV3', data)
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
        if obj.name.endswith(('Arm skin','Sleeve')):
            child_bone = bone_name.replace('Shoulder', 'Elbow')
        elif obj.name.endswith('Trousers'):
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
    return rig

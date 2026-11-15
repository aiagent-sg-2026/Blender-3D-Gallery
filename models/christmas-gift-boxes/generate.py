"""Create editable gift boxes and export their static gallery GLB (Blender 5.1)."""
import bpy
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
for directory in ('sources', 'exports', 'previews'):
    (BASE / directory).mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def material(name, color, metallic=0, roughness=.4):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return result


red = material('Cranberry red paper', (.48, .012, .025), .1, .42)
green = material('Evergreen paper', (.018, .16, .075), .1, .45)
cream = material('Warm ivory paper', (.82, .73, .51), .05, .48)
gold = material('Gold satin ribbon', (.83, .45, .055), .55, .25)
red_ribbon = material('Red satin ribbon', (.52, .018, .025), .35, .28)
root = bpy.data.objects.new('ASSET_ChristmasGiftBoxes', None)
bpy.context.collection.objects.link(root)


def cube(name, parent, location, dimensions, surface, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    obj.parent = parent
    obj.location = location
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(surface)
    if bevel:
        modifier = obj.modifiers.new('Soft edges', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def ribbon_loop(name, parent, side, z, size, ribbon):
    """A curved ribbon strip with width, modeled explicitly rather than a line."""
    vertices = []
    steps = 32
    for i in range(steps + 1):
        t = math.pi * i / steps
        x = side * size * math.sin(t)
        height = .035 * math.sin(t) + size * .36 * math.sin(2 * t)
        for y in (-size * .23, size * .23):
            vertices.append((x, y, z + height))
    faces = [(2*i, 2*i+1, 2*i+3, 2*i+2) for i in range(steps)]
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.data.materials.append(ribbon)
    solidify = obj.modifiers.new('Ribbon thickness', 'SOLIDIFY')
    solidify.thickness = .008
    bevel = obj.modifiers.new('Ribbon edge', 'BEVEL')
    bevel.width = .004
    bevel.segments = 2
    return obj


def gift(name, position, rotation, dimensions, paper, ribbon):
    width, depth, height = dimensions
    group = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(group)
    group.parent = root
    group.location = position
    group.rotation_euler[2] = rotation
    lid_height = .10 * height
    top = height + lid_height
    band = min(width, depth) * .18
    cube(name + ' box', group, (0, 0, height/2), (width, depth, height), paper, .018)
    cube(name + ' lid', group, (0, 0, height + lid_height/2), (width+.045, depth+.045, lid_height), paper, .012)
    # Two ribbons cross on the lid and continue down all four sides.
    cube(name + ' ribbon top X', group, (0, 0, top+.006), (width+.05, band, .012), ribbon, .004)
    cube(name + ' ribbon top Y', group, (0, 0, top+.013), (band, depth+.05, .012), ribbon, .004)
    for sign in (-1, 1):
        cube(name + ' ribbon side X ' + str(sign), group, (sign*(width/2+.006), 0, height/2), (.012, band, height-.01), ribbon, .003)
        cube(name + ' ribbon side Y ' + str(sign), group, (0, sign*(depth/2+.006), height/2), (band, .012, height-.01), ribbon, .003)
        cube(name + ' ribbon lid edge X ' + str(sign), group, (sign*(width/2+.026), 0, height+lid_height/2), (.012, band, lid_height), ribbon, .002)
        cube(name + ' ribbon lid edge Y ' + str(sign), group, (0, sign*(depth/2+.026), height+lid_height/2), (band, .012, lid_height), ribbon, .002)
    bow_size = min(width, depth)*.34
    for side in (-1, 1):
        ribbon_loop(name + ' bow loop ' + str(side), group, side, top+.060, bow_size, ribbon)
    cube(name + ' bow knot', group, (0, 0, top+.062), (band*.9, band*.8, .07), ribbon, .025)
    # Ribbon tails lie over the top of the lid, separate from the crossing bands.
    for side in (-1, 1):
        tail = cube(name + ' bow tail ' + str(side), group, (side*band*.65, -band*.6, top+.028), (band*1.4, band*.52, .012), ribbon, .004)
        tail.rotation_euler[2] = side * -.45


gift('Large red present', (-.43, .18, 0), -.12, (.83, .69, .70), red, gold)
gift('Green present', (.41, .17, 0), .11, (.62, .61, .57), green, gold)
gift('Ivory present', (-.04, -.50, 0), .07, (.60, .52, .43), cream, red_ribbon)
gift('Small gold present', (.57, -.48, 0), .12, (.34, .32, .29), gold, red_ribbon)

bpy.ops.object.select_all(action='DESELECT')
for obj in [root] + list(root.children_recursive):
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE / 'sources/christmas-gift-boxes.blend'))
# Keep the saved source fully editable; batch evaluated export meshes by material
# so the web viewer does not make a draw call for each individual ribbon piece.
bpy.ops.object.select_all(action='DESELECT')
for obj in root.children_recursive:
    if obj.type == 'MESH':
        obj.select_set(True)
bpy.context.view_layer.objects.active = next(obj for obj in root.children_recursive if obj.type == 'MESH')
bpy.ops.object.convert(target='MESH')
for surface in (red, green, cream, gold, red_ribbon):
    group = [obj for obj in root.children_recursive if obj.type == 'MESH' and obj.data.materials[0] == surface]
    if not group:
        continue
    bpy.ops.object.select_all(action='DESELECT')
    for obj in group:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = group[0]
    if len(group) > 1:
        bpy.ops.object.join()
    merged = bpy.context.view_layer.objects.active
    world = merged.matrix_world.copy()
    merged.parent = root
    merged.matrix_world = world
    merged.name = 'Export batch ' + surface.name
for obj in list(root.children):
    if obj.type == 'EMPTY':
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for obj in [root] + list(root.children_recursive):
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(filepath=str(BASE / 'exports/christmas-gift-boxes.glb'), export_format='GLB', use_selection=True, export_apply=True)
print('F02_EXPORT_COMPLETE')

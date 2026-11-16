"""Original deterministic entrance portal, Blender 5.2.3; no external assets.

Metres, Blender +Z up / -Y front; glTF +Y up / +Z front.
Rebuild replaces source. --export-source preserves saved component edits.
"""
from pathlib import Path
import json
import math
import sys
import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'arched-gateway-sign'
ROOT = 'ASSET_ArchedGatewaySign'
TARGET = Vector((0, 0, 2.9))


def material(name, rgb, metallic=0, roughness=.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb) + (1,)
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = color
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    m.diffuse_color = color
    return m


def empty(name, parent=None, location=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.parent = parent
    o.location = location
    return o


def finish(o, name, mat, root, bevel=0):
    o.name = name
    o.data.materials.append(mat)
    o.parent = root
    bpy.context.view_layer.objects.active = o
    if bevel:
        mod = o.modifiers.new('Manufactured edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o


def box(name, location, dimensions, mat, root, bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat, root, bevel)


def arch(name, outer, inner, depth, y, mat, root):
    # A closed elliptical half-ring with 80 sections, not disconnected rods.
    n = 80
    vertices = []
    for yy in (y - depth / 2, y + depth / 2):
        for rx, rz in (outer, inner):
            for i in range(n + 1):
                a = math.pi * i / n
                vertices.append((rx * math.cos(a), yy, 3.65 + rz * math.sin(a)))
    stride = n + 1
    faces = []
    for i in range(n):
        a, b, c, d = i, stride + i, 2 * stride + i, 3 * stride + i
        faces.extend(((a, a + 1, b + 1, b), (c, d, d + 1, c + 1),
                      (a, c, c + 1, a + 1), (b, b + 1, d + 1, d)))
    faces.extend(((0, stride, 3 * stride, 2 * stride),
                  (n, 2 * stride + n, 3 * stride + n, stride + n)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    return finish(o, name, mat, root)


def build(root):
    frame = material('Frame neutral mineral', (.67, .68, .66), .15, .42)
    sign = material('Sign band warm white', (.90, .89, .85), .05, .48)
    trim = material('Trim graphite', (.23, .25, .26), .60, .33)
    for side, x in (('Left', -5.66), ('Right', 5.66)):
        box('SOURCE_Foot_' + side, (x, 0, .09), (.68, 1.30, .18), frame, root, .018)
        box('SOURCE_Pillar_' + side, (x, 0, 1.915), (.48, .62, 3.47), frame, root, .012)
        box('SOURCE_BaseCollar_' + side, (x, 0, .24), (.59, .75, .12), trim, root, .008)
        box('SOURCE_SpringCollar_' + side, (x, 0, 3.59), (.55, .72, .12), trim, root, .008)
        for y in (-.316, .316):
            box(f'SOURCE_PillarReveal_{side}_{y}', (x + math.copysign(.14, x), y, 1.945),
                (.035, .012, 3.27), trim, root, .003)
        for dx in (-.23, .23):
            for y in (-.36, .36):
                bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.022,
                    depth=.012, location=(x + dx, y, .186))
                finish(bpy.context.object, f'SOURCE_Anchor_{side}_{dx}_{y}', trim, root, .002)
    arch('SOURCE_CurvedBeam', (5.90, 2.35), (5.42, 1.87), .62, 0, frame, root)
    for y in (-.318, .318):
        arch('SOURCE_ArchReveal_' + str(y), (5.81, 2.26), (5.77, 2.22), .016, y, trim, root)
    # The solid blank band is a separately named runtime node with a local centre pivot.
    band = box('SOURCE_BlankBand', (0, -.49, 4.575), (10.90, .28, .85), sign, root, .018)
    band['purpose'] = 'Blank sign band; add scene-owned text later'
    for z in (4.126, 5.024):
        box('SOURCE_SignHorizontalTrim_' + str(z), (0, -.49, z),
            (10.96, .31, .048), trim, root, .006)
    for x in (-5.456, 5.456):
        box('SOURCE_SignEndTrim_' + str(x), (x, -.49, 4.575),
            (.048, .31, .85), trim, root, .006)
    for x in (-5.25, 5.25):
        box('SOURCE_SignBracket_' + str(x), (x, -.30, 4.53),
            (.16, .36, .28), trim, root, .008)
    anchor = empty('SIGN_TextAnchor', root, (0, -.641, 4.575))
    anchor['purpose'] = 'Front text plane; glTF +Z normal; scene supplies lettering'
    root['units'] = 'metres'
    root['front_axis'] = 'Blender -Y / glTF +Z'
    root['origin'] = 'floor centre'


def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    s = bpy.context.scene
    s.world = bpy.data.worlds.new('Neutral studio')
    s.world.use_nodes = True
    s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.30, .34, .39, 1)
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
    floor = material('STUDIO floor', (.76, .77, .76), 0, .86)
    box('STUDIO_Floor', (0, 0, -.04), (2000, 2000, .08), floor, None, 0)
    for name, position, power, size in (
        ('Key', (-7, -9, 12), 5400, 7), ('Fill', (8, -5, 8), 3600, 6),
        ('Rim', (1, 6, 11), 5600, 5)):
        bpy.ops.object.light_add(type='AREA', location=position)
        o = bpy.context.object
        o.name = 'STUDIO_' + name
        o.data.energy = power
        o.data.size = size
        aim(o, TARGET)
    bpy.ops.object.camera_add()
    s.camera = bpy.context.object
    s.camera.name = 'STUDIO_Camera'
    s.camera.data.type = 'ORTHO'
    s.camera.location = (11, -21, 8)
    s.camera.data.ortho_scale = 14.3
    aim(s.camera, TARGET)
    s.render.engine = 'CYCLES'
    s.cycles.samples = 32
    s.cycles.use_denoising = True
    s.cycles.seed = 0
    s.render.resolution_x = 1024
    s.render.resolution_y = 768
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.view_settings.view_transform = 'AgX'


def render_views():
    s = bpy.context.scene
    requested = next((arg.split('=', 1)[1].split(',') for arg in sys.argv if arg.startswith('--views=')), None)
    for name, position, scale in (
        ('hero', (11, -21, 8), 14.3), ('front', (0, -24, 6), 14.0),
        ('side', (24, 0, 4), 9.5), ('3q', (-15, -20, 8), 14.3)):
        if requested and name not in requested:
            continue
        s.camera.location = position
        s.camera.data.ortho_scale = scale
        aim(s.camera, TARGET)
        s.render.filepath = str(HERE / 'previews' / (name + '.png'))
        bpy.ops.render.render(write_still=True)


def export(path):
    root = bpy.data.objects[ROOT]
    copies = []
    for material_name, name in (
        ('Frame neutral mineral', 'FRAME_Structure'),
        ('Sign band warm white', 'SIGN_Band'), ('Trim graphite', 'TRIM_Details')):
        bpy.ops.object.select_all(action='DESELECT')
        group = []
        for o in list(root.children_recursive):
            if o.type == 'MESH' and o.data.materials[0].name == material_name:
                copy = o.copy()
                copy.data = o.data.copy()
                bpy.context.scene.collection.objects.link(copy)
                group.append(copy)
                copy.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        bpy.ops.object.join()
        o = bpy.context.object
        o.name = name
        o.data.name = name
        copies.append(o)
    try:
        bpy.ops.object.select_all(action='DESELECT')
        root.select_set(True)
        bpy.data.objects['SIGN_TextAnchor'].select_set(True)
        for o in copies:
            o.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB',
            use_selection=True, export_apply=True, export_yup=True,
            export_animations=False, export_texcoords=False, export_extras=True,
            export_cameras=False, export_lights=False)
    finally:
        for o in copies:
            mesh = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(mesh)


def main():
    for d in ('sources', 'exports', 'previews', 'reports', 'metadata'):
        (HERE / d).mkdir(exist_ok=True)
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version = 0
        s = bpy.context.scene
        s.unit_settings.system = 'METRIC'
        s.unit_settings.scale_length = 1
        root = empty(ROOT)
        build(root)
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')), compress=True)
    export(HERE / 'exports' / 'optimized.glb')
    if '--skip-render' not in sys.argv:
        render_views()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

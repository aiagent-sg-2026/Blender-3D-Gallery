"""Original deterministic low circular platform. Blender 5.2.3; no external assets."""
from pathlib import Path
import json
import math
import sys

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'round-event-platform'
ROOT = 'ASSET_RoundEventPlatform'
SEGMENTS = 192
# Radius and height in metres, from the floor to the plain chamfered top.
PROFILE = [(3.985, 0), (3.992, .006), (3.992, .026),
           (4, .034), (4, .292), (3.992, .3)]
UV_SCALE = .0575


def material(name, rgb, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    linear = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                   for v in rgb) + (1,)
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = linear
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = 0
    mat.diffuse_color = linear
    return mat


def build():
    root = bpy.data.objects.new(ROOT, None)
    bpy.context.scene.collection.objects.link(root)
    root['units'] = 'metres'
    root['origin'] = 'floor centre'
    root['front_axis'] = 'Blender -Y / glTF +Z'
    root['up_axis'] = 'Blender +Z / glTF +Y'
    vertices = [(r * math.cos(2 * math.pi * i / SEGMENTS),
                 r * math.sin(2 * math.pi * i / SEGMENTS), z)
                for r, z in PROFILE for i in range(SEGMENTS)]
    bottom, top = len(vertices), len(vertices) + 1
    vertices.extend([(0, 0, 0), (0, 0, .3)])
    faces, uvs, slots, smooth = [], [], [], []
    distance = [0]
    for a, b in zip(PROFILE, PROFILE[1:]):
        distance.append(distance[-1] + math.dist(a, b))
    # Two half-circumference strips share the same metric UV scale as both caps.
    # All islands have padding and occupy distinct regions of a single UV atlas.
    for row in range(len(PROFILE) - 1):
        for i in range(SEGMENTS):
            j = (i + 1) % SEGMENTS
            a, b = row * SEGMENTS, (row + 1) * SEGMENTS
            faces.append((a + i, a + j, b + j, b + i))
            half, column = divmod(i, SEGMENTS // 2)
            u0 = .05 + column * 2 * math.pi * 4 / SEGMENTS * UV_SCALE
            u1 = .05 + (column + 1) * 2 * math.pi * 4 / SEGMENTS * UV_SCALE
            v0 = .12 + half * .14 + distance[row] * UV_SCALE
            v1 = .12 + half * .14 + distance[row + 1] * UV_SCALE
            uvs.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
            slots.append(2 if row < 2 else 0 if row == 4 else 1)
            smooth.append(True)
    for is_top, centre, ring, uv_centre in [
            (False, bottom, 0, (.75, .72)),
            (True, top, (len(PROFILE) - 1) * SEGMENTS, (.25, .72))]:
        for i in range(SEGMENTS):
            j = (i + 1) % SEGMENTS
            face = (centre, ring + i, ring + j) if is_top else (centre, ring + j, ring + i)
            faces.append(face)
            uvs.append([(uv_centre[0] + vertices[k][0] * UV_SCALE,
                         uv_centre[1] + vertices[k][1] * UV_SCALE) for k in face])
            slots.append(0 if is_top else 2)
            smooth.append(False)
    mesh = bpy.data.meshes.new('Platform_ClosedRadialSurface')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for polygon, coords, slot, shaded in zip(mesh.polygons, uvs, slots, smooth):
        polygon.material_index = slot
        polygon.use_smooth = shaded
        for loop, coord in zip(polygon.loop_indices, coords):
            uv.data[loop].uv = coord
    obj = bpy.data.objects.new('PLATFORM_Surface', mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    for mat in [material('Platform_Top', (.62, .63, .64), .82),
                material('Platform_Edge', (.47, .49, .51), .68),
                material('Platform_BaseTrim', (.27, .29, .31), .75)]:
        mesh.materials.append(mat)
    obj['material_roles'] = 'Top / Edge / BaseTrim; theme with scalar PBR factors'
    obj['uv_mapping'] = 'Planar caps; two side strips; nonoverlapping atlas; 0.0575 UV units/m'


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('STUDIO_World')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.16, .18, .21, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .55
    for name, location, energy, size in [
            ('Key', (-4, -6, 9), 2100, 6), ('Fill', (6, -2, 6), 1500, 5),
            ('Rim', (2, 5, 8), 2400, 5)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        obj = bpy.context.object
        obj.name = 'STUDIO_' + name
        obj.data.energy, obj.data.shape, obj.data.size = energy, 'DISK', size
        aim(obj, (0, 0, .15))
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
    floor = bpy.context.object
    floor.name = 'STUDIO_Floor'
    floor.data.materials.append(material('STUDIO_FloorMaterial', (.19, .21, .24), .9))
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.name = 'STUDIO_Camera'
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 9.7
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1000, 750
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'


def export(path):
    bpy.ops.object.select_all(action='DESELECT')
    root = bpy.data.objects[ROOT]
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format='GLB', use_selection=True,
        export_apply=True, export_yup=True, export_animations=False,
        export_texcoords=True, export_normals=True, export_extras=True,
        export_cameras=False, export_lights=False)


def render_views():
    scene = bpy.context.scene
    target = (0, 0, .15)
    for name, position in [('hero', (10, -14, 10)), ('front', (0, -18, .9)),
                           ('side', (18, 0, .9)), ('3q', (-12, -12, 6.8))]:
        # Low orthographic views use a clean world backdrop instead of a floor horizon.
        bpy.data.objects['STUDIO_Floor'].hide_render = name in ('front', 'side')
        scene.camera.location = position
        aim(scene.camera, target)
        scene.render.filepath = str(HERE / 'previews' / (name + '.png'))
        bpy.ops.render.render(write_still=True)


def main():
    for folder in ['sources', 'exports', 'previews', 'reports', 'metadata']:
        (HERE / folder).mkdir(exist_ok=True)
    if '--export-source' in sys.argv:
        bpy.ops.wm.open_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version = 0
        scene = bpy.context.scene
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 1
        build()
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')), compress=True)
    export(HERE / 'exports/optimized.glb')
    if '--skip-render' not in sys.argv:
        render_views()
    (HERE / 'reports/generation.json').write_text(json.dumps({
        'blender_version': bpy.app.version_string, 'segments': SEGMENTS,
        'profile_radius_height_m': PROFILE, 'uv_scale_per_m': UV_SCALE,
        'external_assets': [], 'seed': 'none; fixed analytic geometry'
    }, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

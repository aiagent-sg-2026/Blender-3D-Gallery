"""Original metric wall-mounted TV; deterministic Blender 5.2.3 geometry, no external assets."""
from pathlib import Path
import math
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'tv-wall-mounted'
ROOT = 'ASSET_TVWallMounted'
TARGET = (0, 0, 1.47)


def material(name, rgb, metallic=0, roughness=.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb) + (1,)
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    mat.diffuse_color = color
    return mat


def finish(obj, name, mat, root, bevel):
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = root
    if bevel:
        mod = obj.modifiers.new('Manufactured edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return obj


def box(name, location, dimensions, mat, root, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, root, min(bevel, min(dimensions) * .24))


def screw(name, location, mat, root):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=.004, depth=.002,
                                      location=location, rotation=(math.pi / 2, 0, 0))
    return finish(bpy.context.object, name, mat, root, .0004)


def combine(name, parts, root):
    # Bake edge modifiers before joining; keep each functional module editable.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        bpy.context.view_layer.objects.active = obj
        for mod in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    obj.parent = root
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return obj


def build_panel(root, graphite, glass):
    """Adapt the original tv-floor-stand panel dimensions and construction.

    Keep the same bezel, body, active screen and rear ventilation geometry.
    Only the blank screen material and functional mesh grouping change here.
    """
    housing = [box('Panel frame', (0, -.035, 1.47), (1.23, .048, .72),
                   graphite, root, .009),
               box('Rear electronics', (0, .003, 1.46), (.74, .038, .40),
                   graphite, root, .012)]
    dark = [box('Blank screen', (0, -.0605, 1.475), (1.194, .004, .671625),
                glass, root, .003)]
    for z in (1.32, 1.60):
        housing.append(box('Rear vent recess', (0, .0225, z), (.60, .002, .028),
                        graphite, root, .001))
        for index in range(20):
            housing.append(box('Rear vent rib', (-.285 + index * .03, .0245, z),
                               (.010, .004, .030), graphite, root, .001))
    combine('PANEL_Housing', housing, root)
    combine('SCREEN_StandbyPanel', dark, root)


def build(root):
    graphite = material('Graphite powder coat', (.15, .17, .19), .18, .38)
    satin = material('Satin aluminium', (.55, .59, .62), .75, .32)
    screen = material('Neutral dark standby glass', (.055, .065, .072), .08, .22)
    shader = screen.node_tree.nodes['Principled BSDF']
    shader.inputs['Emission Color'].default_value = (.009, .012, .014, 1)
    shader.inputs['Emission Strength'].default_value = .3
    build_panel(root, graphite, screen)
    # A separate editable fixed bracket; nominal VESA bolt centres 400 x 200 mm.
    mount = []
    for z in (1.37, 1.57):
        mount.append(box('Wall plate horizontal rail', (0, .0775, z),
                         (.50, .012, .036), satin, root, .002))
    for x in (-.232, .232):
        mount.append(box('Wall plate end link', (x, .0775, 1.47),
                         (.036, .012, .164), satin, root, .002))
    for x in (-.20, .20):
        mount.append(box('Panel attachment rail', (x, .0405, 1.47),
                         (.032, .035, .30), satin, root, .003))
        for z in (1.37, 1.57):
            mount.append(box('Bracket standoff', (x, .0555, z),
                             (.030, .040, .028), satin, root, .002))
            mount.append(screw('Panel mount fastener', (x, .0225, z), satin, root))
    bracket = combine('MOUNT_VESAWallBracket', mount, root)
    bracket['nominal_bolt_pattern_metres'] = [.4, .2]
    bracket['role'] = 'Separate fixed wall bracket; visual mounting geometry only'
    # Centre the full depth envelope above the origin; retain floor-stand height.
    for obj in root.children_recursive:
        obj.location.y -= .0105



def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Neutral studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.22, .25, .29, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
    floor = material('Studio floor only', (.65, .68, .70), 0, .8)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.005))
    bpy.context.object.name = 'STUDIO_Floor'
    bpy.context.object.data.materials.append(floor)
    for name, location, energy, size in [('Key', (-3, -4, 5), 600, 3),
                                         ('Fill', (4, -2, 3), 400, 3),
                                         ('Rim', (1, 3, 4), 700, 2)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        obj = bpy.context.object
        obj.name = 'STUDIO_' + name
        obj.data.energy = energy
        obj.data.shape = 'DISK'
        obj.data.size = size
        aim(obj, TARGET)
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.name = 'STUDIO_Camera'
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 1.65
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.camera.location = (2.2, -4.5, 2.25)
    aim(scene.camera, TARGET)


def export(path):
    bpy.ops.object.select_all(action='DESELECT')
    root = bpy.data.objects[ROOT]
    root.select_set(True)
    for obj in root.children_recursive:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True, export_animations=False,
                              export_texcoords=False, export_extras=True,
                              export_cameras=False, export_lights=False)


def render_views():
    scene = bpy.context.scene
    selected = next((set(arg.split('=', 1)[1].split(',')) for arg in sys.argv if arg.startswith('--views=')), None)
    if selected is not None:
        assert selected <= {'hero', 'front', 'side', '3q', 'rear'}, 'Unknown preview view'
    for name, location in [('hero', (2.2, -4.5, 2.25)), ('front', (0, -5, 1.47)),
                            ('side', (5, 0, 1.47)), ('3q', (-2.7, -4.5, 2.2)),
                            ('rear', (2.7, 4.5, 2.3))]:
        if selected is not None and name not in selected:
            continue
        scene.camera.location = location
        aim(scene.camera, TARGET)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(HERE / 'previews' / (name + '.png'))
        bpy.ops.render.render(write_still=True)
        scene.render.image_settings.file_format = 'WEBP'
        scene.render.image_settings.quality = 85
        bpy.data.images['Render Result'].save_render(str(HERE / 'previews' / (name + '.webp')), scene=scene)


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
        root = bpy.data.objects.new(ROOT, None)
        scene.collection.objects.link(root)
        root['units'] = 'metres'
        root['front_axis'] = 'Blender -Y / glTF +Z'
        root['origin'] = 'Floor centre below full TV and bracket envelope'
        root['wall_plane_gltf_z'] = -.073
        root['panel_centre_height_metres'] = 1.47
        root['scope'] = 'Static wall TV for S13 and S14; soft blank emissive screen; no video or load certification'
        build(root)
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')), compress=True)
    export(HERE / 'exports' / 'optimized.glb')
    if '--skip-render' not in sys.argv:
        render_views()


if __name__ == '__main__':
    main()

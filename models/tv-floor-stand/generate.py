"""Original metric floor TV; deterministic Blender 5.2.3 geometry, no external assets."""
from pathlib import Path
import math
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'tv-floor-stand'
ROOT = 'ASSET_TVFloorStand'
TARGET = (0, 0, .94)


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
    """Reusable 1.23 x 0.72 m blank panel; Blender front -Y, centre height 1.47 m.

    tv-wall-mounted was absent in the task baseline; this is original construction,
    not a claim of source reuse. The screen remains opaque and has no content.
    """
    housing = [box('Panel frame', (0, -.035, 1.47), (1.23, .048, .72),
                   graphite, root, .009),
               box('Rear electronics', (0, .003, 1.46), (.74, .038, .40),
                   graphite, root, .012)]
    dark = [box('Blank screen', (0, -.0605, 1.475), (1.194, .004, .671625),
                glass, root, .003)]
    for z in (1.32, 1.60):
        dark.append(box('Rear vent recess', (0, .0225, z), (.60, .002, .028),
                        glass, root, .001))
        for index in range(20):
            housing.append(box('Rear vent rib', (-.285 + index * .03, .0245, z),
                               (.010, .004, .030), graphite, root, .001))
    combine('PANEL_Housing', housing, root)
    combine('PANEL_GlassAndVentRecesses', dark, root)


def build(root):
    graphite = material('Graphite powder coat', (.15, .17, .19), .18, .38)
    satin = material('Satin aluminium', (.55, .59, .62), .75, .32)
    glass = material('Opaque unlit screen and recesses', (.035, .085, .11), .15, .19)
    build_panel(root, graphite, glass)
    base = [box('Weighted base', (0, 0, .0415), (.78, .52, .055), graphite, root, .020),
            box('Column socket', (0, .085, .099), (.14, .13, .065), graphite, root, .008),
            box('Cable exit grommet', (0, .19, .071), (.046, .030, .006), graphite, root, .003)]
    for x in (-.285, .285):
        for y in (-.17, .17):
            base.append(box('Floor pad', (x, y, .008), (.09, .08, .016), graphite, root, .006))
    combine('STAND_WeightedBaseAndPads', base, root)
    support = [box('Upright column', (0, .085, .794), (.075, .075, 1.452), satin, root, .006),
               box('Mount crossbar', (0, .037, 1.47), (.50, .040, .065), satin, root, .004)]
    for x in (-.19, .19):
        support.append(box('Panel attachment rail', (x, .027, 1.47),
                           (.035, .025, .28), satin, root, .003))
    combine('STAND_ColumnAndMount', support, root)
    cover = box('STAND_RearCableCover', (0, .134, .735), (.043, .024, 1.30),
                graphite, root, .004)
    combine('STAND_RearCableCover', [cover], root)
    fasteners = []
    for x in (-.19, .19):
        for z in (1.36, 1.58):
            fasteners.append(screw('Rear mount fastener', (x, .0405, z), satin, root))
    for z in (.15, 1.32):
        fasteners.append(screw('Cable cover fastener', (0, .147, z), satin, root))
    combine('DETAILS_Fasteners', fasteners, root)


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
    scene.camera.data.ortho_scale = 2.25
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.camera.location = (2.7, -4.5, 2.5)
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
    for name, location in [('hero', (2.7, -4.5, 2.5)), ('front', (0, -5, 1.24)),
                            ('side', (5, 0, 1.24)), ('3q', (-2.7, -4.5, 2.2)),
                            ('rear', (2.7, 4.5, 2.5))]:
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
        root['origin'] = 'Floor centre of base footprint'
        root['scope'] = 'Static visual prop; no video, electronics, stability or load certification'
        build(root)
        studio()
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'sources' / (SLUG + '.blend')), compress=True)
    export(HERE / 'exports' / 'optimized.glb')
    if '--skip-render' not in sys.argv:
        render_views()


if __name__ == '__main__':
    main()

"""Original deterministic TV experience table. Blender 5.2.3; no external assets."""
from pathlib import Path
import sys
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'tv-demo-table'
ROOT = 'ASSET_TVDemoTable'
TARGET = (0, 0, .69)


def material(name, rgb, metallic=0, roughness=.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb) + (1,)
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    mat.diffuse_color = color
    return mat


def box(name, location, dimensions, mat, root, bevel=.003):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj.parent = root
    if bevel:
        mod = obj.modifiers.new('Manufactured edge', 'BEVEL')
        mod.width = min(bevel, min(dimensions) * .24)
        mod.segments = 2
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return obj


def build(root):
    ivory = material('Warm mineral laminate', (.84, .83, .78), 0, .43)
    graphite = material('Graphite powder coat', (.17, .19, .21), .16, .38)
    screen = material('Opaque blue grey screen', (.085, .17, .205), .12, .22)
    box('TABLE_Top', (0, 0, .776), (2, 1, .048), ivory, root, .012)
    box('TABLE_EdgeStrip', (0, 0, .744), (1.986, .986, .016), graphite, root, .004)
    box('SHELF_Lower', (0, 0, .235), (1.76, .76, .034), ivory, root, .008)
    for x in (-.87, .87):
        for y in (-.37, .37):
            side = ('Left' if x < 0 else 'Right') + ('Front' if y < 0 else 'Rear')
            box('FRAME_Leg_' + side, (x, y, .394), (.055, .055, .716), graphite, root, .004)
            box('FRAME_Foot_' + side, (x, y, .018), (.072, .072, .036), graphite, root, .005)
        box('FRAME_SideRail_' + str(x), (x, 0, .705), (.045, .74, .068), graphite, root)
        box('SHELF_Support_' + str(x), (x, 0, .207), (.046, .75, .022), graphite, root)
    for y in (-.37, .37):
        box('FRAME_LongRail_' + str(y), (0, y, .709), (1.74, .038, .060), graphite, root)
    box('CABLE_RearTrough', (0, .32, .694), (1.62, .11, .045), graphite, root, .005)
    box('CABLE_RearUprightCover', (.87, .407, .46), (.035, .018, .44), graphite, root)
    # Three original small 16:9 screens; the centre screen is slightly raised.
    for label, x, width, height, bottom in [('Left', -.65, .57, .350, .955),
                                          ('Centre', 0, .62, .380, .985),
                                          ('Right', .65, .57, .350, .955)]:
        y = .13
        z = bottom + height / 2
        box('TV_' + label + '_Base', (x, y, .811), (.265, .22, .022), graphite, root, .009)
        box('TV_' + label + '_Riser', (x, y + .022, (.82 + bottom + .075) / 2),
            (.036, .038, bottom + .075 - .82), graphite, root, .003)
        box('TV_' + label + '_Housing', (x, y, z), (width, .034, height), graphite, root, .007)
        box('TV_' + label + '_RearPod', (x, y + .024, z - .025),
            (width * .58, .025, height * .5), graphite, root, .006)
        inner_width = width - .028
        box('TV_' + label + '_Screen', (x, y - .0185, z + .003),
            (inner_width, .004, inner_width * 9 / 16), screen, root, .002)
        # Sparse rear cooling ribs and a covered cable route add believable depth.
        for index in range(7):
            box('TV_' + label + '_Vent_' + str(index),
                (x - .09 + index * .03, y + .0375, z + .035),
                (.012, .003, .035), graphite, root, .0006)
        box('TV_' + label + '_CableCover', (x, y + .045, (.822 + z - .03) / 2),
            (.012, .012, z - .03 - .822), graphite, root, .002)
    box('SIGN_Base', (0, -.33, .806), (.25, .12, .012), graphite, root, .004)
    box('SIGN_Post', (0, -.30, .858), (.018, .018, .104), graphite, root, .002)
    box('SIGN_Frame', (0, -.315, .934), (.244, .020, .152), graphite, root, .004)
    box('SIGN_BlankCard', (0, -.326, .934), (.224, .004, .132), ivory, root, .001)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Neutral studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.22, .25, .29, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
    floor_mat = material('Studio floor only', (.64, .67, .69), 0, .8)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.004))
    bpy.context.object.name = 'STUDIO_Floor'
    bpy.context.object.data.materials.append(floor_mat)
    for name, location, energy, size in [('Key', (-3, -4, 5), 650, 3),
                                         ('Fill', (4, -2, 3), 400, 3),
                                         ('Rim', (1, 3, 4), 650, 2)]:
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
    scene.camera.data.ortho_scale = 2.65
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.camera.location = (3, -4.7, 2.8)
    aim(scene.camera, TARGET)


def export(path):
    """Bake saved source edits and batch by material only in the exported copy."""
    root = bpy.data.objects[ROOT]
    original_name = root.name
    root.name = 'SOURCE_TVDemoTable'
    export_root = bpy.data.objects.new(ROOT, None)
    bpy.context.scene.collection.objects.link(export_root)
    for key in root.keys():
        export_root[key] = root[key]
    try:
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        groups = {}
        for obj in sorted(root.children_recursive, key=lambda part: part.name):
            if obj.type != 'MESH':
                continue
            mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(graph))
            mesh.transform(root.matrix_world.inverted() @ obj.matrix_world)
            copy = bpy.data.objects.new('EXPORT_' + obj.name, mesh)
            bpy.context.scene.collection.objects.link(copy)
            copy.parent = export_root
            groups.setdefault(obj.data.materials[0].name, []).append(copy)
        for index, (name, parts) in enumerate(sorted(groups.items())):
            bpy.ops.object.select_all(action='DESELECT')
            for part in parts:
                part.select_set(True)
            bpy.context.view_layer.objects.active = parts[0]
            bpy.ops.object.join()
            parts[0].name = ['BATCH_Graphite', 'BATCH_Screens', 'BATCH_Laminate'][index]
        bpy.ops.object.select_all(action='DESELECT')
        export_root.select_set(True)
        for obj in export_root.children_recursive:
            obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                                  export_apply=True, export_yup=True, export_animations=False,
                                  export_texcoords=False, export_extras=True,
                                  export_cameras=False, export_lights=False)
    finally:
        for obj in list(export_root.children_recursive):
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        bpy.data.objects.remove(export_root, do_unlink=True)
        root.name = original_name


def render_views():
    scene = bpy.context.scene
    selected = next((set(arg.split('=', 1)[1].split(',')) for arg in sys.argv if arg.startswith('--views=')), None)
    views = [('hero', (3, -4.7, 2.8)), ('front', (0, -5, .69)),
             ('side', (5, 0, .69)), ('3q', (-3, -4.7, 2.4)), ('rear', (3, 4.7, 2.8))]
    if selected is not None:
        assert selected <= {name for name, _ in views}, 'Unknown preview view'
    for name, location in views:
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
        root['origin'] = 'Floor centre of table footprint'
        root['screen_count'] = 3
        root['scope'] = 'Static visual prop; no video or electrical operation'
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

"""Original deterministic cordless phone retail display. Blender 5.2.3; no assets."""
from pathlib import Path
import math
import sys
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
SLUG = 'cordless-phone-display'
ROOT = 'ASSET_CordlessPhoneDisplay'
TARGET = (0, 0, .145)
HANDSET = Matrix.Translation(Vector((-.052, .012, .176))) @ Matrix.Rotation(math.radians(-10), 4, 'X')


def material(name, rgb, roughness=.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb) + (1,)
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = roughness
    mat.diffuse_color = color
    return mat


def finish(obj, name, mat, root, bevel, segments=3, handset=False):
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = root
    if bevel:
        mod = obj.modifiers.new('Manufactured edge', 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    if handset:
        obj.matrix_world = HANDSET @ Matrix.LocRotScale(obj.location, obj.rotation_euler.to_quaternion(), obj.scale)
    return obj


def box(name, location, dimensions, mat, root, bevel=.001, segments=3, handset=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, root, min(bevel, min(dimensions) * .49), segments, handset)


def disc(name, location, radius, depth, mat, root, front=False, handset=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    if front:
        obj.rotation_euler.x = math.pi / 2
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return finish(obj, name, mat, root, min(.0006, depth * .2), 2, handset)


def face_plate(name, location, width, height, depth, radius, mat, root):
    # A thin rounded rectangle with real corner radii independent of thickness.
    outline = []
    for cx, cz, start in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
        for step in range(6):
            angle = math.radians(start + step * 18)
            outline.append((cx * (width / 2 - radius) + radius * math.cos(angle),
                            cz * (height / 2 - radius) + radius * math.sin(angle)))
    count = len(outline)
    verts = [(x, y, z) for y in (-depth / 2, depth / 2) for x, z in outline]
    faces = [tuple(range(count)), tuple(reversed(range(count, count * 2)))]
    for i in range(count):
        j = (i + 1) % count
        faces.append((i, i + count, j + count, j))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    return finish(obj, name, mat, root, 0, handset=True)


def numeral(number, x, z, mat, root):
    # Original seven-segment key legends: geometry only, no fonts or textures.
    patterns = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
                '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    for segment in patterns[str(number)]:
        if segment in 'agd':
            offset = {'a': .0017, 'g': 0, 'd': -.0017}[segment]
            box(f'LEGEND_{number}_{segment}', (x, -.0221, z + offset),
                (.0016, .00015, .00035), mat, root, 0, handset=True)
        else:
            xx = .00095 if segment in 'bc' else -.00095
            zz = .00085 if segment in 'bf' else -.00085
            box(f'LEGEND_{number}_{segment}', (x + xx, -.0221, z + zz),
                (.00035, .00015, .00135), mat, root, 0, handset=True)


def build(root):
    ivory = material('Warm mineral', (.84, .83, .78), .43)
    graphite = material('Graphite', (.17, .19, .21), .38)
    lcd = material('Muted sage LCD', (.39, .57, .51), .28)
    # Low, chamfered counter-top display plinth; root datum is its floor centre.
    box('PLINTH_ShadowFoot', (0, 0, .003), (.282, .202, .006), graphite, root, .002)
    box('PLINTH_Body', (0, 0, .025), (.300, .220, .044), ivory, root, .005)
    box('PLINTH_TopInlay', (0, 0, .0475), (.282, .202, .001), graphite, root, .0003)
    # Base meets the plinth. Raised cradle cheeks wrap the handset heel.
    box('BASE_Lower', (-.052, .014, .056), (.118, .132, .016), graphite, root, .006)
    box('BASE_Upper', (-.052, .014, .071), (.114, .128, .022), ivory, root, .009, 4)
    box('CRADLE_Well', (-.052, .004, .0835), (.067, .056, .007), graphite, root, .001)
    for label, x in [('Left', -.090), ('Right', -.014)]:
        box('CRADLE_' + label, (x, .014, .088), (.014, .067, .027), ivory, root, .006)
    box('CRADLE_RearRest', (-.052, .022, .097), (.063, .018, .034), ivory, root, .005)
    disc('BASE_PageButton', (-.052, -.031, .0835), .006, .003, graphite, root)
    box('BASE_ChargeIndicator', (-.052, -.0504, .070), (.009, .0012, .002), lcd, root, .0005)
    # Rear phone-line and power sockets are unlabelled recess representations.
    box('BASE_PhoneSocket', (-.074, .0783, .065), (.012, .0015, .008), graphite, root, .0004)
    box('BASE_PowerSocket', (-.035, .0783, .065), (.007, .0015, .007), graphite, root, .001)
    # A seated, slightly rear-leaning handset: all detail uses one rigid transform.
    box('HANDSET_Seam', (0, 0, 0), (.058, .027, .182), graphite, root, .012, 5, True)
    box('HANDSET_RearShell', (0, .005, 0), (.057, .021, .181), ivory, root, .010, 5, True)
    box('HANDSET_FrontShell', (0, -.006, 0), (.058, .024, .184), ivory, root, .011, 5, True)
    face_plate('HANDSET_FaceInset', (0, -.0179, -.001), .047, .155, .002, .008, graphite, root)
    box('SCREEN_Recess', (0, -.0191, .044), (.042, .002, .039), graphite, root, .0008, 3, True)
    face_plate('SCREEN_BlankLCD', (0, -.0203, .044), .037, .032, .001, .0025, lcd, root)
    for index in range(3):
        box('EARPIECE_Slot_' + str(index), (0, -.0192, .065 + index * .0033),
            (.022 - index * .003, .001, .0014), ivory, root, .0006, 3, True)
    disc('CONTROL_NavigationRim', (0, -.0204, .010), .0105, .003, ivory, root, True, True)
    disc('CONTROL_NavigationCentre', (0, -.0221, .010), .0055, .001, graphite, root, True, True)
    for label, x in [('Left', -.0175), ('Right', .0175)]:
        box('CONTROL_' + label, (x, -.0204, .010), (.007, .003, .010), ivory, root, .0013, 3, True)
    for row in range(4):
        for col in range(3):
            x, z = (col - 1) * .014, -.013 - row * .013
            key = str(1 + row * 3 + col) if row < 3 else ['Star', '0', 'Hash'][col]
            box('KEYPAD_Key_' + key, (x, -.0204, z), (.011, .0032, .009), ivory, root, .0015, 3, True)
            if key.isdigit():
                numeral(int(key), x, z, graphite, root)
            elif key == 'Star':
                for angle in (0, math.pi / 3, -math.pi / 3):
                    obj = box('LEGEND_Star', (x, -.0221, z), (.0034, .00015, .0004), graphite, root, 0)
                    obj.rotation_euler.y = angle
                    obj.matrix_world = HANDSET @ Matrix.LocRotScale(obj.location, obj.rotation_euler.to_quaternion(), obj.scale)
            else:
                for dx in (-.0008, .0008):
                    box('LEGEND_HashVertical', (x + dx, -.0221, z), (.00035, .00015, .0038), graphite, root, 0, handset=True)
                for dz in (-.0008, .0008):
                    box('LEGEND_HashHorizontal', (x, -.0221, z + dz), (.0033, .00015, .00035), graphite, root, 0, handset=True)
    for x in (-.003, 0, .003):
        disc('MICROPHONE_Perforation', (x, -.0192, -.069), .0007, .0006, ivory, root, True, True)
    disc('ANTENNA_Collar', (.018, .003, .091), .005, .007, graphite, root, handset=True)
    disc('ANTENNA_Stub', (.018, .003, .105), .0036, .023, graphite, root, handset=True)
    # Empty price-card holder sits beside the phone and faces the same aisle.
    box('PRICE_HolderFoot', (.088, -.039, .050), (.086, .055, .004), graphite, root, .0017)
    box('PRICE_Stem', (.088, -.027, .072), (.008, .008, .042), graphite, root, .002)
    box('PRICE_Frame', (.088, -.031, .112), (.082, .008, .053), graphite, root, .002)
    box('PRICE_BlankCard', (.088, -.0356, .112), (.074, .0014, .045), ivory, root, .0006)
    box('PRICE_LowerLip', (.088, -.037, .0865), (.083, .006, .003), graphite, root, .001)


def aim(obj, target=TARGET):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Neutral studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.22, .25, .29, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.0005))
    bpy.context.object.name = 'STUDIO_Floor'
    bpy.context.object.data.materials.append(material('Studio floor only', (.64, .67, .69), .8))
    for name, location, energy, size in [('Key', (-.7, -.9, 1.2), 45, .75),
                                         ('Fill', (.8, -.4, .6), 25, .6),
                                         ('Rim', (.1, .7, .9), 45, .5)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        obj = bpy.context.object
        obj.name = 'STUDIO_' + name
        obj.data.energy = energy
        obj.data.shape = 'DISK'
        obj.data.size = size
        aim(obj)
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.name = 'STUDIO_Camera'
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = .405
    scene.camera.location = (.48, -.85, .50)
    aim(scene.camera)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 48
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'


def export(path):
    """Bake saved source edits and batch by shared material in a temporary copy."""
    root = bpy.data.objects[ROOT]
    root.name = 'SOURCE_CordlessPhoneDisplay'
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
        for name, parts in sorted(groups.items()):
            bpy.ops.object.select_all(action='DESELECT')
            for part in parts:
                part.select_set(True)
            bpy.context.view_layer.objects.active = parts[0]
            bpy.ops.object.join()
            parts[0].name = 'BATCH_' + {'Graphite': 'Graphite', 'Muted sage LCD': 'LCD', 'Warm mineral': 'Mineral'}[name]
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
        root.name = ROOT


def render_views():
    scene = bpy.context.scene
    views = [('hero', (.48, -.85, .50)), ('front', (0, -.9, .145)),
             ('side', (.9, 0, .145)), ('3q', (-.48, -.85, .44))]
    for name, location in views:
        scene.camera.location = location
        aim(scene.camera)
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
        root['origin'] = 'Floor centre of plinth footprint'
        root['scope'] = 'Static cordless landline retail display; no electronic operation'
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

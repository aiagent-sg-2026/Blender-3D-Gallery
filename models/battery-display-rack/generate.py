"""Original deterministic retail battery rack. Blender 5.2.3; no external assets."""
from pathlib import Path
import math
import sys
import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SLUG = 'battery-display-rack'
ROOT = 'ASSET_BatteryDisplayRack'
TARGET = (0, 0, 1.0)
IVORY = (.81, .82, .78)
GRAPHITE = (.16, .20, .22)
TEAL = (.22, .49, .48)
ORANGE = (.83, .45, .23)
VIOLET = (.51, .45, .61)
SILVER = (.69, .73, .75)


def linear(rgb):
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb) + (1,)


def material(name, metallic=0, roughness=.48, alpha=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = True
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if alpha == 1:
        color = mat.node_tree.nodes.new('ShaderNodeVertexColor')
        color.layer_name = 'Color'
        mat.node_tree.links.new(color.outputs['Color'], shader.inputs['Base Color'])
    else:
        shader.inputs['Base Color'].default_value = (.72, .84, .88, 1)
        shader.inputs['Alpha'].default_value = alpha
        mat.surface_render_method = 'DITHERED'
    return mat


def finish(obj, name, mat, root, color=IVORY, bevel=0):
    obj.name = name
    obj.parent = root
    obj.data.materials.append(mat)
    if mat.name != 'Clear blister':
        attr = obj.data.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='CORNER')
        for entry in attr.data:
            entry.color = linear(color)
    if bevel:
        mod = obj.modifiers.new('Manufactured edge', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return obj


def box(name, location, dimensions, mat, root, color=IVORY, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, root, color, min(bevel, min(dimensions) * .2))


def cylinder(name, location, radius, depth, mat, root, color=SILVER, front=False, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    if front:
        obj.rotation_euler.x = math.pi / 2
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return finish(obj, name, mat, root, color)


def rod(name, a, b, radius, mat, root):
    a, b = Vector(a), Vector(b)
    obj = cylinder(name, (a + b) / 2, radius, (b - a).length, mat, root, vertices=8)
    obj.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return obj


def mesh_object(name, vertices, faces, location, mat, root, color):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.0000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    return finish(obj, name, mat, root, color)


def perforated_panel(name, location, width, height, thickness, columns, rows, radius, mat, root,
                     color=IVORY, hole_offset=0):
    # Eight-sided real through-holes. Adjacent cell boundaries share vertices.
    vertices, faces = [], []
    dx, dz = width / columns, height / rows
    for row in range(rows):
        for col in range(columns):
            cx = -width / 2 + (col + .5) * dx
            cz = -height / 2 + (row + .5) * dz
            outer = [(dx / 2, 0), (dx / 2, dz / 2), (0, dz / 2), (-dx / 2, dz / 2),
                     (-dx / 2, 0), (-dx / 2, -dz / 2), (0, -dz / 2), (dx / 2, -dz / 2)]
            inner = [(radius * math.cos(i * math.pi / 4),
                      hole_offset + radius * math.sin(i * math.pi / 4)) for i in range(8)]
            start = len(vertices)
            for y in (-thickness / 2, thickness / 2):
                vertices += [(cx + x, y, cz + z) for x, z in outer + inner]
            for i in range(8):
                j = (i + 1) % 8
                faces += [(start + i, start + j, start + 8 + j, start + 8 + i),
                          (start + 16 + i, start + 24 + i, start + 24 + j, start + 16 + j),
                          (start + 8 + i, start + 8 + j, start + 24 + j, start + 24 + i)]
                boundary = ((i in (0, 7) and col == columns - 1) or
                            (i in (1, 2) and row == rows - 1) or
                            (i in (3, 4) and col == 0) or
                            (i in (5, 6) and row == 0))
                if boundary:
                    faces.append((start + i, start + 16 + i, start + 16 + j, start + j))
    return mesh_object(name, vertices, faces, location, mat, root, color)


def blister(name, x, z, width, height, mat, root):
    # A closed, shallow chamfered vacuum-form bubble; no texture or transmission pass.
    vertices = []
    for y, inset in [(-.007, 0), (-.030, .005)]:
        w, h, r = width / 2 - inset, height / 2 - inset, .006
        outline = [(w, h - r), (w - r, h), (-w + r, h), (-w, h - r),
                   (-w, -h + r), (-w + r, -h), (w - r, -h), (w, -h + r)]
        vertices += [(xx, y, zz) for xx, zz in outline]
    faces = [tuple(range(8)), tuple(range(15, 7, -1))]
    faces += [(i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8) for i in range(8)]
    return mesh_object(name, vertices, faces, (x, 0, z), mat, root, IVORY)


def build(root):
    matte = material('Matte finish')
    metal = material('Satin metal', .72, .29)
    clear = material('Clear blister', 0, .16, .12)
    # Full-footprint base establishes an unambiguous floor-centred origin.
    box('FRAME_Platform', (0, 0, .050), (1.0, .50, .10), matte, root, GRAPHITE, .012)
    box('FRAME_UpperPlinth', (0, 0, .112), (.97, .47, .024), matte, root, IVORY, .004)
    for x in (-.461, .461):
        box('FRAME_Upright', (x, .145, 1.045), (.045, .050, 1.91), matte, root, GRAPHITE, .004)
        box('FRAME_EndCap', (x, .145, 1.998), (.046, .051, .004), matte, root, GRAPHITE, .0005)
    for z in (.606, 1.793):
        box('FRAME_CrossRail', (0, .145, z), (.90, .040, .035), matte, root, GRAPHITE, .003)
    perforated_panel('PEGBOARD_ThroughHoles', (0, .111, 1.194), .864, 1.152, .006,
                     12, 16, .006, matte, root)
    box('HEADER_Surround', (0, .118, 1.897), (.900, .074, .194), matte, root, GRAPHITE, .008)
    box('HEADER_BlankPanel', (0, .078, 1.897), (.852, .008, .147), matte, root, TEAL, .0015)
    # Two open storage bins: raised front lips, shared back, visible divider.
    box('BINS_Floor', (0, -.031, .145), (.900, .386, .030), matte, root, GRAPHITE, .003)
    box('BINS_Rear', (0, .155, .343), (.900, .016, .397), matte, root, IVORY, .002)
    for x in (-.45, 0, .45):
        box('BINS_Divider', (x, -.031, .338), (.016, .386, .385), matte, root, IVORY, .002)
    box('BINS_FrontLip', (0, -.217, .228), (.916, .016, .165), matte, root, TEAL, .002)
    box('BINS_LipRail', (0, -.227, .313), (.916, .018, .018), matte, root, GRAPHITE, .002)
    for x in (-.225, .225):
        box('BINS_BlankLabel', (x, -.227, .251), (.108, .002, .032), matte, root, IVORY, .0003)
    # Four hanging rows. Colour and actual cell silhouettes separate AA/AAA/button packs.
    for row in range(4):
        z = .790 + row * .270
        for col in range(5):
            x = (col - 2) * .171
            kind = 'AA' if col < 2 else ('AAA' if col < 4 else 'Button')
            color = ORANGE if kind == 'AA' else (TEAL if kind == 'AAA' else VIOLET)
            suffix = f'{kind}_{row}_{col}'
            perforated_panel('CARD_' + suffix, (x, -.005, z), .140, .206, .003,
                             1, 1, .0045, matte, root, color, .084)
            box('CARD_BlankBand_' + suffix, (x, -.0068, z + .044), (.116, .0005, .018),
                matte, root, IVORY, 0)
            box('CARD_BlankTab_' + suffix, (x, -.0068, z - .079), (.048, .0005, .008),
                matte, root, IVORY, 0)
            # Mount through the card's punched hang hole. The rear end meets the board.
            rod('HOOK_Pin_' + suffix, (x, .113, z + .084), (x, -.026, z + .084), .0017, metal, root)
            rod('HOOK_Tip_' + suffix, (x, -.026, z + .084), (x, -.026, z + .091), .0017, metal, root)
            cylinder('HOOK_Rosette_' + suffix, (x, .106, z + .084), .006, .004, metal, root,
                     front=True, vertices=8)
            if kind in ('AA', 'AAA'):
                radius, length = (.00725, .0505) if kind == 'AA' else (.00525, .0445)
                for cell in range(4):
                    xx = x + (cell - 1.5) * .0185
                    obj = cylinder('CELL_' + suffix + '_' + str(cell), (xx, -.015, z - .022),
                                   radius, length, metal, root)
                    # A generic dark sleeve is vertex colour on the existing cylinder sides.
                    attr = obj.data.color_attributes['Color']
                    for face in obj.data.polygons:
                        if len(face.vertices) == 4:
                            for loop in face.loop_indices:
                                attr.data[loop].color = linear(GRAPHITE)
                    cylinder('CELL_Positive_' + suffix + '_' + str(cell),
                             (xx, -.015, z - .022 + length / 2 + .0006), radius * .43,
                             .0012, metal, root, vertices=8)
                blister('BLISTER_' + suffix, x, z - .021, .090, .075, clear, root)
            else:
                for cell in range(2):
                    cylinder('CELL_' + suffix + '_' + str(cell),
                             (x + (cell - .5) * .031, -.010, z - .022), .010,
                             .0032, metal, root, front=True, vertices=16)
                blister('BLISTER_' + suffix, x, z - .022, .075, .045, clear, root)


def aim(obj):
    obj.rotation_euler = (Vector(TARGET) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def studio():
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Neutral studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.22, .25, .29, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.001))
    bpy.context.object.name = 'STUDIO_Floor'
    floor = bpy.data.materials.new('Studio floor only')
    floor.diffuse_color = (.34, .38, .41, 1)
    bpy.context.object.data.materials.append(floor)
    for name, location, energy, size in [('Key', (-3, -4, 5), 950, 4),
                                         ('Fill', (4, -2, 3), 650, 3),
                                         ('Rim', (1, 3, 4), 1050, 3)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        obj = bpy.context.object
        obj.name = 'STUDIO_' + name
        obj.data.energy = energy
        obj.data.size = size
        aim(obj)
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.name = 'STUDIO_Camera'
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = 2.60
    scene.camera.location = (3, -5, 2.65)
    aim(scene.camera)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 40
    scene.cycles.seed = 0
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'


def export(path):
    """Bake evaluated source parts into three temporary batches, preserving the source."""
    root = bpy.data.objects[ROOT]
    root.name = 'SOURCE_BatteryDisplayRack'
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
            mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(graph), preserve_all_data_layers=True,
                                                    depsgraph=graph)
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
            parts[0].name = 'BATCH_' + name.replace(' ', '')
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
    for name, location in [('hero', (3, -5, 2.65)), ('front', (0, -6, 1.0)),
                           ('side', (6, 0, 1.3)), ('3q', (-3, -5, 2.4))]:
        scene.camera.location = location
        aim(scene.camera)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(HERE / 'previews' / (name + '.png'))
        bpy.ops.render.render(write_still=True)
        scene.render.image_settings.file_format = 'WEBP'
        scene.render.image_settings.quality = 88
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
        root['scope'] = 'Static unbranded battery display rack; S16 / P1'
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

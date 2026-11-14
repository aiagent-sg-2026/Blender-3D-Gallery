"""Fit real modules to the frozen Foundation footprint. Never edits input assets."""
from pathlib import Path
import bpy
import hashlib
import json
import math
import os
import tempfile
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCES = {
    'floor': 'models/mall-floor-tile/exports/mall-floor-tile-module.glb',
    'ceiling': 'models/mall-ceiling-panel/exports/mall-ceiling-panel-module.glb',
    'column': 'models/mall-structural-column/exports/mall-structural-column.glb',
    'partition': 'models/mall-glass-partition/exports/mall-glass-partition.glb',
    'door': 'models/mall-shopfront-door/exports/mall-shopfront-door.glb',
    'fascia210': 'models/mall-fit-finishes/exports/mall-shopfront-fascia-210.glb',
    'collar': 'models/mall-fit-finishes/exports/mall-column-ceiling-collar.glb',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    assert not path.is_symlink() and (not path.exists() or path.is_file())
    fd, tmp = tempfile.mkstemp(prefix='.report-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(value, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def export(path, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True,
                              export_apply=True, export_extras=True, export_animations=False)


# Adapt the saved source by moving rail ends and side rails, preserving rail
# sections, thicknesses and materials. Object scaling is not used to conceal a gap.
fascia_source = ROOT / 'models/mall-fit-finishes/sources/mall-shopfront-fascia-120.blend'
bpy.ops.wm.open_mainfile(filepath=str(fascia_source))
fascia_root = bpy.data.objects['ASSET_mall_shopfront_fascia_120']
fascia_objects = set([fascia_root, *fascia_root.children_recursive])
for obj in list(bpy.data.objects):
    if obj not in fascia_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
delta = (3.48 - 1.2) / 2
for obj in fascia_objects:
    if obj.name == 'FRAME_Left':
        obj.location.x -= delta
    elif obj.name == 'FRAME_Right':
        obj.location.x += delta
    elif obj.type == 'MESH':
        obj.data = obj.data.copy()
        for vertex in obj.data.vertices:
            vertex.co.x += delta if vertex.co.x > 0 else -delta
    elif obj.name in ('CONNECTOR_Left', 'CONNECTOR_Right'):
        obj.location.x = -1.74 if obj.name.endswith('Left') else 1.74
fascia_root.name = 'ASSET_foundation_fascia_run_348'
fascia_root['width_m'] = 3.48
fascia_root['adaptation'] = '3 shared-post partition bays: 1.20 + 1.14 + 1.14 m'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'sources/fascia-run-348.blend'), compress=True)
export(HERE / 'exports/fascia-run-348.glb', fascia_objects)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
SOURCES['fascia348'] = str((HERE / 'exports/fascia-run-348.glb').relative_to(ROOT))
base = json.loads((HERE.parent / 'whitebox/layout.json').read_text())
cache, records = {}, []


def add(kind, name, position, rotation=0, remove_left_post=False):
    if kind not in cache:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(ROOT / SOURCES[kind]))
        objects = list(set(bpy.data.objects) - before)
        # Cache unparented templates; all assembled instances are copies.
        cache[kind] = objects
    originals = cache[kind]
    copies = {obj: obj.copy() for obj in originals}
    for obj, copy in copies.items():
        scene.collection.objects.link(copy)
        copy.parent = copies.get(obj.parent)
    objects = list(copies.values())
    if remove_left_post:
        post = next(obj for obj in objects if obj.name.startswith('POST_Left'))
        objects.remove(post)
        bpy.data.objects.remove(post, do_unlink=True)
    wrapper = bpy.data.objects.new(name, None)
    scene.collection.objects.link(wrapper)
    wrapper.location = position
    wrapper.rotation_euler.z = rotation
    wrapper['kind'] = kind
    for obj in objects:
        if obj.parent not in objects:
            obj.parent = wrapper
    bpy.context.view_layer.update()
    points = [obj.matrix_world @ Vector(c) for obj in objects if obj.type == 'MESH' for c in obj.bound_box]
    records.append({'name': name, 'kind': kind, 'position_blender_m': list(position),
                    'rotation_z': rotation, 'removed_left_post': remove_left_post,
                    'min': [min(v[i] for v in points) for i in range(3)],
                    'max': [max(v[i] for v in points) for i in range(3)]})
    return wrapper


shell_mat = bpy.data.materials.new('Study shell ivory')
shell_mat.diffuse_color = (.65, .68, .63, 1)
shell_mat.use_nodes = True
shell_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = shell_mat.diffuse_color


def box(part):
    x, y, z = part['center']
    w, h, d = part['size']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -z, y))
    obj = bpy.context.object
    obj.name = 'Shell_' + part['id']
    obj.dimensions = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(shell_mat)
    obj['kind'] = part['kind']
    return obj


# Keep the approved footprint, room shells and fixture reservations. Replaced
# facade boxes must disappear from both rendering and the collision contract.
removed = {side + suffix for side in ('west', 'east')
           for suffix in ('_front_north', '_front_south', '_door_header')}
shell = [p for p in base['parts'] if p['id'] not in removed and not p['kind'].startswith('floor_')]
for part in shell:
    box(part)

cells = set()
for region in base['regions']:
    x1, x2, z1, z2 = region['bounds']
    for i in range(round((x2 - x1) / 1.2)):
        for j in range(round((z2 - z1) / 1.2)):
            cells.add((round(x1 + .6 + i * 1.2, 6), round(z1 + .6 + j * 1.2, 6)))
for i, (x, z) in enumerate(sorted(cells)):
    add('floor', f'Floor_{i:03}', (x, -z, -.03))
    if (x, z) != (-3.0, 13.8):
        add('ceiling', f'Ceiling_{i:03}', (x, -z, 3))
add('column', 'Column', (-3, -13.8, 0))
add('collar', 'Ceiling_Collar', (-3, -13.8, 3))

for label, x, rotation in [('A', -2.4, math.pi / 2), ('B', 2.4, -math.pi / 2)]:
    add('door', f'Door_{label}', (x, 0, 0), rotation)
    add('fascia210', f'Fascia_Door_{label}', (x, 0, 2.4), rotation)
    for run, offsets in [('Left', [-3.93, -2.79, -1.65]), ('Right', [1.65, 2.79, 3.93])]:
        for i, offset in enumerate(offsets):
            add('partition', f'Partition_{label}_{run}_{i}',
                (x, math.sin(rotation) * offset, 0), rotation, i > 0)
        add('fascia348', f'Fascia_Run_{label}_{run}',
            (x, math.sin(rotation) * offsets[1], 2.4), rotation)
    for sign in (-1, 1):
        # 4.53 m facade edge to 4.74 m inner face of the transverse shell wall.
        part = {'id': f'return_{label}_{sign}', 'center': [x, 1.5, sign * 4.635],
                'size': [.06, 3, .21], 'kind': 'wall', 'collision': True}
        shell.append(part)
        box(part)

# Remove import templates so no hidden/unplaced duplicate modules are exported.
for objects in cache.values():
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.view_layer.update()
asset_objects = list(scene.objects)
export(HERE / 'foundation-fitted.glb', asset_objects)

layout = {**base, 'version': '1.1-module-fit', 'parts':
          [p for p in base['parts'] if p['kind'].startswith('floor_')] + shell,
          'door_rough_opening_m': [2.1, 2.4], 'door_frame_aperture_m': [1.94, 2.32],
          'door_clear_width_m': 1.734, 'door_clear_height_m': 2.32,
          'partition_pitch_m': 1.14, 'partition_run_width_m': 3.48,
          'floorCells': sorted(cells), 'objects': records,
          'sources': {k: {'path': v, 'sha256': sha(ROOT / v)} for k, v in SOURCES.items()},
          'parent_layout_sha256': sha(HERE.parent / 'whitebox/layout.json'),
          'adaptation_source': {'path': str(fascia_source.relative_to(ROOT)), 'sha256': sha(fascia_source)}}
write_json(HERE / 'layout.json', layout)

scene.world = bpy.data.worlds.new('Module fit world')
scene.world.color = (.4, .4, .4)
for name, location, power in [('Key', (4, -12, 18), 7000), ('Fill', (-12, 5, 12), 5000)]:
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.size = 18
    light.rotation_euler = (Vector((0, -4, 0)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add(location=(26, -32, 31))
camera = bpy.context.object
camera.name = 'Module fit overview'
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 40
camera.rotation_euler = (Vector((0, -3.6, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE / 'foundation-fitted.blend'), compress=True)
ceilings = [obj for obj in scene.objects if obj.parent is None and obj.get('kind') in ('ceiling', 'collar')]
for root in ceilings:
    for obj in root.children_recursive:
        obj.hide_render = True
scene.render.filepath = str(HERE / 'overview.png')
bpy.ops.render.render(write_still=True)
for root in ceilings:
    for obj in root.children_recursive:
        obj.hide_render = False
# The saved source retains complete ceilings. Cutaway affects the image only.
write_json(HERE / 'reports/build.json', {
    'status': 'PASS', 'blender': bpy.app.version_string, 'instances': len(records),
    'floorCells': len(cells), 'partitionInstances': 12, 'sharedPostsRemoved': 8,
    'files': [{'path': p, 'bytes': (HERE / p).stat().st_size, 'sha256': sha(HERE / p)}
              for p in ['foundation-fitted.glb', 'foundation-fitted.blend', 'layout.json',
                        'sources/fascia-run-348.blend', 'exports/fascia-run-348.glb', 'overview.png']]})
print('MODULE_FIT_BUILT', len(records), 'instances;', len(cells), 'floor cells')

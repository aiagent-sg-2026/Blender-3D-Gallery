"""Create the editable Blender source, GLB and dimensioned SVG from layout.json.

Run in a separate Blender background process; never modifies the open UI scene.
"""
from pathlib import Path
from mathutils import Vector
import bpy
import hashlib
import json
import math
import os
import tempfile

HERE = Path(__file__).resolve().parent
OUT = HERE / 'whitebox'
LAYOUT = json.loads((OUT / 'layout.json').read_text())
COLORS = {
    'wall': '#e4e6e3', 'header': '#c4cdca', 'shelf': '#7e8a88',
    'fixture': '#53665e', 'floor_entrance': '#b7bebb',
    'floor_atrium': '#d4d8d0', 'floor_corridor': '#bcc8c4',
    'floor_newmoon': '#527c6a', 'floor_sample': '#c9b389',
}


def write_report(path, data):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('Unsafe report target')
    path.parent.mkdir(exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.report-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def linear_color(code):
    def linear(value):
        return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
    return tuple(linear(int(code[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1,)


def floor_plan():
    # Dimensions describe the planning grid; walls intrude 0.06 m on each side.
    elements = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1280">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#254d40"/></marker></defs>
<style>text{font-family:Arial,sans-serif;fill:#20362f} .title{font-size:30px;font-weight:bold}.sub{font-size:15px}.room{font-size:18px;font-weight:bold}.dim{stroke:#254d40;stroke-width:1.3;marker-start:url(#arrow);marker-end:url(#arrow)}.note{font-size:14px}</style>
<rect width="1000" height="1280" fill="#f6f5ee"/>
<text x="50" y="58" class="title">FOUNDATION V1 / ONE-FLOOR WHITEBOX</text>
<text x="50" y="88" class="sub">FND-002 · 1.2 m planning grid · metres · v1.0</text>
<text x="50" y="114" class="sub">Layout study, not a construction or statutory-compliance drawing.</text>''']
    px = lambda x: 500 + x * 25
    py = lambda z: 450 + z * 25

    def text(x, z, value, cls='sub'):
        elements.append(f'<text x="{px(x)}" y="{py(z)}" text-anchor="middle" class="{cls}">{value}</text>')

    def dimension(x1, z1, x2, z2, value, offset_x=0, offset_y=-7):
        elements.append(f'<line class="dim" x1="{px(x1)}" y1="{py(z1)}" x2="{px(x2)}" y2="{py(z2)}"/>')
        elements.append(f'<text x="{(px(x1)+px(x2))/2+offset_x}" y="{(py(z1)+py(z2))/2+offset_y}" text-anchor="middle" class="sub">{value}</text>')

    for region in LAYOUT['regions']:
        x1, x2, z1, z2 = region['bounds']
        elements.append(f'<rect x="{px(x1)}" y="{py(z1)}" width="{25*(x2-x1)}" height="{25*(z2-z1)}" fill="{COLORS["floor_"+region["id"]]}"/>')
    for part in LAYOUT['parts']:
        if part['kind'].startswith('floor_') or part['kind'] == 'header':
            continue
        x, _, z = part['center']
        w, _, d = part['size']
        color = '#293e35' if part['kind'] == 'wall' else COLORS[part['kind']]
        elements.append(f'<rect x="{px(x-w/2)}" y="{py(z-d/2)}" width="{w*25}" height="{d*25}" fill="{color}"/>')
    # Door headers are dashed to leave the floor opening visible.
    for x in (-2.4, 2.4):
        elements.append(f'<line x1="{px(x)}" x2="{px(x)}" y1="{py(-1.05)}" y2="{py(1.05)}" stroke="#254d40" stroke-width="2" stroke-dasharray="4 3"/>')
    route = ' '.join(f'{px(x)},{py(z)}' for x, z in [[0,18],[0,13],[0,0],[-6,0],[0,0],[6,0]])
    elements.append(f'<polyline points="{route}" fill="none" stroke="#fff5c3" stroke-width="9"/>')
    elements.append(f'<polyline points="{route}" fill="none" stroke="#254d40" stroke-width="2.5" stroke-dasharray="8 5"/>')
    elements.append(f'<circle cx="{px(0)}" cy="{py(18)}" r="7" fill="#20362f"/>')
    text(-6, -2.8, 'NEW MOON', 'room')
    text(-6, -1.8, '7.2 × 9.6 m')
    text(6, -2.8, 'SAMPLE STORE', 'room')
    text(6, -1.8, '7.2 × 9.6 m')
    text(0, 12.5, 'ATRIUM', 'room')
    text(0, 13.5, '9.6 × 7.2 m')
    text(0, 20.6, 'ENTRANCE / 4.8 × 2.4 m', 'room')
    dimension(-2.4,-9,2.4,-9,'4.8 m grid / 4.68 m clear')
    dimension(-9.6,-6.3,-2.4,-6.3,'7.2 m')
    dimension(2.4,-6.3,9.6,-6.3,'7.2 m')
    dimension(11.2,-12,11.2,9.6,'21.6 m',offset_x=44,offset_y=4)
    dimension(-2.4,-.9,-2.4,.9,'',offset_x=-15)
    elements.append('<path d="M100 240V165" stroke="#254d40" stroke-width="3" marker-end="url(#arrow)"/><text x="100" y="150" text-anchor="middle" class="room">N / −Z</text>')
    elements.extend([
        '<text x="50" y="1030" class="room">DIMENSION AND CIRCULATION CONTRACT</text>',
        '<text x="50" y="1060" class="note">Store doors: 2.10 m clear width × 2.40 m clear height. Entry opening: 2.40 m wide.</text>',
        '<text x="50" y="1085" class="note">Walls: 3.00 m high × 0.12 m thick. Floor top: Y = 0.00 m. No ceiling in this study.</text>',
        '<text x="50" y="1110" class="note">Room dimensions use wall centrelines. Store interiors: 7.08 × 9.48 m clear.</text>',
        '<text x="50" y="1135" class="note">Dashed route: entrance → atrium → New Moon → Sample Store → entrance, 60 m.</text>',
        '<text x="50" y="1160" class="note">Grey blocks: shelf / bench / directory / planter / bin proxies. No final asset-fit claim.</text>',
        '<text x="50" y="1185" class="note">Arrival has a 0.60 m low boundary: capsule stops; follow camera can look over it.</text>',
        '<text x="50" y="1220" class="sub">Authoritative coordinates: whitebox/layout.json · Three.js/glTF +Y up · Blender +Z up</text>',
        '</svg>',
    ])
    (OUT / 'floor-plan.svg').write_text('\n'.join(elements) + '\n')


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene['layout_version'] = LAYOUT['version']
scene['coordinate_mapping'] = 'Three (x,y,z) -> Blender (x,-z,y)'
scene['purpose'] = 'FND-002 spatial whitebox; no final fit-out or product acceptance'
materials = {}
for key, code in COLORS.items():
    material = bpy.data.materials.new(key)
    material.diffuse_color = linear_color(code)
    material.use_nodes = True
    material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = material.diffuse_color
    material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .85
    materials[key] = material

meshes = []
for part in LAYOUT['parts']:
    x, y, z = part['center']
    w, h, d = part['size']
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -z, y))
    obj = bpy.context.object
    obj.name = part['id']
    obj.dimensions = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(materials[part['kind']])
    obj['layout_id'] = part['id']
    obj['collision'] = part['collision']
    obj['role'] = part['kind']
    meshes.append(obj)

bpy.ops.object.select_all(action='DESELECT')
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.export_scene.gltf(filepath=str(OUT / 'foundation-v1.glb'), export_format='GLB',
                          use_selection=True, export_extras=True, export_yup=True)

# Cameras and lights remain editable in the .blend but are omitted from the GLB.
bpy.ops.object.camera_add(location=(27, -34, 34))
camera = bpy.context.object
camera.name = 'Whitebox overview camera'
camera.rotation_euler = (Vector((0, -3.6, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 39
camera.data.lens = 40
scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(0, -4, 22))
light = bpy.context.object
light.data.energy = 6500
light.data.shape = 'DISK'
light.data.size = 24
scene.world = bpy.data.worlds.new('Whitebox world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.75, .8, .76, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .7
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.render.resolution_x = 1400
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(OUT / 'overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'foundation-v1.blend'))
bpy.ops.render.render(write_still=True)
floor_plan()
receipt = {
    'status': 'PASS', 'blender_version': bpy.app.version_string,
    'layout_sha256': hashlib.sha256((OUT / 'layout.json').read_bytes()).hexdigest(),
    'parts': len(meshes), 'triangles': sum(len(obj.data.polygons) * 2 for obj in meshes),
    'coordinate_mapping': 'Three (x,y,z) -> Blender (x,-z,y)',
    'units': 'metres', 'files': [],
}
for filename in ['foundation-v1.blend', 'foundation-v1.glb', 'floor-plan.svg', 'overview.png']:
    path = OUT / filename
    receipt['files'].append({'path': 'whitebox/' + filename, 'bytes': path.stat().st_size,
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
write_report(HERE / 'reports' / 'geometry-build.json', receipt)
print('Built editable whitebox:', receipt['parts'], 'parts,', receipt['triangles'], 'triangles')

"""Inspect and render ONE source root or ONE imported GLB without saving it.

blender --background --disable-autoexec scene.blend --python this.py -- \
    --root ASSET_Table --output /absolute/evidence/before
Use --glb /absolute/model.glb instead of opening a .blend for re-import QA.
"""
import argparse
import bmesh
import bpy
import json
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--root', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--glb')
parser.add_argument('--render', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
if args.glb:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(Path(args.glb).resolve()))
root = bpy.data.objects.get(args.root)
if root is None:
    raise RuntimeError('Missing required root: ' + args.root)
objects = [o for o in [root, *root.children_recursive] if o.type == 'MESH']
if not objects:
    raise RuntimeError('No meshes in selected model')
bpy.context.view_layer.update()

def connected_components(bm):
    components = 0
    remaining = set(bm.verts)
    while remaining:
        components += 1
        pending = [remaining.pop()]
        while pending:
            for edge in pending.pop().link_edges:
                for v in edge.verts:
                    if v in remaining:
                        remaining.remove(v)
                        pending.append(v)
    return components

rows = []
for ob in objects:
    mesh = ob.data
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    coords = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    row = {
        'name': ob.name, 'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles),
        'zero_area_triangles': sum(t.area < 1e-12 for t in mesh.loop_triangles),
        'non_manifold_edges': sum(not e.is_manifold for e in bm.edges),
        'boundary_edges': sum(e.is_boundary for e in bm.edges),
        'loose_vertices': sum(not v.link_faces for v in bm.verts),
        'inconsistent_winding_edges': sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
        'signed_volume': bm.calc_volume(signed=True), 'connected_components': connected_components(bm),
        'bounds_min': [min(v[i] for v in coords) for i in range(3)],
        'bounds_max': [max(v[i] for v in coords) for i in range(3)],
        'world_scale': list(ob.matrix_world.to_scale()),
        'uv_layers': [uv.name for uv in mesh.uv_layers],
        'uv_nonfinite': sum(not all(math.isfinite(v) for v in item.uv) for uv in mesh.uv_layers for item in uv.data),
        'materials': [m.name if m else None for m in mesh.materials],
        'modifiers': [m.type for m in ob.modifiers],
    }
    # glTF duplicates positions for UV and hard-normal seams. Weld only this
    # disposable BMesh so topology QA distinguishes seams from actual holes.
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
    row['position_weld_tolerance_m'] = 1e-7
    row['welded_connected_components'] = connected_components(bm)
    row['welded_non_manifold_edges'] = sum(not e.is_manifold for e in bm.edges)
    row['welded_inconsistent_winding_edges'] = sum(e.is_manifold and not e.is_contiguous for e in bm.edges)
    rows.append(row)
    bm.free()
materials = []
used_materials = {m for ob in objects for m in ob.data.materials if m}
for mat in sorted(used_materials, key=lambda m: m.name):
    node = mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
    materials.append({'name': mat.name, 'use_nodes': mat.use_nodes,
        'base_color': list(node.inputs['Base Color'].default_value) if node else None,
        'metallic': node.inputs['Metallic'].default_value if node else None,
        'roughness': node.inputs['Roughness'].default_value if node else None,
        'alpha': node.inputs['Alpha'].default_value if node else None,
        'image_nodes': [{'name': n.image.name if n.image else None,
                         'path': n.image.filepath if n.image else None,
                         'packed': bool(n.image and n.image.packed_file),
                         'colorspace': n.image.colorspace_settings.name if n.image else None}
                        for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE'] if mat.use_nodes else []})
coords = [ob.matrix_world @ Vector(c) for ob in objects for c in ob.bound_box]
minimum = Vector([min(v[i] for v in coords) for i in range(3)])
maximum = Vector([max(v[i] for v in coords) for i in range(3)])
input_path = Path(args.glb).resolve() if args.glb else Path(bpy.data.filepath)
report = {'blender_version': bpy.app.version_string, 'source': bpy.data.filepath,
    'input_sha256': hashlib.sha256(input_path.read_bytes()).hexdigest(),
    'imported_glb': args.glb, 'root': args.root, 'root_location': list(root.location),
    'unit_system': bpy.context.scene.unit_settings.system,
    'bounds_min': list(minimum), 'bounds_max': list(maximum), 'dimensions': list(maximum-minimum),
    'mesh_count': len(objects), 'triangles': sum(r['triangles'] for r in rows),
    'armatures': [o.name for o in [root, *root.children_recursive] if o.type == 'ARMATURE'],
    'animation_data': [o.name for o in [root, *root.children_recursive] if o.animation_data],
    'materials': materials, 'meshes': rows}
(out / 'inspection.json').write_text(json.dumps(report, indent=2) + '\n')
print('QA_INSPECTION', json.dumps({k: report[k] for k in ['root', 'mesh_count', 'triangles', 'dimensions']}), flush=True)
if not args.render:
    raise SystemExit(0)

# Camera and light changes stay in this disposable process. No .blend is saved.
scene = bpy.context.scene
for ob in list(scene.objects):
    if ob not in objects and ob != root:
        ob.hide_render = True
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 800
scene.render.resolution_y = 650
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
world = bpy.data.worlds.new('QA neutral world')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18, .18, .18, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .5
scene.world = world
center = (minimum + maximum) / 2
size = (maximum-minimum).length
for name, direction, power in [('Key',(-3,-4,5),600), ('Fill',(4,2,3),400), ('Bottom',(1,1,-4),200)]:
    light = bpy.data.lights.new('QA ' + name, 'AREA')
    light.energy = power
    light.shape = 'DISK'
    light.size = 4
    ob = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(ob)
    ob.location = center + Vector(direction)
    ob.rotation_euler = (center-ob.location).to_track_quat('-Z','Y').to_euler()
cam_data = bpy.data.cameras.new('QA camera')
cam = bpy.data.objects.new('QA camera', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.type = 'ORTHO'
cam_data.ortho_scale = size * 1.18
cam_data.clip_start = .001
cam_data.clip_end = 100
views = {'front':(0,-1,0), 'back':(0,1,0), 'left':(-1,0,0), 'right':(1,0,0),
         'top':(0,0,1), 'bottom':(0,0,-1), 'three-quarter':(3,-4,3)}
manifest = []
for name, direction in views.items():
    target = center
    cam.location = target + Vector(direction).normalized() * size * 3
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(out / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    manifest.append({'view': name, 'camera': list(cam.location), 'target': list(target), 'ortho_scale': cam_data.ortho_scale})
if args.root == 'ASSET_Table':
    target = Vector((-.62,-.636,.8535))
    cam_data.ortho_scale = .15
    cam.location = target + Vector((.12,-.16,.065))
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(out / 'detail-rail-sight.png')
    bpy.ops.render.render(write_still=True)
    manifest.append({'view': 'detail-rail-sight', 'camera': list(cam.location), 'target': list(target), 'ortho_scale': cam_data.ortho_scale})
(out / 'render-settings.json').write_text(json.dumps({'engine':scene.render.engine, 'samples':scene.cycles.samples,
    'view_transform':scene.view_settings.view_transform, 'views':manifest}, indent=2) + '\n')

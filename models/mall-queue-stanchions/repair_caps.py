"""Repair legacy axis rings in saved sources, staging all output separately."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

import bpy

assert bpy.app.background, 'Run in a separate background Blender process'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def serial(value):
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    if hasattr(value, 'name'):
        return value.name
    return [serial(v) for v in value]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def snapshot(repaired):
    objects = []
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        data = {'name': obj.name, 'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                'matrix': [list(row) for row in obj.matrix_world], 'selected': obj.select_get(),
                'properties': {key: serial(value) for key, value in obj.items()},
                'modifiers': [(m.name, m.type) for m in obj.modifiers]}
        if obj.type == 'MESH':
            mesh = obj.data
            data['materials'] = [m.name if m else None for m in mesh.materials]
            data['geometry'] = sorted({tuple(round(c, 7) for c in v.co) for v in mesh.vertices}) if obj.name in repaired else {
                'vertices': [list(v.co) for v in mesh.vertices], 'edges': [list(e.vertices) for e in mesh.edges],
                'faces': [(list(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
                'uv': [[list(item.uv) for item in layer.data] for layer in mesh.uv_layers]}
        objects.append(data)
    materials = []
    for material in sorted(bpy.data.materials, key=lambda m: m.name):
        nodes = []
        if material.use_nodes:
            for node in material.node_tree.nodes:
                nodes.append((node.name, node.type, [(s.identifier, serial(s.default_value)) for s in node.inputs if hasattr(s, 'default_value')]))
        materials.append((material.name, list(material.diffuse_color), nodes))
    scene = bpy.context.scene
    return digest({'objects': objects, 'materials': materials,
                   'active': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
                   'cursor': list(scene.cursor.location), 'frame': scene.frame_current,
                   'units': [scene.unit_settings.system, scene.unit_settings.scale_length],
                   'camera': scene.camera.name if scene.camera else None})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=HERE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    assert args.input.resolve() != args.output.resolve(), 'Stage before replacing originals'
    for folder in ['sources', 'exports']: (args.output / folder).mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('fixed_queue_generator', HERE / 'generate.py')
    generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    generator.HERE = args.output.resolve()
    results = []
    for suffix, root_name, posts in [('post', 'ASSET_MallQueuePost', 1), ('short', 'ASSET_MallQueueShort', 2), ('long', 'ASSET_MallQueueLong', 2)]:
        identity = 'mall-queue-' + suffix
        bpy.ops.wm.open_mainfile(filepath=str(args.input / 'sources' / (identity + '.blend')), load_ui=False, use_scripts=False)
        root = bpy.data.objects[root_name]
        objects = list(root.children_recursive)
        profiles = [(name, profile) for name, profile, _ in generator.POST_LATHE_PARTS if any(radius == 0 for radius, _ in profile)]
        targets = [(obj, profile) for obj in objects for name, profile in profiles
                   if obj.name == name or re.fullmatch(re.escape(name) + r'\.\d+', obj.name)]
        assert len(targets) == posts * 5, [(o.name, p) for o, p in targets]
        repaired = {o.name for o, _ in targets}
        before = snapshot(repaired)
        selection = list(bpy.context.selected_objects); active = bpy.context.view_layer.objects.active
        cursor = bpy.context.scene.cursor.location.copy()
        for obj, profile in targets:
            mesh = obj.data
            assert not obj.modifiers and not obj.vertex_groups and not mesh.uv_layers and not mesh.shape_keys
            assert not mesh.has_custom_normals and all(p.use_smooth and p.material_index == 0 for p in mesh.polygons)
            # Refuse to overwrite saved/manual shape edits. The known legacy
            # profile must match before only its redundant axis topology changes.
            expected = [(radius * math.cos(i*math.tau/48), radius * math.sin(i*math.tau/48), height)
                        for radius, height in profile for i in range(48)]
            assert len(expected) == len(mesh.vertices), obj.name
            assert all(max(abs(a-b) for a,b in zip(v.co, xyz)) < 1e-7 for v,xyz in zip(mesh.vertices, expected)), obj.name
            legacy_faces = [(row*48+i, row*48+(i+1)%48, (row+1)*48+(i+1)%48, (row+1)*48+i)
                            for row in range(len(profile)-1) for i in range(48)]
            assert [tuple(p.vertices) for p in mesh.polygons] == legacy_faces, 'Saved topology differs: ' + obj.name
            vertices, faces = generator.lathe_geometry(profile)
            mesh.clear_geometry(); mesh.from_pydata(vertices, [], faces); mesh.update()
            for polygon in mesh.polygons: polygon.use_smooth = True
            mesh.calc_loop_triangles()
            assert all(t.area > 0 for t in mesh.loop_triangles), obj.name
        generator.export_asset(identity, root, objects)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection: obj.select_set(True)
        bpy.context.view_layer.objects.active = active
        bpy.context.scene.cursor.location = cursor
        bpy.context.view_layer.update()
        after = snapshot(repaired)
        assert before == after, 'Unrelated source geometry, materials, placement or selection changed'
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output / 'sources' / (identity + '.blend')), compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(args.output / 'sources' / (identity + '.blend')), load_ui=False, use_scripts=False)
        assert snapshot(repaired) == before, 'Reopened source differs'
        results.append({'id': identity, 'status': 'PASS', 'repaired_meshes': sorted(repaired),
                        'preserved_source_semantics_sha256': before, 'source_reopened': True,
                        'editable_parts': len(objects), 'blender_version': bpy.app.version_string})
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(results, indent=2) + '\n')
    print('PASS: 25 cap meshes repaired; remaining source semantics preserved and reopened')


if __name__ == '__main__':
    main()

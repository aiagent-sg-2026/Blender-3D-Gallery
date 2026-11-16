"""Inspect saved mesh features and persist a controlled source edit on a copy."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import bpy
import bmesh

HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'sources/battery-display-rack.blend'
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = digest(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects['ASSET_BatteryDisplayRack']
    objects = sorted(root.children_recursive, key=lambda obj: obj.name)
    assert all(obj.type == 'MESH' for obj in objects), 'Original editable meshes only'
    assert bpy.context.scene.unit_settings.system == 'METRIC'
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert tuple(root.location) == (0, 0, 0)
    assert tuple(root.scale) == (1, 1, 1)
    assert len({obj.data.materials[0].name for obj in objects}) == 3
    assert not bpy.data.images, 'No external or procedural image assets'
    parts = {}
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        assert all(edge.is_manifold for edge in bm.edges), obj.name
        assert bm.calc_volume() > 0, obj.name
        bm.free()
        assert len(obj.data.materials) == 1
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        parts[obj.name] = {
            'min': [min(point[i] for point in points) for i in range(3)],
            'max': [max(point[i] for point in points) for i in range(3)],
            'material': obj.data.materials[0].name,
        }
        evaluated.to_mesh_clear()
    near = lambda a, b: abs(a - b) < 1e-5
    assert all(part['min'][2] >= -1e-6 for part in parts.values())
    assert near(parts['FRAME_Platform']['min'][2], 0)
    assert near(parts['FRAME_Platform']['min'][0], -.5)
    assert near(parts['FRAME_Platform']['max'][0], .5)
    cards = [name for name in parts if name.startswith('CARD_') and not name.startswith('CARD_Blank')]
    cells = [name for name in parts if name.startswith('CELL_') and not name.startswith('CELL_Positive')]
    assert len(cards) == 20
    assert len(cells) == 72
    assert len([name for name in parts if name.startswith('BLISTER_')]) == 20
    assert len([name for name in parts if name.startswith('HOOK_Pin')]) == 20
    assert len([name for name in parts if name.startswith('BINS_Divider')]) == 3
    # Real through-hole count from topology, independent of the generator's loop bounds.
    def genus(obj):
        mesh = obj.data
        return (2 - (len(mesh.vertices) - len(mesh.edges) + len(mesh.polygons))) // 2
    holes = genus(bpy.data.objects['PEGBOARD_ThroughHoles'])
    assert holes == 192, holes
    for name in cards:
        assert genus(bpy.data.objects[name]) == 1
        suffix = name[len('CARD_'):]
        card, pin, bubble = parts[name], parts['HOOK_Pin_' + suffix], parts['BLISTER_' + suffix]
        assert pin['min'][1] < card['min'][1] < pin['max'][1]
        assert bubble['max'][1] <= card['min'][1], 'Bubble meets card front'
        assert card['min'][2] > parts['BINS_Rear']['max'][2], 'Packs clear bins'
    assert parts['HEADER_BlankPanel']['min'][1] < parts['HEADER_Surround']['min'][1]
    assert parts['BINS_Divider']['max'][2] < parts['PEGBOARD_ThroughHoles']['min'][2]
    spec = importlib.util.spec_from_file_location('asset_generator', HERE / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scratch = HERE / 'reports/source-edit'
    scratch.mkdir(exist_ok=True)
    module.export(scratch / 'source-reexport.glb')
    assert digest(scratch / 'source-reexport.glb') == digest(HERE / 'exports/optimized.glb')
    target = bpy.data.objects['FRAME_Platform']
    for vertex in target.data.vertices:
        vertex.co.x *= .92
    target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .77
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(scratch / 'edited.blend'), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(scratch / 'edited.blend'))
    module.export(scratch / 'edited.glb')
    assert digest(source) == before
    report = {
        'result': 'PASS', 'source_reopened': True, 'editable_mesh_parts': len(objects),
        'closed_manifold_meshes': len(objects), 'asset_materials': 3,
        'pack_count': len(cards), 'cell_count': len(cells), 'pegboard_through_holes': holes,
        'units': 'metres', 'blender_version': bpy.app.version_string, 'source_sha256': before,
        'unchanged_source_reexport_sha256': digest(scratch / 'source-reexport.glb'),
        'original_source_unchanged': True, 'edited_mesh': 'BATCH_Mattefinish',
        'edit': 'FRAME_Platform local mesh X scaled by 0.92; matte roughness to 0.77',
        'edited_glb_sha256': digest(scratch / 'edited.glb'),
        'parts_axis_order': 'Blender X,Y,Z (width,depth,height)', 'parts': parts,
    }
    (HERE / 'reports/sources.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'parts'}))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

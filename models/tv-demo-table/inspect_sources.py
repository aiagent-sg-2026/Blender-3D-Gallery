"""Inspect saved editable source, then exercise edits on a disposable copy."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import bpy
import bmesh

HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'sources/tv-demo-table.blend'
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = digest(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects['ASSET_TVDemoTable']
    objects = sorted(root.children_recursive, key=lambda obj: obj.name)
    assert all(obj.type == 'MESH' for obj in objects), 'No text, curves or external content'
    assert bpy.context.scene.unit_settings.system == 'METRIC'
    assert bpy.context.scene.unit_settings.scale_length == 1
    assert tuple(root.location) == (0, 0, 0)
    assert tuple(root.scale) == (1, 1, 1)
    assert len({obj.data.materials[0].name for obj in objects}) == 3
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
    assert near(parts['TABLE_Top']['max'][2], .8)
    assert near(parts['TABLE_Top']['max'][0] - parts['TABLE_Top']['min'][0], 2)
    assert near(parts['TABLE_Top']['max'][1] - parts['TABLE_Top']['min'][1], 1)
    assert parts['SHELF_Lower']['max'][2] < parts['TABLE_Top']['min'][2]
    assert parts['SHELF_Lower']['min'][2] > .2
    screens = [parts['TV_' + name + '_Screen'] for name in ['Left', 'Centre', 'Right']]
    for label, screen in zip(['Left', 'Centre', 'Right'], screens):
        housing = parts['TV_' + label + '_Housing']
        base = parts['TV_' + label + '_Base']
        riser = parts['TV_' + label + '_Riser']
        assert screen['min'][1] < housing['min'][1], 'Blender front -Y / glTF +Z'
        assert near((screen['max'][0] - screen['min'][0]) / (screen['max'][2] - screen['min'][2]), 16 / 9)
        assert near(base['min'][2], .8), 'Stand touches tabletop'
        assert riser['min'][2] < base['max'][2] and riser['max'][2] > housing['min'][2]
        assert housing['min'][0] > -1 and housing['max'][0] < 1
    for left, right in zip(screens, screens[1:]):
        assert left['max'][0] < right['min'][0], 'Screens do not overlap'
    assert parts['SIGN_BlankCard']['max'][2] < min(screen['min'][2] for screen in screens) + .06
    assert all(part['min'][2] >= -1e-6 for part in parts.values()), 'Floor datum'
    spec = importlib.util.spec_from_file_location('asset_generator', HERE / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scratch = HERE / 'reports/source-edit'
    scratch.mkdir(exist_ok=True)
    module.export(scratch / 'source-reexport.glb')
    assert digest(scratch / 'source-reexport.glb') == digest(HERE / 'exports/optimized.glb')
    target = bpy.data.objects['TABLE_Top']
    for vertex in target.data.vertices:
        vertex.co.x *= .92
    target.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .77
    bpy.ops.wm.save_as_mainfile(filepath=str(scratch / 'edited.blend'), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(scratch / 'edited.blend'))
    module.export(scratch / 'edited.glb')
    assert digest(source) == before
    report = {
        'result': 'PASS', 'source_reopened': True, 'editable_mesh_parts': len(objects),
        'closed_manifold_meshes': len(objects), 'asset_materials': 3, 'screen_count': len(screens),
        'units': 'metres', 'blender_version': bpy.app.version_string, 'source_sha256': before,
        'unchanged_source_reexport_sha256': digest(scratch / 'source-reexport.glb'),
        'original_source_unchanged': True, 'edited_mesh': 'TABLE_Top',
        'edit': 'Top local mesh X vertices scaled by 0.92; laminate roughness to 0.77',
        'edited_glb_sha256': digest(scratch / 'edited.glb'),
        'tabletop_height': parts['TABLE_Top']['max'][2],
        'shelf_top_height': parts['SHELF_Lower']['max'][2],
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

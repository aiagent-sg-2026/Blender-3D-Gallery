"""Check saved editable geometry and persist a controlled edit on a copy."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import bpy
import bmesh

HERE = Path(__file__).resolve().parent


def main():
    source = HERE / 'sources/cordless-phone-display.blend'
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = digest(source)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects['ASSET_CordlessPhoneDisplay']
    objects = sorted(root.children_recursive, key=lambda obj: obj.name)
    assert all(obj.type == 'MESH' for obj in objects), 'Only original editable meshes'
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
    print(json.dumps({'handset_min_z': parts['HANDSET_FrontShell']['min'][2],
                      'cradle_max_z': parts['CRADLE_Well']['max'][2],
                      'handset_bounds': parts['HANDSET_FrontShell']}), flush=True)
    assert all(part['min'][2] >= -1e-6 for part in parts.values()), 'Floor datum'
    assert near(parts['PLINTH_ShadowFoot']['min'][2], 0)
    assert near(parts['BASE_Lower']['min'][2], parts['PLINTH_TopInlay']['max'][2])
    assert near(parts['PRICE_HolderFoot']['min'][2], parts['PLINTH_TopInlay']['max'][2])
    assert parts['HANDSET_FrontShell']['min'][2] <= parts['CRADLE_Well']['max'][2] + .0001, 'Handset heel is seated'
    assert parts['HANDSET_RearShell']['max'][2] > parts['CRADLE_RearRest']['max'][2]
    assert len([name for name in parts if name.startswith('KEYPAD_Key_')]) == 12
    assert parts['SCREEN_BlankLCD']['min'][1] < parts['HANDSET_FrontShell']['max'][1]
    assert parts['ANTENNA_Stub']['max'][2] > parts['HANDSET_FrontShell']['max'][2]
    assert parts['PRICE_Frame']['min'][0] > parts['BASE_Upper']['max'][0], 'Separate holder clears phone'
    assert parts['PRICE_BlankCard']['max'][2] < parts['SCREEN_BlankLCD']['min'][2], 'Card does not obscure display'
    spec = importlib.util.spec_from_file_location('asset_generator', HERE / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scratch = HERE / 'reports/source-edit'
    scratch.mkdir(exist_ok=True)
    module.export(scratch / 'source-reexport.glb')
    assert digest(scratch / 'source-reexport.glb') == digest(HERE / 'exports/optimized.glb')
    target = bpy.data.objects['PLINTH_Body']
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
        'closed_manifold_meshes': len(objects), 'asset_materials': 3, 'keypad_key_count': 12,
        'units': 'metres', 'blender_version': bpy.app.version_string, 'source_sha256': before,
        'unchanged_source_reexport_sha256': digest(scratch / 'source-reexport.glb'),
        'original_source_unchanged': True, 'edited_mesh': 'PLINTH_Body',
        'edit': 'Plinth local mesh X vertices scaled by 0.92; mineral roughness to 0.77',
        'edited_glb_sha256': digest(scratch / 'edited.glb'),
        'plinth_top_height': parts['PLINTH_TopInlay']['max'][2],
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

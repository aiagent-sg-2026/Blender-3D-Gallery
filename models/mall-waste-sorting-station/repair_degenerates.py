"""Stage a collection-root source repair without rebuilding authored modules."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from blender_degenerate_cleanup import source_fingerprint, geometry_counts

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--expected-sha256', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
assert hashlib.sha256(args.input.read_bytes()).hexdigest() == args.expected_sha256
assert args.output.resolve() != args.input.parent.resolve()
assert not args.output.exists(), 'Use a new staging directory'
args.output.mkdir(parents=True)
spec = importlib.util.spec_from_file_location('waste_generator', HERE / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
bpy.ops.wm.open_mainfile(filepath=str(args.input), load_ui=False, use_scripts=False)
root = bpy.data.collections[generator.ROOT]
assert set(generator.GROUPS) == {c.name for c in root.children}
objects = list(root.all_objects)
before_hash = source_fingerprint(); before = geometry_counts(objects)
selection = list(bpy.context.selected_objects); active = bpy.context.view_layer.objects.active
cursor = bpy.context.scene.cursor.location.copy()
generator.prepare_asset_geometry(); bpy.context.view_layer.update()
after = geometry_counts(objects)
assert sum(r['zero_area_triangles'] for r in after) == 0, after
generator.export_asset(args.output / (generator.ID + '.glb'))
bpy.ops.object.select_all(action='DESELECT')
for obj in selection: obj.select_set(True)
bpy.context.view_layer.objects.active = active
bpy.context.scene.cursor.location = cursor
bpy.context.view_layer.update()
assert source_fingerprint() == before_hash
bpy.ops.wm.save_as_mainfile(filepath=str(args.output / (generator.ID + '.blend')), compress=True)
bpy.ops.wm.open_mainfile(filepath=str(args.output / (generator.ID + '.blend')), load_ui=False, use_scripts=False)
assert source_fingerprint() == before_hash
reopened = geometry_counts(list(bpy.data.collections[generator.ROOT].all_objects))
assert sum(r['zero_area_triangles'] for r in reopened) == 0
receipt = {'id': generator.ID, 'status': 'PASS', 'blender': bpy.app.version_string,
           'source_sha256_before': args.expected_sha256, 'source_fingerprint': before_hash,
           'authored_data_and_collection_membership_preserved': True, 'source_reopened': True,
           'editable_parts': len(objects), 'modules': list(generator.GROUPS),
           'before': before, 'after': after, 'reopened': reopened}
(args.output / 'source-repair.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS: source/reopened geometry clean;', len(objects), 'editable parts; seven module collections preserved')

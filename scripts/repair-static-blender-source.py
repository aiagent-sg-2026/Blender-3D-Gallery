"""Repair one reviewed saved source in a distinct staging directory."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / 'scripts'))
from blender_degenerate_cleanup import source_fingerprint, geometry_counts, FINGERPRINT_SCHEMA

parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--generator', type=Path, required=True)
parser.add_argument('--input', type=Path, required=True)
parser.add_argument('--expected-sha256', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--lod', type=int, help='Use a reviewed generator hook to derive a source LOD before cleanup')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
assert args.input.is_file() and args.input.suffix == '.blend'
assert hashlib.sha256(args.input.read_bytes()).hexdigest() == args.expected_sha256
assert args.output.resolve() != args.input.parent.resolve()
args.output.mkdir(parents=True, exist_ok=True)
assert not (args.output / (args.id + '.blend')).exists()
assert not (args.output / (args.id + '.glb')).exists()
generator_path = args.generator.resolve()
assert generator_path.is_relative_to(REPOSITORY) and generator_path.suffix == '.py'
assert generator_path.is_file(), 'Pass the explicitly reviewed project generator'
spec = importlib.util.spec_from_file_location('reviewed_generator', generator_path)
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
assert args.id in generator.CLEANUP_PARTS
catalog = json.loads((REPOSITORY / 'models/catalog.json').read_text())
asset = next(a for c in catalog['collections'] for a in c['assets'] if a['id'] == args.id)
bpy.ops.wm.open_mainfile(filepath=str(args.input), load_ui=False, use_scripts=False)
root = bpy.data.objects.get(asset['root']) or bpy.data.collections.get(asset['root'])
assert root is not None
collection_root = isinstance(root, bpy.types.Collection)
if collection_root:
    assert generator.ROOT == root.name
    assert set(generator.GROUPS) == {child.name for child in root.children}
objects = list(root.all_objects) if collection_root else list(root.children_recursive)
original_fingerprint = source_fingerprint()
if args.lod is not None:
    assert hasattr(generator, 'prepare_source_lod'), 'This generator has no reviewed saved-source LOD derivation'
    generator.prepare_source_lod(root, args.lod)
    bpy.context.view_layer.update()
before_hash = source_fingerprint(); before = geometry_counts(objects)
selection = list(bpy.context.selected_objects); active = bpy.context.view_layer.objects.active
cursor = bpy.context.scene.cursor.location.copy()
generator.prepare_asset_geometry(args.id, objects)
bpy.context.view_layer.update()
after = geometry_counts(objects)
assert sum(item['zero_area_triangles'] for item in after) == 0, after
if collection_root:
    generator.export_asset(args.output / (args.id + '.glb'))
else:
    generator.export_asset(args.id, root, objects, args.output / (args.id + '.glb'))
bpy.ops.object.select_all(action='DESELECT')
for obj in selection: obj.select_set(True)
bpy.context.view_layer.objects.active = active
bpy.context.scene.cursor.location = cursor
bpy.context.view_layer.update()
assert source_fingerprint() == before_hash, 'Authored data or unrelated source semantics changed'
bpy.ops.wm.save_as_mainfile(filepath=str(args.output / (args.id + '.blend')), compress=True, relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(args.output / (args.id + '.blend')), load_ui=False, use_scripts=False)
assert source_fingerprint() == before_hash, 'Reopened source semantics changed'
reopened_root = bpy.data.collections[asset['root']] if collection_root else bpy.data.objects[asset['root']]
reopened = geometry_counts(list(reopened_root.all_objects) if collection_root else list(reopened_root.children_recursive))
assert sum(item['zero_area_triangles'] for item in reopened) == 0
receipt = {'id': args.id, 'status': 'PASS', 'blender': bpy.app.version_string,
           'original_sha256': args.expected_sha256, 'source_fingerprint': before_hash,
           'fingerprint_schema': FINGERPRINT_SCHEMA,
           'original_fingerprint': original_fingerprint, 'derived_lod': args.lod,
           'authored_data_preserved': True, 'source_reopened': True, 'editable_parts': len(objects),
           'root_type': reopened_root.bl_rna.identifier,
           'derived_face_attributes': [{'object': obj.name, 'attribute': 'cleanup_alternate_quad',
               'faces': len(obj.data.polygons),
               'alternate_diagonals': sum(value.value for value in obj.data.attributes['cleanup_alternate_quad'].data)}
               for obj in bpy.data.objects if obj.type == 'MESH' and obj.data.attributes.get('cleanup_alternate_quad')],
           'before': before, 'after': after, 'reopened': reopened}
(args.output / 'source-repair.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS:', args.id, 'source and reopened evaluated geometry clean; authored data preserved')

"""Native regression: fresh four-LOD generation and delivered GLB import."""
from pathlib import Path
import bpy, hashlib, importlib.util, json, shutil, subprocess, sys
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1] / 'scripts'))
from blender_degenerate_cleanup import geometry_counts, source_fingerprint, FINGERPRINT_SCHEMA
args = sys.argv[sys.argv.index('--') + 1:]
assert len(args) == 1, 'Pass a new, owned output directory'
out = Path(args[0]); out.mkdir(parents=True, exist_ok=False)
spec = importlib.util.spec_from_file_location('m057_fresh', here / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
generator.HERE = out
sys.argv = ['test_degenerate_cleanup.py', '--skip-render']
generator.main()
for name in ['backlog.json', 'support-manifest.json']:
    shutil.copyfile(here / name, out / name)
subprocess.run(['node', str(here / 'validate.mjs')], env={**__import__('os').environ, 'MODEL_QA_ROOT': str(out)}, check=True)
bpy.ops.wm.open_mainfile(filepath=str(out / 'sources' / (here.name + '.blend')), use_scripts=False, load_ui=False)
root = bpy.data.objects[generator.ROOT]
assert len(root.children_recursive) == 78
fingerprint = source_fingerprint()
generator.prepare_asset_geometry(generator.SLUG, list(root.children_recursive))
assert source_fingerprint() == fingerprint, 'Cleanup must be idempotent'
assert sum(r['zero_area_triangles'] for r in geometry_counts(root.children_recursive)) == 0
assert sum(1 for o in root.children_recursive for m in o.modifiers if m.type == 'NODES') == 1
imports = []
for n in range(4):
    file = here / 'exports' / ('lod%d.glb' % n)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(file))
    rows = geometry_counts(bpy.context.scene.objects)
    assert sum(r['zero_area_triangles'] for r in rows) == 0, rows
    assert len([o for o in bpy.context.scene.objects if o.type == 'MESH']) == 42
    imports.append({'file': str(file.relative_to(here)), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                    'triangles': sum(r['triangles'] for r in rows), 'zero_area_triangles': 0})
(out / 'native-regression.json').write_text(json.dumps({'status':'PASS', 'blender_version':bpy.app.version_string,
    'fingerprint_schema':FINGERPRINT_SCHEMA, 'fresh_generation':'All four LODs, 24 stable anchors, two packed PNGs, LED contact, L footprint, label visibility and collider validated by the production validator',
    'editable_parts':78, 'idempotent_cleanup':True, 'delivered_imports':imports}, indent=2) + '\n')
print('PASS M057 fresh generation, idempotent cleanup and four canonical native imports')

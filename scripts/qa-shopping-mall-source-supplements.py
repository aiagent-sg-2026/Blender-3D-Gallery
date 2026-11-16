"""Resolve source collection roots without changing assets or earlier evidence."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def inspect(inventory_path, identity, output):
    import addon_utils
    import bpy
    assert bpy.app.background
    spec = importlib.util.spec_from_file_location('mall_source_inspector', ROOT / 'scripts/qa-shopping-mall-blender.py')
    inspector = importlib.util.module_from_spec(spec); spec.loader.exec_module(inspector)
    inventory = json.loads(Path(inventory_path).read_text())
    asset = next(a for a in inventory['assets'] if a['id'] == identity)
    for name in inspector.MODULES:
        addon_utils.enable(name, default_set=True, persistent=True)
        assert addon_utils.check(name)[1]
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / asset['source']), load_ui=False, use_scripts=False)
    collection = bpy.data.collections.get(asset.get('root', ''))
    if not collection:
        raise RuntimeError('No exact source collection for ' + identity)
    objects = [o for o in collection.all_objects if o.type in {'MESH', 'FONT', 'CURVE', 'SURFACE'}]
    assert objects
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    result = {'status': 'SCANNED', 'mapping': {'method': 'exact source Collection root', 'root': collection.name,
               'original_evidence': 'blender/' + identity + '.json',
               'reason': 'Authoring Collection and export Empty share an identifier; the first object-only lookup was insufficient.'},
              'file_version': list(bpy.data.version), 'declared_scene_scale': scene.unit_settings.scale_length,
              'source_geometry_count': len(objects), 'meshes': inspector.inspect_objects(objects, 'source', scene)}
    inspector.save(Path(output), result)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('directory', type=Path)
    args = parser.parse_args(); directory = args.directory.resolve()
    inventory = json.loads((directory / 'inventory.json').read_text())
    out = directory / 'source-supplements'; out.mkdir(exist_ok=True)
    results = []
    for asset in inventory['assets']:
        evidence = directory / 'blender' / (asset['id'] + '.json')
        if not evidence.exists(): continue
        original = json.loads(evidence.read_text())['phases'].get('source', {})
        if original.get('status') != 'ROOT_UNRESOLVED': continue
        destination = out / (asset['id'] + '.json')
        with tempfile.TemporaryDirectory(prefix='mall-qa-source-config-') as profile:
            env = {**os.environ, 'BLENDER_USER_CONFIG': profile, 'PYTHONDONTWRITEBYTECODE': '1'}
            expression = "import sys; sys.path.insert(0," + repr(str(ROOT / 'scripts')) + "); import importlib; m=importlib.import_module('qa-shopping-mall-source-supplements'); m.inspect(" + repr(str(directory / 'inventory.json')) + ',' + repr(asset['id']) + ',' + repr(str(destination)) + ')'
            run = subprocess.run([os.environ.get('BLENDER_BIN', '/Applications/Blender.app/Contents/MacOS/Blender'),
                                  '--background', '--factory-startup', '--disable-autoexec', '--threads', '2',
                                  '--python-exit-code', '23', '--python-expr', expression], env=env, capture_output=True, text=True, timeout=150)
            (directory / 'logs' / (asset['id'] + '-source-supplement.log')).write_text(run.stdout + run.stderr)
            results.append({'id': asset['id'], 'exit_code': run.returncode, 'resolved': destination.exists() and run.returncode == 0})
            print(asset['id'], 'SOURCE_COLLECTION_SCANNED' if results[-1]['resolved'] else 'SOURCE_MAPPING_UNRESOLVED', flush=True)
    (out / 'execution.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()

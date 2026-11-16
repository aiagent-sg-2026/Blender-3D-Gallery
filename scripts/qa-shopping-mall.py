"""Read-only mall QA orchestrator. Write only the requested evidence directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def discover():
    catalog = json.loads((ROOT / 'models/catalog.json').read_text())
    assets, duplicates, seen = [], [], set()
    for collection in catalog['collections']:
        for asset in collection['assets']:
            primary = 'Shopping Mall' in (asset.get('category'), asset.get('browseCategory'))
            support = 'mall' in collection['id'] or 'mall' in asset.get('tags', [])
            if not (primary or support):
                continue
            if asset['file'] in seen:
                duplicates.append({'id': asset['id'], 'file': asset['file'], 'collection': collection['id']})
                continue
            seen.add(asset['file'])
            folder = next(parent for parent in Path(asset['file']).parents if parent.parent == Path('models'))
            metadata = json.loads((ROOT / asset['metadata']).read_text()) if asset.get('metadata') else {}
            declared = metadata.get('paths', {}).get('source') or metadata.get('source') or metadata.get('files', {}).get('source')
            candidates = []
            if isinstance(declared, str):
                candidates.append(Path(declared) if declared.startswith('models/') else folder / declared)
            candidates += [folder / 'sources' / (asset['id'] + '.blend'), folder / 'sources' / (Path(asset['file']).stem + '.blend'), folder / 'scene.blend']
            existing = [p for p in candidates if (ROOT / p).is_file()]
            if not existing:
                existing = sorted(folder.glob('*.blend')) + sorted((folder / 'sources').glob('*.blend'))
            source = existing[0] if len(set(existing)) == 1 or (existing and existing[0] in candidates) else None
            assets.append({'id': asset['id'], 'name': asset['name'], 'group': 'shopping-mall' if primary else 'supporting-character',
                           'collection': collection['id'], 'file': asset['file'], 'folder': str(folder),
                           'metadata': asset.get('metadata'), 'source': str(source) if source else None,
                           'source_mapping': 'declared/exact candidate; root checked in Blender' if source else 'UNRESOLVED',
                           'root': asset.get('root'), 'tags': asset.get('tags', []),
                           'declared_metrics': metadata.get('metrics', {}), 'budgets': metadata.get('budgets', {})})
    # Explicit non-catalog current artifacts are supplemental, not silently published.
    extra = [('gjh-mall-visitor-v2-lod1', 'models/gjh-mall-visitor-v2/exports/gjh-mall-visitor-v2-lod1.glb',
              'models/gjh-mall-visitor-v2/sources/gjh-mall-visitor-v2.blend', 'supporting-lod'),
             ('chibi-mall-visitor-local', 'models/chibi-mall-visitor/chibi-mall-visitor.glb',
              'models/chibi-mall-visitor/scene.blend', 'local-uncatalogued-character')]
    for identity, glb, source, group in extra:
        if (ROOT / glb).exists():
            assets.append({'id': identity, 'name': identity, 'group': group, 'collection': None, 'file': glb,
                           'folder': str(Path(glb).parents[1] if '/exports/' in glb else Path(glb).parent),
                           'metadata': None, 'source': source if (ROOT / source).exists() else None, 'root': None,
                           'source_mapping': 'related source; equivalence not assumed', 'tags': [], 'declared_metrics': {}, 'budgets': {}})
    for asset in assets:
        for key in ['file', 'source', 'metadata']:
            if asset.get(key):
                path = (ROOT / asset[key]).resolve()
                assert path.is_relative_to(ROOT / 'models'), path
                asset[key + '_sha256'] = digest(path)
    folders = {ROOT / a['folder'] for a in assets}
    inputs = {ROOT / 'models/catalog.json'}
    for folder in folders:
        for p in folder.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.blend', '.glb', '.json', '.py', '.png', '.jpg', '.jpeg', '.webp'}:
                if not any(part in {'reports', 'previews', 'thumbnails', '__pycache__'} for part in p.relative_to(folder).parts):
                    inputs.add(p)
    return {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
            'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'Current Shopping Mall catalog assets, mall-tagged/catalog characters, their explicit LOD and the local chibi mall visitor. Historical reports, build replicas, other products and unrelated characters excluded.',
            'duplicate_catalog_records': duplicates, 'assets': assets,
            'protected_inputs': {str(p.relative_to(ROOT)): digest(p) for p in sorted(inputs)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2, choices=[1, 2])
    parser.add_argument('--only', nargs='*')
    args = parser.parse_args()
    output = args.output.resolve()
    assert not output.is_relative_to(ROOT / 'models')
    output.mkdir(parents=True, exist_ok=False)
    inventory = discover()
    inventory['scanner_sources'] = {str(p.relative_to(ROOT)): digest(p) for p in [
        ROOT / 'scripts/qa-shopping-mall.py', ROOT / 'scripts/qa-shopping-mall-glb.mjs',
        ROOT / 'scripts/qa-shopping-mall-blender.py']}
    if args.only:
        inventory['assets'] = [a for a in inventory['assets'] if a['id'] in args.only]
    write(output / 'inventory.json', inventory)
    subprocess.run(['node', str(ROOT / 'scripts/qa-shopping-mall-glb.mjs'), str(output / 'inventory.json'), str(output)], cwd=ROOT, check=True)
    executable = os.environ.get('BLENDER_BIN', '/Applications/Blender.app/Contents/MacOS/Blender')
    # Only separate Blender processes run concurrently; never share bpy between threads.
    with tempfile.TemporaryDirectory(prefix='mall-qa-config-') as profile:
        def inspect(asset):
            env = {**os.environ, 'BLENDER_USER_CONFIG': str(Path(profile) / asset['id']), 'PYTHONDONTWRITEBYTECODE': '1'}
            Path(env['BLENDER_USER_CONFIG']).mkdir()
            command = [executable, '--background', '--factory-startup', '--disable-autoexec', '--threads', '2',
                       '--python-exit-code', '23', '--python', str(ROOT / 'scripts/qa-shopping-mall-blender.py'), '--',
                       '--inventory', str(output / 'inventory.json'), '--asset', asset['id'], '--output', str(output)]
            try:
                run = subprocess.run(command, env=env, capture_output=True, text=True, timeout=150)
                (output / 'logs').mkdir(exist_ok=True)
                (output / 'logs' / (asset['id'] + '.log')).write_text(run.stdout + run.stderr)
                if run.returncode != 0:
                    return {'id': asset['id'], 'status': 'SCAN_ERROR', 'exit_code': run.returncode, 'log': 'logs/' + asset['id'] + '.log'}
                return {'id': asset['id'], 'status': 'SCANNED', 'exit_code': 0}
            except subprocess.TimeoutExpired:
                return {'id': asset['id'], 'status': 'TIMEOUT', 'seconds': 150}
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            tasks = [pool.submit(inspect, a) for a in inventory['assets']]
            for task in as_completed(tasks):
                result = task.result(); results.append(result)
                write(output / 'progress.json', {'completed': len(results), 'total': len(tasks), 'results': results})
                print(f"{len(results)}/{len(tasks)} {result['id']} {result['status']}", flush=True)
    changed = [name for name, expected in inventory['protected_inputs'].items()
               if not (ROOT / name).exists() or digest(ROOT / name) != expected]
    new_inputs = sorted(set(discover()['protected_inputs']) - set(inventory['protected_inputs']))
    write(output / 'preservation.json', {'status': 'PASS' if not changed and not new_inputs else 'INPUT_DRIFT',
                                        'checked_files': len(inventory['protected_inputs']), 'changed': changed,
                                        'new_model_input_files': new_inputs})
    write(output / 'execution.json', {'results': results, 'workers': args.workers, 'source_revision': inventory['source_revision'],
                                     'status': 'COMPLETE' if not changed and not new_inputs and all(r['status'] == 'SCANNED' for r in results) else 'INCOMPLETE'})


if __name__ == '__main__':
    main()

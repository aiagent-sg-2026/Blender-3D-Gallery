"""Read-only asset discovery; write inventory/evidence only, never model assets."""
import collections
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/model-qa'
EXCLUDED = {'.git', 'node_modules', 'dist', '.venv', 'venv', '__pycache__'}


def sha256(file):
    h = hashlib.sha256()
    with file.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    if (OUT / 'inventory.json').exists():
        raise SystemExit('Inventory already exists; preserve its QA history. Reconcile new artifacts explicitly instead of resetting statuses.')
    catalog = json.loads((ROOT / 'models/catalog.json').read_text())
    files = []
    extensions = collections.Counter()
    for directory, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            file = Path(directory) / name
            relative = file.relative_to(ROOT).as_posix()
            if relative.startswith('docs/model-qa/') or relative == 'docs/3d-model-qa-progress.md':
                continue
            if file.is_symlink():
                continue
            suffix = file.suffix.lower()
            extensions[suffix] += 1
            if suffix in {'.blend', '.blend1', '.glb', '.gltf', '.obj', '.fbx', '.bin', '.png', '.jpg', '.jpeg', '.webp', '.exr', '.hdr', '.py', '.mjs', '.json', '.md'}:
                entry = {'path': relative, 'bytes': file.stat().st_size, 'extension': suffix}
                if suffix in {'.blend', '.blend1', '.glb', '.gltf', '.obj', '.fbx'}:
                    entry['sha256'] = sha256(file)
                files.append(entry)
    assets = {file['path']: file for file in files if 'sha256' in file}
    records = []
    claimed = set()
    for collection in catalog['collections']:
        for asset in collection['assets']:
            file = ROOT / asset['file']
            folder = file.parent
            while folder != ROOT / 'models' and folder != ROOT:
                sources = sorted(folder.glob('*.blend')) + sorted(folder.glob('sources/*.blend'))
                generators = sorted(folder.glob('*.py'))
                if sources or generators:
                    break
                folder = folder.parent
            prefix = folder.relative_to(ROOT).as_posix() + '/'
            related = [f['path'] for f in files if f['path'].startswith(prefix)]
            record = {
                'qa_id': f'MODEL-{len(records)+1:04d}', 'model_id': asset['id'], 'name': asset['name'],
                'collection': collection['id'], 'kind': 'catalog-model', 'status': 'PENDING',
                'export_paths': [asset['file']], 'source_candidates': [s.relative_to(ROOT).as_posix() for s in sources],
                'source_mapping': 'candidate; inspect asset root in Blender before acceptance',
                'generator_candidates': [g.relative_to(ROOT).as_posix() for g in generators],
                'render_scripts': [s for s in related if s.endswith('.py') and 'render' in Path(s).name],
                'validation_tools': [s for s in related if s.endswith(('.mjs', '.py')) and any(k in Path(s).name for k in ('validate', 'verify', 'inspect', 'test'))],
                'metadata': asset.get('metadata'), 'thumbnail': asset['thumbnail'], 'root': asset.get('root'),
                'runtime_route': '?model=' + asset.get('slug', asset['id']),
                'export_sha256': assets.get(asset['file'], {}).get('sha256'),
                'defects': [], 'repairs': [], 'qa_results': {}, 'commit_sha': None, 'remote_verified': False,
                'remaining_risks': ['Not yet inspected under this QA campaign.'],
            }
            records.append(record)
            claimed.update(record['export_paths'])
            claimed.update(record['source_candidates'])
    # Preserve every uncatalogued artifact in the queue, including historical
    # variants. Identical hashes are linked, never silently treated as QA PASS.
    hash_owners = collections.defaultdict(list)
    for relative in claimed:
        if relative in assets:
            hash_owners[assets[relative]['sha256']].append(relative)
    for relative, asset in sorted(assets.items()):
        if relative in claimed:
            continue
        historical = relative.startswith(('docs/verification/', 'output/')) or '/reports/' in relative or relative.endswith('.blend1')
        records.append({
            'qa_id': f'MODEL-{len(records)+1:04d}', 'model_id': 'artifact:' + relative,
            'name': Path(relative).name, 'kind': 'historical-or-test-variant' if historical else 'uncatalogued-artifact',
            'status': 'PENDING', 'export_paths': [relative] if asset['extension'] in {'.glb', '.gltf'} else [],
            'source_candidates': [relative] if asset['extension'] in {'.blend', '.blend1'} else [],
            'sha256': asset['sha256'], 'identical_catalog_artifacts': sorted(hash_owners[asset['sha256']]),
            'defects': [], 'repairs': [], 'qa_results': {}, 'commit_sha': None, 'remote_verified': False,
            'remaining_risks': ['Artifact identity and applicability require inspection; no exemption or PASS assumed.'],
        })
    inventory = {
        'schema_version': 1, 'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'All repository authoring assets and historical/test variants; dependencies, git internals and dist build replicas excluded.',
        'excluded_directories': sorted(EXCLUDED), 'catalog_entries': sum(len(c['assets']) for c in catalog['collections']),
        'physical_3d_files': len(assets), 'extension_counts': dict(sorted(extensions.items())),
        'ordering': 'Catalog order first; remaining artifacts sorted by path. Only one active model; no advance before verified main release.',
        'runtime': 'src/main.js -> src/viewer.js -> Three.js GLTFLoader; Game and Solar have separate consumers.',
        'shared_tools': ['scripts/validate-assets.mjs', 'scripts/catalog.mjs', 'scripts/export-selected-assets.py', 'scripts/render-asset-thumbnails.py', 'tests/*.test.mjs', 'scripts/test-*-browser.mjs'],
        'records': records,
    }
    (OUT / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    with (OUT / 'file-index.jsonl').open('w') as stream:
        for file in files:
            stream.write(json.dumps(file) + '\n')
    progress = ['# 3D Model QA Progress', '',
        'Discovery only. No model has passed this campaign. Historical evidence is reference material, not current acceptance.', '',
        f'Catalog entries: {inventory["catalog_entries"]}; physical 3D artifacts: {len(assets)}; queue records: {len(records)}.', '',
        'Full source/export mappings, hashes, generators, validation tools, defects, repairs, gate results, commit and remote evidence: [inventory](model-qa/inventory.json).', '',
        'All initial records are PENDING. Uncatalogued/historical artifacts remain explicitly in the queue. Dist is a generated replica; dependencies are outside authoring scope.', '',
        '| QA ID | Model | Source / GLB | Status | Defects / repairs / QA | Commit / GitHub main | Remaining risk |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for r in records:
        paths = ', '.join(r['export_paths'] + r['source_candidates'])
        progress.append(f'| {r["qa_id"]} | {r["model_id"]} | {paths} | PENDING | Not inspected | — / unverified | QA pending |')
    (ROOT / 'docs/3d-model-qa-progress.md').write_text('\n'.join(progress) + '\n')
    print(json.dumps({k: inventory[k] for k in ['catalog_entries', 'physical_3d_files', 'source_revision']}))
    print('Queue records:', len(records))


if __name__ == '__main__':
    main()

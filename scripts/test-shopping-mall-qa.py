"""Independent known-value calibration for material-scoped density and topology."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
executable = os.environ.get('BLENDER_BIN', '/Applications/Blender.app/Contents/MacOS/Blender')
receipt = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix='mall-qa-calibration-') as directory:
    temporary = Path(directory)
    env = {**os.environ, 'BLENDER_USER_CONFIG': str(temporary / 'config'), 'PYTHONDONTWRITEBYTECODE': '1'}
    (temporary / 'config').mkdir()
    common = [executable, '--background', '--factory-startup', '--disable-autoexec', '--threads', '2', '--python-exit-code', '23']
    commands = [common + ['--python', str(ROOT / 'scripts/qa-shopping-mall-fixture.py'), '--', directory]]
    run = subprocess.run(commands[0], env=env, capture_output=True, text=True, timeout=90)
    assert run.returncode == 0, run.stdout + run.stderr
    # Both fixtures are owned by this test; production discovery forbids escaped paths.
    relative = lambda file: os.path.relpath(temporary / file, ROOT)
    hashed = lambda file: hashlib.sha256((temporary / file).read_bytes()).hexdigest()
    asset = {'id': 'known-fixture', 'root': 'QA_FixtureRoot', 'file': relative('fixture.glb'),
             'source': relative('fixture.blend'), 'file_sha256': hashed('fixture.glb')}
    (temporary / 'inventory.json').write_text(json.dumps({'assets': [asset]}))
    subprocess.run(['node', str(ROOT / 'scripts/qa-shopping-mall-glb.mjs'), str(temporary / 'inventory.json'), directory], check=True, cwd=ROOT)
    command = common + ['--python', str(ROOT / 'scripts/qa-shopping-mall-blender.py'), '--', '--inventory',
                        str(temporary / 'inventory.json'), '--asset', 'known-fixture', '--output', directory]
    run = subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads((temporary / 'blender/known-fixture.json').read_text())
    checks = {}
    for phase, inspection in result['phases'].items():
        assert inspection['status'] == 'SCANNED', inspection
        assert inspection['mapping']['method'] == ('exact source Collection root' if phase == 'source' else 'exact catalog root')
        densities = [d for mesh in inspection['meshes'] for d in mesh['density']]
        assert len(densities) == 2, densities
        assert all(d['status'] == 'MEASURED' for d in densities), densities
        observed = sorted(d['density_px_per_m'] for d in densities)
        assert observed == [64.0, 128.0], observed
        assert sum(m['density_status'] == 'N_A_NO_IMAGE_TEXTURE' for m in inspection['meshes']) == 1
        textured = next(m for m in inspection['meshes'] if m['density'])
        assert textured['raw_topology']['boundary_edges'] == 8
        checks[phase] = {'expected_px_per_m': [64, 128], 'observed_px_per_m': observed, 'untextured_patch_N_A': True, 'boundary_edges': 8,
                         'root_kind': 'Collection' if phase == 'source' else 'Empty Object'}
    glb = json.loads((temporary / 'glb/known-fixture.json').read_text())
    assert glb['metrics']['triangles'] == 6 and glb['validation']['numErrors'] == 0
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({'status': 'PASS', 'checks': checks, 'triangles': 6,
                                  'scope': 'Known-value material filtering, UV scaling, actual image resolutions, image-free applicability and topology checks'}, indent=2) + '\n')
print('PASS: per-material density 64/128 px/m, untextured N_A, boundary topology and independent GLB geometry')

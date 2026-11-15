"""Exercise the complete fresh source/export path without rendering previews."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import subprocess
import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
folder = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('areca_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
from blender_degenerate_cleanup import geometry_counts, source_fingerprint

with tempfile.TemporaryDirectory(prefix='areca-cleanup-regression-') as directory:
    generator.HERE = Path(directory)
    for name in ('exports', 'sources', 'previews'):
        (generator.HERE / name).mkdir()
    generator.build('gjh-areca-planter', 'ASSET_GJHArecaPlanter', generator.planter,
                    (3, 4, 2.8), (0, 0, 1.1), 2.8, render=False)
    objects = list(bpy.data.objects['ASSET_GJHArecaPlanter'].children_recursive)
    assert len(objects) == 213
    assert sum(item['zero_area_triangles'] for item in geometry_counts(objects)) == 0
    assert sum(obj.name.startswith('Palm leaflet ') for obj in objects) == 198
    fingerprint = source_fingerprint()
    generator.prepare_asset_geometry('gjh-areca-planter', objects)
    assert source_fingerprint() == fingerprint
    assert all(sum(m.name == 'Degenerate face cleanup' for m in obj.modifiers) <= 1 for obj in objects)
    exported = generator.HERE / 'exports/gjh-areca-planter.glb'
    subprocess.run(['node', str(folder.parents[1] / 'scripts/check-degenerate-repair.mjs'),
                    str(folder / 'exports/gjh-areca-planter.glb'), str(exported),
                    str(generator.HERE / 'export-check.json'), '--allow-normal-drift',
                    '--precision-line-tolerance-m=2e-10'], check=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(exported))
    assert sum(item['zero_area_triangles'] for item in geometry_counts(list(bpy.context.scene.objects))) == 0
    print('PASS: fresh complete source/export retains 213 editable parts, 198 palm leaflets and zero degenerates')

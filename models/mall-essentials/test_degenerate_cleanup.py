"""Exercise the actual generator's reviewed cleanup before any export/render."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import subprocess

import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
folder = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('essentials_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
from blender_degenerate_cleanup import geometry_counts, source_fingerprint

for identity, factory, parts in [('mall-trash-bin', generator.waste_bin, 32),
                                  ('mall-directory-kiosk', generator.directory, 23),
                                  ('mall-advertising-lightbox', generator.lightbox, 18),
                                  ('mall-display-shelf', generator.shelf, 31)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    factory()
    objects = list(bpy.context.scene.objects)
    assert len(objects) == parts
    before = geometry_counts(objects)
    assert sum(r['zero_area_triangles'] for r in before) > 0
    fingerprint = source_fingerprint()
    generator.prepare_asset_geometry(identity, objects)
    bpy.context.view_layer.update()
    after = geometry_counts(objects)
    assert sum(r['zero_area_triangles'] for r in after) == 0, after
    assert source_fingerprint() == fingerprint
    generator.prepare_asset_geometry(identity, objects)
    assert all(sum(m.name == 'Degenerate face cleanup' for m in obj.modifiers) <= 1 for obj in objects)
    print('PASS:', identity, 'generator cleanup preserves', parts, 'authored parts and is idempotent')

with tempfile.TemporaryDirectory(prefix='shelf-cleanup-regression-') as directory:
    generator.HERE = Path(directory)
    for name in ('exports', 'sources', 'previews'):
        (generator.HERE / name).mkdir()
    generator.build('mall-display-shelf', 'ASSET_MallDisplayShelf', generator.shelf,
                    (3, 4.8, 2.8), (0, 0, .96), 2.75, render=False)
    objects = list(bpy.data.objects['ASSET_MallDisplayShelf'].children_recursive)
    assert len(objects) == 31
    assert sum(item['zero_area_triangles'] for item in geometry_counts(objects)) == 0
    exported = generator.HERE / 'exports/mall-display-shelf.glb'
    subprocess.run(['node', str(folder.parents[1] / 'scripts/check-degenerate-repair.mjs'),
                    str(exported), str(exported), str(generator.HERE / 'export-check.json')], check=True)
    print('PASS: complete fresh shelf source/export is clean; preview rendering skipped')

"""Exercise the actual generator's reviewed cleanup before any export/render."""
import importlib.util
from pathlib import Path
import sys

import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
folder = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('essentials_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
from blender_degenerate_cleanup import geometry_counts, source_fingerprint

bpy.ops.wm.read_factory_settings(use_empty=True)
generator.waste_bin()
objects = list(bpy.context.scene.objects)
assert len(objects) == 32
before = geometry_counts(objects)
assert sum(r['zero_area_triangles'] for r in before) > 0
fingerprint = source_fingerprint()
generator.prepare_asset_geometry('mall-trash-bin', objects)
bpy.context.view_layer.update()
after = geometry_counts(objects)
assert sum(r['zero_area_triangles'] for r in after) == 0, after
assert source_fingerprint() == fingerprint
generator.prepare_asset_geometry('mall-trash-bin', objects)
assert all(sum(m.name == 'Degenerate face cleanup' for m in obj.modifiers) <= 1 for obj in objects)
assert bpy.data.objects['Label - WASTE'].type == 'FONT'
assert bpy.data.objects['Label - WASTE'].data.body == 'WASTE'
print('PASS: actual generator cleanup removes degenerate evaluated faces, preserves all 32 authored parts and is idempotent')

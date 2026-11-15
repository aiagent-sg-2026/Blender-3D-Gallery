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
spec = importlib.util.spec_from_file_location('service_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
from blender_degenerate_cleanup import geometry_counts, source_fingerprint

with tempfile.TemporaryDirectory(prefix='service-cleanup-regression-') as directory:
    generator.HERE = Path(directory)
    for name in ('exports', 'sources', 'previews'):
        (generator.HERE / name).mkdir()
    generator.build('mall-service-desk', 'ASSET_MallServiceDesk', generator.service_desk,
                    (3.8, 5.5, 3.2), (0, 0, .89), 3.9, render=False)
    objects = list(bpy.data.objects['ASSET_MallServiceDesk'].children_recursive)
    assert len(objects) == 37
    assert sum(item['zero_area_triangles'] for item in geometry_counts(objects)) == 0
    assert any(obj.type == 'FONT' and obj.data.body == 'SERVICE' for obj in objects)
    fingerprint = source_fingerprint()
    generator.prepare_asset_geometry('mall-service-desk', objects)
    assert source_fingerprint() == fingerprint
    assert all(sum(m.name == 'Degenerate face cleanup' for m in obj.modifiers) <= 1 for obj in objects)
    exported = generator.HERE / 'exports/mall-service-desk.glb'
    subprocess.run(['node', str(folder.parents[1] / 'scripts/check-degenerate-repair.mjs'),
                    str(exported), str(exported), str(generator.HERE / 'export-check.json')], check=True)
    print('PASS: fresh complete source/export retains 37 editable parts, editable text and zero degenerates')

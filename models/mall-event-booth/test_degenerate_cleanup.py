"""Verify actual fresh generation without rendering or replacing repository files."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import subprocess
import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
folder = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('booth_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
from blender_degenerate_cleanup import geometry_counts, source_fingerprint

with tempfile.TemporaryDirectory(prefix='booth-cleanup-regression-') as directory:
    generator.HERE = Path(directory)
    for name in ('exports','sources','previews'):
        (generator.HERE / name).mkdir()
    generator.build(render=False)
    root = bpy.data.collections[generator.ROOT]
    objects = list(root.all_objects)
    assert len(objects) == 28
    assert set(generator.GROUPS) == {c.name for c in root.children}
    assert sum(r['zero_area_triangles'] for r in geometry_counts(objects)) == 0
    fingerprint = source_fingerprint()
    generator.prepare_asset_geometry()
    assert source_fingerprint() == fingerprint
    assert all(sum(m.name == 'Degenerate face cleanup' for m in obj.modifiers) <= 1 for obj in objects)
    assert bpy.data.objects['PosterPanel editable headline'].data.body == 'YOUR STORY'
    exported=generator.HERE/'exports'/f'{generator.ID}.glb'
    subprocess.run(['node',str(folder.parents[1]/'scripts/check-degenerate-repair.mjs'),
                    str(exported),str(exported),str(generator.HERE/'export-check.json')],check=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(exported))
    assert sum(item['zero_area_triangles'] for item in geometry_counts(list(bpy.context.scene.objects))) == 0
    print('PASS: fresh generator retains 28 editable parts, three collections, zero degenerates and idempotent cleanup')

"""Reopen native source, replay export, edit a disposable band, and reimport GLB."""
from pathlib import Path
import hashlib
import json
import runpy
import sys
import tempfile
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent


def main():
    api = runpy.run_path(str(HERE / 'generate.py'))
    source = HERE / 'sources/arched-gateway-sign.blend'
    delivered = HERE / 'exports/optimized.glb'
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects[api['ROOT']]
    assert root.location.length == 0
    assert bpy.context.scene.unit_settings.scale_length == 1
    parts = [o for o in root.children_recursive if o.type == 'MESH']
    assert len({o.data.materials[0].name for o in parts}) == 3
    assert not any(o.type == 'FONT' for o in root.children_recursive)
    assert not any(o.animation_data for o in root.children_recursive)
    assert not any(o.library for o in bpy.data.objects)
    with tempfile.TemporaryDirectory(prefix='arched-gateway-source-') as tmp:
        replay = Path(tmp) / 'replay.glb'
        api['export'](replay)
        assert replay.read_bytes() == delivered.read_bytes(), 'saved-source replay matches delivery'
        band = bpy.data.objects['SOURCE_BlankBand']
        band.location.z += .1
        edited_source = Path(tmp) / 'edited.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(edited_source), compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(edited_source))
        edited = Path(tmp) / 'edited.glb'
        api['export'](edited)
        assert edited.read_bytes() != delivered.read_bytes()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(edited))
        edited_band = bpy.data.objects['SIGN_Band']
        points = [edited_band.matrix_world @ Vector(v) for v in edited_band.bound_box]
        assert abs(min(p.z for p in points) - 4.25) < 1e-5
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(delivered))
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(meshes) == 3
    points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    for a, b in zip([high[i] - low[i] for i in range(3)], [12, 1.3, 6]):
        assert abs(a - b) < 1e-5
    report = {
        'result': 'PASS', 'blender_version': bpy.app.version_string,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'glb_sha256': hashlib.sha256(delivered.read_bytes()).hexdigest(),
        'editable_source_meshes': len(parts), 'runtime_meshes': len(meshes),
        'saved_source_replay': 'byte-identical',
        'source_edit': 'Saved/reopened disposable sign band +0.1 m; exported/imported lower bound 4.25 m; delivery untouched.',
        'native_glb_import': 'PASS', 'blender_bounds': {'min': low, 'max': high}
    }
    (HERE / 'reports/sources.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

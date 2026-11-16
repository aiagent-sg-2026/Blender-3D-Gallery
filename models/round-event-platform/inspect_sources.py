"""Source topology/UV checks, saved-source replay and a disposable saved edit."""
from pathlib import Path
import hashlib
import json
import math
import runpy
import sys
import tempfile

import bmesh
import bpy

HERE = Path(__file__).resolve().parent


def main():
    api = runpy.run_path(str(HERE / 'generate.py'))
    source = HERE / 'sources/round-event-platform.blend'
    delivered = HERE / 'exports/optimized.glb'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    root = bpy.data.objects[api['ROOT']]
    scene = bpy.context.scene
    assert scene.unit_settings.system == 'METRIC' and scene.unit_settings.scale_length == 1
    assert root.location.length == 0
    parts = [obj for obj in root.children_recursive if obj.type == 'MESH']
    assert len(parts) == 1 and len(parts[0].data.materials) == 3
    assert not any(obj.library or obj.animation_data or obj.type == 'FONT' for obj in root.children_recursive)
    mesh = parts[0].data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(edge.is_manifold for edge in bm.edges)
    volume = bm.calc_volume(signed=True)
    assert volume > 0
    bm.free()
    mesh.calc_loop_triangles()
    uv = mesh.uv_layers.active
    assert uv
    densities = []
    for triangle in mesh.loop_triangles:
        a, b, c = [mesh.vertices[i].co for i in triangle.vertices]
        u, v, w = [uv.data[i].uv for i in triangle.loops]
        world_area = (b - a).cross(c - a).length / 2
        uv_area = abs((v.x - u.x) * (w.y - u.y) - (v.y - u.y) * (w.x - u.x)) / 2
        assert world_area > 0 and uv_area > 0
        densities.append(math.sqrt(uv_area / world_area))
    assert max(densities) / min(densities) < 1.01, 'consistent atlas scale within 1 percent'
    with tempfile.TemporaryDirectory(prefix='round-platform-source-') as tmp:
        replay = Path(tmp) / 'replay.glb'
        api['export'](replay)
        assert replay.read_bytes() == delivered.read_bytes(), 'saved-source replay must match delivery'
        for vertex in mesh.vertices:
            vertex.co.x *= .92
        mesh.materials[0].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .77
        edited_source = Path(tmp) / 'edited.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(edited_source), compress=True)
        bpy.ops.wm.open_mainfile(filepath=str(edited_source))
        edited = Path(tmp) / 'edited.glb'
        api['export'](edited)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(edited))
        edited_mesh = next(obj for obj in bpy.context.scene.objects if obj.type == 'MESH')
        xs = [(edited_mesh.matrix_world @ vertex.co).x for vertex in edited_mesh.data.vertices]
        assert abs(max(xs) - min(xs) - 7.36) < 1e-5
        assert abs(bpy.data.materials['Platform_Top'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value - .77) < 1e-6
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    report = {
        'result': 'PASS', 'blender_version': bpy.app.version_string,
        'source_sha256': source_hash, 'glb_sha256': hashlib.sha256(delivered.read_bytes()).hexdigest(),
        'editable_source_meshes': len(parts), 'closed_manifold_meshes': len(parts),
        'signed_volume_m3': volume, 'uv_scale_per_m_range': [min(densities), max(densities)],
        'saved_source_replay': 'byte-identical',
        'source_edit': 'Saved/reopened disposable mesh X scale 0.92 and top roughness 0.77; GLB reimport width 7.36 m and roughness verified.',
        'original_source_unchanged': True
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

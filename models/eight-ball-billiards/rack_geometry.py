"""Close the three authored cylindrical rack bars at shared miter planes."""
import runpy
from pathlib import Path
from mathutils import Vector


def close_rack_joints(bars):
    assert len(bars) == 3
    endpoints = []
    for ob in bars:
        mesh = ob.data
        assert len(mesh.vertices) == 24 and len(mesh.polygons) == 14
        zs = sorted({round(v.co.z, 7) for v in mesh.vertices})
        assert len(zs) == 2, 'Expected original uncut twelve-sided bars'
        endpoints.append([ob.matrix_world @ Vector((0, 0, z)) for z in zs])
    axes = [(b-a).normalized() for a, b in endpoints]
    for i in range(3):
        assert (endpoints[i][1]-endpoints[(i+1)%3][0]).length < 1e-6
    # Keep the original radial coordinates, UVs, faces and transforms. Only
    # slide each ring vertex along its bar to the common corner bisector.
    for i, ob in enumerate(bars):
        for v in ob.data.vertices:
            end = int(v.co.z > 0)
            neighbor = axes[(i+1)%3] if end else axes[(i-1)%3]
            normal = (axes[i]+neighbor).normalized()
            local_normal = ob.matrix_world.to_3x3().transposed() @ normal
            endpoint = ob.matrix_world.inverted() @ endpoints[i][end]
            assert abs(local_normal.z) > .1
            v.co.z = endpoint.z-(local_normal.x*v.co.x+local_normal.y*v.co.y)/local_normal.z
        ob.data.update()
    # The matching rings must close in world space, independently of naming
    # or the different orientations of the three rods.
    for i, ob in enumerate(bars):
        other = bars[(i+1)%3]
        a = [ob.matrix_world @ v.co for v in ob.data.vertices if v.co.z > 0]
        b = [other.matrix_world @ v.co for v in other.data.vertices if v.co.z < 0]
        assert len(a) == len(b) == 12
        assert max(min((p-q).length for q in b) for p in a) < 1e-6
    mark_caps = runpy.run_path(str(Path(__file__).with_name('cue_shading.py')))['mark_planar_caps']
    for ob in bars:
        assert mark_caps(ob.data) == (2, 24)
        # Clipping a cylinder changes corner-angle weights. Preserve the true
        # radial side normal instead of allowing that weighting to bend it.
        normals = [None] * len(ob.data.loops)
        for face in ob.data.polygons:
            for index in face.loop_indices:
                point = ob.data.vertices[ob.data.loops[index].vertex_index].co
                normals[index] = face.normal[:] if len(face.vertices) > 4 else Vector((point.x, point.y, 0)).normalized()[:]
        ob.data.normals_split_custom_set(normals)

"""Inspect saved assembly surfaces and prove a saved-source edit/re-export."""
from pathlib import Path
import bpy
import hashlib
import json
import os
import tempfile
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
source = HERE / 'foundation-fitted.blend'
original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.view_layer.update()


def meshes(root):
    return [o for o in bpy.data.objects[root].children_recursive if o.type == 'MESH']


def tree(objects):
    verts, faces = [], []
    for obj in objects:
        start = len(verts)
        verts.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(start + i for i in face.vertices) for face in obj.data.polygons)
    return BVHTree.FromPolygons(verts, faces)


def hit(bvh, origin, direction, distance):
    return bvh.ray_cast(Vector(origin), Vector(direction), distance)[0]


def bounds(obj):
    points = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return [min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]


fascias = [o for o in bpy.context.scene.objects if o.parent is None and o.get('kind') in ('fascia210', 'fascia348')]
fascia_meshes = [m for root in fascias for m in root.children_recursive if m.type == 'MESH']
fascia_tree = tree(fascia_meshes)
misses, edge_rechecks, samples = [], [], 0
for sign in (-1, 1):
    for i in range(227):
        y = -4.52 + i * .04
        for j in range(29):
            z = 2.41 + j * .02
            samples += 1
            if hit(fascia_tree, (sign * 2.1, y, z), (sign, 0, 0), .5) is None:
                probes = [hit(fascia_tree, (sign * 2.1, y + d, z), (sign, 0, 0), .5) is not None for d in (-.00001, .00001)]
                edge_rechecks.append({'side': sign, 'y': y, 'z': z, 'bothOffsetsHit': all(probes)})
                if not all(probes):
                    misses.append([sign, y, z])
assert not misses, misses[:5]
collar_meshes = meshes('Ceiling_Collar')
collar = tree(collar_meshes)
collar_misses, hole_hits, collar_samples = [], [], 0
for i in range(60):
    for j in range(60):
        x, y = -.59 + i * .02, -.59 + j * .02
        if abs(x) < .3 and abs(y) < .3:
            continue
        collar_samples += 1
        if hit(collar, (-3 + x, -13.8 + y, 2.95), (0, 0, 1), .1) is None:
            collar_misses.append([x, y])
for x in (-.25, 0, .25):
    for y in (-.25, 0, .25):
        if hit(collar, (-3 + x, -13.8 + y, 2.95), (0, 0, 1), .1) is not None:
            hole_hits.append([x, y])
assert not collar_misses and not hole_hits

all_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
boxes = {o: bounds(o) for o in all_meshes}
overlaps, seen = [], set()
for a in fascia_meshes + collar_meshes:
    for b in all_meshes:
        pair = tuple(sorted((a.name, b.name)))
        if a == b or pair in seen:
            continue
        seen.add(pair)
        lo, hi = boxes[a]
        other_lo, other_hi = boxes[b]
        ext = [min(hi[i], other_hi[i]) - max(lo[i], other_lo[i]) for i in range(3)]
        if min(ext) > .00001:
            overlaps.append({'a': a.name, 'b': b.name, 'extents': ext})
assert not overlaps, overlaps[:5]

ceiling_objects = [m for o in bpy.context.scene.objects if o.parent is None and o.get('kind') == 'ceiling' for m in o.children_recursive if m.type == 'MESH']
ceiling_tree = tree(ceiling_objects)
ceiling_reveals = []
for x in (-2.4, 2.4):
    for y in (-4.4, -3.8, -2.6, -1.4, 0, 1.4, 2.6, 3.8, 4.4):
        # Offset into either neighbouring cell; record exact grid-boundary misses.
        hits = [hit(ceiling_tree, (x + offset, y, 2.9999), (0, 0, 1), .05) for offset in (-.00001, .00001)]
        values = [None if h is None else float(h.z - 3) for h in hits]
        corners = None
        if any(v is None for v in values):
            # At a crossing of two cell boundaries, offset both axes; retain the
            # original misses instead of describing them as successful rays.
            probes = [hit(ceiling_tree, (x + dx, y + dy, 2.9999), (0, 0, 1), .05)
                      for dx in (-.00001, .00001) for dy in (-.00001, .00001)]
            corners = [None if p is None else float(p.z - 3) for p in probes]
        checked = values if corners is None else corners
        assert all(v is not None and -.0001 <= v <= .0081 for v in checked), (x, y, values, corners)
        ceiling_reveals.append({'x': x, 'y': y, 'originalOffsetGaps': values,
                               'twoAxisEdgeRecheckGaps': corners, 'offsetMetres': .00001})

# Prove the actual saved source remains editable, using an isolated copy.
target = next(o for o in meshes('Fascia_Run_A_Left') if o.name.startswith('SIGN_ReplaceableFace'))
before_top = bounds(target)[1][2]
target.data = target.data.copy()
material = target.data.materials[0].copy()
target.data.materials[0] = material
material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .37
for v in target.data.vertices:
    if (target.matrix_world @ v.co).z > before_top - .0001:
        v.co += target.matrix_world.to_3x3().inverted() @ Vector((0, 0, .004))
target.data.update()
target_name = target.name
with tempfile.TemporaryDirectory(prefix='fnd003-source-') as directory:
    copy_path = Path(directory) / 'edited.blend'
    export_path = Path(directory) / 'edited.glb'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(copy_path), compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(copy_path))
    target = bpy.data.objects[target_name]
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(export_path), export_format='GLB', use_selection=True, export_apply=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(export_path))
    imported = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(imported) == 1
    after_top = bounds(imported[0])[1][2]
    assert abs(after_top - before_top - .004) < .00001, (before_top, after_top)
    roughness = imported[0].data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value
    assert abs(roughness - .37) < .00001
assert hashlib.sha256(source.read_bytes()).hexdigest() == original_hash
result = {'status': 'PASS', 'sourceSha256': original_hash, 'fasciaRays': samples,
          'fasciaMisses': misses, 'fasciaEdgeRechecks': edge_rechecks,
          'collarRays': collar_samples, 'collarMisses': collar_misses, 'holeSamples': 9,
          'holeHits': hole_hits, 'newComponentOverlaps': overlaps, 'ceilingReveals': ceiling_reveals,
          'sourceEditProof': {'worldTopDeltaMetres': after_top - before_top, 'roughness': roughness,
                              'savedReopenedReexportedImported': True, 'canonicalSourceUnchanged': True},
          'limits': 'Fixed ray samples and component boxes; isolated source edit proof, not construction certification.'}
path = HERE / 'reports/source-surfaces.json'
assert not path.is_symlink()
fd, tmp = tempfile.mkstemp(prefix='.source-', dir=path.parent)
with os.fdopen(fd, 'w') as handle:
    json.dump(result, handle, indent=2)
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
os.replace(tmp, path)
print('PASS source surfaces and actual saved-source edit/export proof')

"""Regression for radius-zero caps; run only in background Blender."""
import importlib.util
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy

assert bpy.app.background
sys.dont_write_bytecode = True
folder = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('queue_generator', folder / 'generate.py')
generator = importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
material = bpy.data.materials.new('Cap regression material')
obj = generator.lathe('Cap regression cylinder', [(0,0),(1,0),(1,1),(0,1)], material)
mesh = obj.data; mesh.calc_loop_triangles()
bm = bmesh.new(); bm.from_mesh(mesh)
observed = {'vertices': len(mesh.vertices), 'triangles': len(mesh.loop_triangles),
            'zero_area_triangles': sum(t.area == 0 for t in mesh.loop_triangles),
            'boundary_edges': sum(e.is_boundary for e in bm.edges),
            'non_manifold_edges': sum(not e.is_manifold for e in bm.edges),
            'signed_volume': bm.calc_volume(signed=True)}
bm.free()
print('CAP_REGRESSION', json.dumps(observed), flush=True)
assert observed['zero_area_triangles'] == 0, observed
assert observed['vertices'] == 98  # Two 48-vertex circles and two shared axis vertices.
assert observed['triangles'] == 192  # 96 side triangles and 96 cap triangles.
assert observed['boundary_edges'] == observed['non_manifold_edges'] == 0
expected_volume = 48 * .5 * math.sin(2 * math.pi / 48)
assert math.isclose(observed['signed_volume'], expected_volume, rel_tol=1e-6), observed
print('PASS: closed, outward cylinder with no degenerate cap triangles', flush=True)

"""Reconcile M057 source density on a temporary triangulated copy only."""
from pathlib import Path
import importlib.util
import importlib
import json
import sys
import addon_utils
import bmesh
import bpy

assert bpy.app.background
root = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out = root / 'docs/model-qa/shopping-mall-2026-11-15'
identity = 'gjh-m057-premium-wall-shelf-corner'
inventory = json.loads((out / 'inventory.json').read_text())
asset = next(a for a in inventory['assets'] if a['id'] == identity)
spec = importlib.util.spec_from_file_location('density_inspector', root / 'scripts/qa-shopping-mall-blender.py')
inspector = importlib.util.module_from_spec(spec); spec.loader.exec_module(inspector)
for name in inspector.MODULES:
    addon_utils.enable(name, default_set=True, persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(root / asset['source']), load_ui=False, use_scripts=False)
original = json.loads((out / 'blender' / (identity + '.json')).read_text())
names = {m['name'] for m in original['phases']['source']['meshes']
         if any(d['status'] != 'MEASURED' for d in m.get('density', []))}
depsgraph = bpy.context.evaluated_depsgraph_get()
prepared = []
for name in sorted(names):
    obj = bpy.data.objects[name]
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.transform(obj.matrix_world); mesh.update()
    area = sum(p.area for p in mesh.polygons)
    ngon_count = sum(len(p.vertices) > 4 for p in mesh.polygons)
    before = bpy.data.objects.new('QA_AreaDiagnosticOnly', mesh)
    bpy.context.scene.collection.objects.link(before)
    utils = importlib.import_module('bl_ext.user_default.texel_density_checker.utils')
    fan_area = sum(utils.calculate_geometry_areas(before))
    bpy.data.objects.remove(before, do_unlink=True)
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free(); mesh.update()
    prepared.append((name, mesh, area, ngon_count, fan_area))
scene = bpy.data.scenes.new('QA_TriangulatedDensityOnly'); bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1
rows = []
for name, mesh, before_area, ngons, fan_area in prepared:
    holder = bpy.data.objects.new(name + '_temporary', mesh); scene.collection.objects.link(holder)
    inspector.activate(holder)
    measured = []
    for index, mat in enumerate(mesh.materials):
        if not mat or not mat.use_nodes: continue
        for node in mat.node_tree.nodes:
            if node.type == 'TEX_IMAGE': measured.append(inspector.density_for_material(holder, index, node, scene))
    rows.append({'object': name, 'original_ngons': ngons, 'original_area_m2': before_area, 'native_fan_area_m2': fan_area,
                 'triangulated_area_m2': sum(p.area for p in mesh.polygons), 'measurements': measured})
result = {'status': 'MEASURED_DIAGNOSTIC', 'id': identity, 'method': 'Triangulate every face of each affected evaluated copy before both operator and independent area measurement; no source/export saved.', 'objects': rows}
(out / 'source-density-ngon-diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'objects':len(rows),'states':[d['status'] for r in rows for d in r['measurements']]}))

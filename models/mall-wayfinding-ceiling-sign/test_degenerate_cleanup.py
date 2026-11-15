"""Exercise fresh production generation, saved double-sided labels and canonical native import."""
from pathlib import Path
import bpy,hashlib,importlib.util,json,subprocess,sys
here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fresh_ceiling',here/'generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
from blender_degenerate_cleanup import geometry_counts,source_fingerprint
args=sys.argv[sys.argv.index('--')+1:];assert len(args)==1
out=Path(args[0]);out.mkdir(parents=True,exist_ok=False);g.HERE=out
for name in ('exports','sources','previews'):(out/name).mkdir()
g.build();source=out/'sources'/f'{g.ID}.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False)
root=bpy.data.collections[g.ROOT];objects=list(root.all_objects);assert len(objects)==75
assert set(g.GROUPS)=={c.name for c in root.children}
assert sum(r['zero_area_triangles'] for r in geometry_counts(objects))==0
fonts=[o for o in objects if o.type=='FONT'];assert len(fonts)==10
assert all(o.matrix_world.determinant()>.999 for o in fonts)
assert bpy.data.objects['Front_Shops_Label'].data.body=='SHOPS'
assert bpy.data.objects['Rear_Shops_Label'].data.body=='SHOPS'
fp=source_fingerprint();g.prepare_asset_geometry();assert source_fingerprint()==fp
assert all(sum(m.name=='Degenerate face cleanup' for m in o.modifiers)<=1 for o in objects)
exported=out/'exports/optimized.glb'
subprocess.run(['node',str(here.parents[1]/'scripts/check-degenerate-repair.mjs'),str(here/'exports/optimized.glb'),str(exported),str(out/'fresh-comparison.json'),'--allow-normal-drift'],check=True)
canonical=here/'exports/optimized.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(canonical))
rows=geometry_counts(list(bpy.context.scene.objects));assert sum(r['zero_area_triangles'] for r in rows)==0,rows
(out/'native-regression.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'editable_parts':75,'editable_labels':10,'idempotent_cleanup':True,'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),'canonical_import_zero_area_triangles':0,'canonical_import_triangles':sum(r['triangles'] for r in rows)},indent=2)+'\n')
print('PASS fresh generation, saved double-sided labels, idempotent cleanup and canonical native import')

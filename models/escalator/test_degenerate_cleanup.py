"""Native fresh-generation, animation preservation and import regression."""
from pathlib import Path
import bpy, hashlib, importlib.util, json, shutil, subprocess, sys
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parents[1]/'scripts'))
from blender_degenerate_cleanup import geometry_counts, source_fingerprint
from blender_animation_snapshot import animation_snapshot, action_curves
args=sys.argv[sys.argv.index('--')+1:];assert len(args)==1
out=Path(args[0]);out.mkdir(parents=True,exist_ok=False)
spec=importlib.util.spec_from_file_location('fresh_escalator',here/'generate.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
g.HERE=out
for name in ['sources','exports','previews']:(out/name).mkdir()
shutil.copyfile(here/'rail-profiles.json',out/'rail-profiles.json')
sys.argv=['test_degenerate_cleanup.py','--skip-render'];g.main()
source=out/'sources/escalator.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=False)
root=bpy.data.objects[g.ROOT];objects=list(root.children_recursive);assert len(objects)==200
assert sum(r['zero_area_triangles'] for r in geometry_counts(objects))==0
fingerprint=source_fingerprint();g.prepare_asset_geometry(g.SLUG,objects);assert source_fingerprint()==fingerprint
snapshot=animation_snapshot();assert (snapshot['actions'],snapshot['curves'],snapshot['keyframes'])==(60,420,466354)
key=action_curves(bpy.data.actions[0])[0].keyframe_points[0]
co=key.co.copy();left=key.handle_left.copy();right=key.handle_right.copy()
key.co.y+=.001;assert animation_snapshot()['sha256']!=snapshot['sha256'],'A real keyframe edit must be detected'
key.co=co;key.handle_left=left;key.handle_right=right
assert animation_snapshot()==snapshot
subprocess.run(['node',str(here.parents[1]/'scripts/check-degenerate-repair.mjs'),str(here/'exports/optimized.glb'),str(out/'exports/optimized.glb'),str(out/'fresh-comparison.json'),'--allow-normal-drift','--static-meshes-in-rigid-container'],check=True)
canonical=here/'exports/optimized.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(canonical))
rows=geometry_counts(list(bpy.context.scene.objects));assert sum(r['zero_area_triangles'] for r in rows)==0,rows
assert len(bpy.data.actions)==60
(out/'native-regression.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'editable_parts':200,'idempotent_cleanup':True,'animation_snapshot':snapshot,'keyframe_negative_control':True,'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),'canonical_import_zero_area_triangles':0,'canonical_import_actions':60,'canonical_import_triangles':sum(r['triangles'] for r in rows)},indent=2)+'\n')
print('PASS fresh escalator generation, 60 actions preserved, keyframe negative control and canonical native import')

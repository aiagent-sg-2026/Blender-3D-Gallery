"""Step 6 check: build Head + Eyes only, report, export a GLB for the Three.js morph test.
Run: blender --background --factory-startup --python-exit-code 1 --python models/chibi-mall-guide-v5/build_head.py -- OUT_DIR"""
import bpy, bmesh, sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import config as C, kit, garments, head as H
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mats = garments.make_materials(bpy)
head, eyes = H.build_head(bpy, bmesh, mats)
rep = dict(triangles={'Head': kit.tri_count(head), 'Eyes': kit.tri_count(eyes)},
           keys={'Head': [k.name for k in head.data.shape_keys.key_blocks], 'Eyes': [k.name for k in eyes.data.shape_keys.key_blocks]},
           materials={'Head': len(head.data.materials), 'Eyes': len(eyes.data.materials)})
glb = os.path.join(OUT, 'head.glb')
bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', export_morph=True, export_morph_normal=True, export_animations=False, export_yup=True)
rep['glb_bytes'] = os.path.getsize(glb)
json.dump(rep, open(os.path.join(OUT, 'head-report.json'), 'w'), indent=1); print('REPORT', json.dumps(rep))

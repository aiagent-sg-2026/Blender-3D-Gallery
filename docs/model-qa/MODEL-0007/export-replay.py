import bpy,hashlib,json,sys,runpy
from pathlib import Path
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()=='6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672'
root=bpy.data.objects['ASSET_Ball_01'];bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in root.children_recursive:ob.select_set(True)
root.location=(0,0,0)
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert out!=source.parent/'exports';out.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out/'ball_01.glb'),export_format='GLB',use_selection=True,export_apply=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672'

compare=runpy.run_path(str(Path(__file__).resolve().parents[3]/'scripts/glb-index-order-equivalence.py'))['compare_index_order_only']
result=compare((source.parent/'exports/ball_01.glb').read_bytes(),(out/'ball_01.glb').read_bytes())
(out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')

"""Replay one cue-ball export to a scratch directory without saving source."""
import bpy,hashlib,json,sys,struct
from pathlib import Path
source=Path(bpy.data.filepath);expected='6b06dedf3da537c411afc7c6c4589268fb6945e4dfd22e8af4ed35a5abc71672';assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();assert out!=source.parent/'exports';out.mkdir(parents=True,exist_ok=True)
root=bpy.data.objects['ASSET_Ball_00'];bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in root.children_recursive:ob.select_set(True)
root.location=(0,0,0)
bpy.ops.export_scene.gltf(filepath=str(out/'ball_00.glb'),export_format='GLB',use_selection=True,export_apply=True)
reference=(source.parent/'exports/ball_00.glb').read_bytes();actual=(out/'ball_00.glb').read_bytes()
def unpack(data):
    n=int.from_bytes(data[12:16],'little');return json.loads(data[20:20+n]),data[28+n:]
a,ab=unpack(reference);b,bb=unpack(actual);assert a==b,'Export JSON/identity/materials changed'
primitive=a['meshes'][0]['primitives'][0];assert primitive.get('mode',4)==4
accessor=a['accessors'][primitive['indices']];view=a['bufferViews'][accessor['bufferView']];size={5123:2,5125:4}[accessor['componentType']];assert view.get('byteStride',size)==size
start=view.get('byteOffset',0)+accessor.get('byteOffset',0);end=start+accessor['count']*size
assert len(ab)==len(bb) and ab[:start]==bb[:start] and ab[end:]==bb[end:],'Non-index payload changed'
fmt='<'+('H' if size==2 else 'I')*accessor['count']
def oriented(data):
    ids=struct.unpack_from(fmt,data,start);rows=[]
    for i in range(0,len(ids),3):
        x,y,z=ids[i:i+3];rows.append(min((x,y,z),(y,z,x),(z,x,y)))
    return sorted(rows)
assert oriented(ab)==oriented(bb),'Oriented geometry/UV/normal connectivity changed'

assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
(out/'results.json').write_text(json.dumps(dict(input_source_sha256=expected,output_sha256=hashlib.sha256(actual).hexdigest(),bytes=len(actual),exact_standalone_replay=actual==reference,semantic_standalone_replay=True,index_order_may_differ=True,oriented_triangle_count=len(oriented(ab)),all_non_index_binary_bytes_and_full_json_unchanged=True,source_and_product_files_unchanged=True),indent=2)+'\n')

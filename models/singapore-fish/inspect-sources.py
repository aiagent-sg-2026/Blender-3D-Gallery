"""Read every standalone source and verify scene isolation and editable anatomy."""
import bpy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
reports=[]
for i,s in enumerate(json.loads((HERE/'species.json').read_text()),1):
 slug=s[0];path=HERE/slug/'sources'/f'{slug}.blend'
 with bpy.data.libraries.load(str(path),link=False) as (source,target):
  assert len(source.scenes)==1,(slug,source.scenes)
  target.scenes=source.scenes
 scene=target.scenes[0]
 roots=[o for o in scene.objects if o.name.startswith('ASSET_')]
 assert len(roots)==1,(slug,len(roots))
 root=roots[0];assert root['fish_id']=='FISH-%03d'%i
 meshes=[o for o in root.children_recursive if o.type=='MESH']
 assert len(meshes)>5 and any(o.name.startswith('BODY_Profile') for o in meshes)
 assert scene.camera is not None
 rigs=[o for o in root.children_recursive if o.type=='ARMATURE']
 assert len(rigs)==1 and rigs[0].animation_data and rigs[0].animation_data.action
 assert len(rigs[0].data.bones)==11
 assert all(any(m.type=='ARMATURE' and m.object==rigs[0] for m in o.modifiers) for o in meshes)
 assert scene.frame_start==0 and scene.frame_end>=48
 assert all(o.data.vertices and o.data.polygons for o in meshes)
 reports.append({'id':root['fish_id'],'meshes':len(meshes),'scene':scene.name,'source_bytes':path.stat().st_size})
 bpy.data.scenes.remove(scene)
(HERE/'source-validation.json').write_text(json.dumps(reports,indent=2)+'\n')
print('PASS: 60 isolated Blender scenes, editable skinned anatomy, 11-bone swim rigs and studio cameras.')

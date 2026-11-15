"""Reimport delivery GLBs and measure actual animated geometry, including morphs."""
import bpy,json,hashlib,math,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'fish-realism-qa'))
from fin_attachment import check_surface_contact
manifest=json.loads((HERE/'releases.json').read_text())
profiles=json.loads((HERE.parent/'fish-realism-qa'/'profiles.json').read_text())
results=[]
for directory in sorted(HERE.iterdir()):
 file=directory/'model.glb'
 if not file.exists():continue
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(file));s=bpy.context.scene
 actions=list(bpy.data.actions);assert actions,directory.name
 end=max(a.frame_range.y for a in actions);start=min(a.frame_range.x for a in actions);meshes=[o for o in s.objects if o.type=='MESH'];poses=[]
 for frame in [start,start+(end-start)*.25,end]:
  s.frame_set(int(frame),subframe=frame-int(frame));dg=bpy.context.evaluated_depsgraph_get();positions=[]
  for o in meshes:
   ev=o.evaluated_get(dg);positions.extend(ev.matrix_world@v.co for v in ev.data.vertices)
  assert all(math.isfinite(c) for v in positions for c in v);poses.append(positions)
 motion=max((a-b).length for a,b in zip(poses[0],poses[1]));loop=max((a-b).length for a,b in zip(poses[0],poses[2]));assert motion>.001
 # Betta inherits a small nonzero endpoint difference from the licensed original.
 assert loop<(.01 if directory.name=='betta' else .0001),(directory.name,loop)
 contacts=[]
 if manifest['models'][directory.name].get('surface_contact_qa'):
  for frame in [start,start+(end-start)*.25,start+(end-start)*.50,start+(end-start)*.75,end]:
   s.frame_set(int(frame),subframe=frame-int(frame));contacts.append({'frame':frame,'fins':check_surface_contact(s)})
 profile=profiles.get(directory.name,{});expected_barbels=2*len(profile.get('barbels',[]));barbels=[o for o in meshes if o.name.startswith('Barbel_')];assert len(barbels)==expected_barbels,(directory.name,'Delivery mouth-barbel count',len(barbels),expected_barbels)
 adipose=[o for o in meshes if o.name.startswith('Dorsal_AdiposeFin')];assert len(adipose)==(1 if profile.get('adipose_fin') else 0),(directory.name,'Delivery adipose-fin count')
 results.append({'barbel_meshes':len(barbels),'adipose_fins':len(adipose),'surface_contact':contacts,'slug':directory.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'vertices':len(poses[0]),'actions':[a.name for a in actions],'start':start,'end':end,'motion':motion,'loop_error':loop})
(HERE/'motion-verification.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS delivery deformation',len(results))

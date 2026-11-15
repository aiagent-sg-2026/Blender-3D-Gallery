"""Reimport delivery GLBs and measure actual animated geometry, including morphs."""
import bpy,json,hashlib,math,sys,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'fish-realism-qa'))
from fin_attachment import check_surface_contact
manifest=json.loads((HERE/'releases.json').read_text())
profiles=json.loads((HERE.parent/'fish-realism-qa'/'profiles.json').read_text())
report=HERE/'motion-verification.json'
previous={row['slug']:row for row in json.loads(report.read_text())} if report.exists() else {}
selected=set(filter(None,os.environ.get('FISH_SLUGS','').split(',')))
assert selected.issubset(manifest['models']),('Unknown selected fish',selected-set(manifest['models']))
def verifier_signature():
 return hashlib.sha256(b'\0'.join([Path(__file__).read_bytes(),(HERE.parent/'fish-realism-qa'/'fin_attachment.py').read_bytes(),bpy.app.version_string.encode()])).hexdigest()
signature=verifier_signature();results=[];checked=[];reused=[]
for directory in sorted(HERE.iterdir()):
 file=directory/'model.glb'
 if not file.exists():continue
 digest=hashlib.sha256(file.read_bytes()).hexdigest();profile=profiles.get(directory.name,{})
 profile_signature=hashlib.sha256(json.dumps(profile,sort_keys=True).encode()).hexdigest();prior=previous.get(directory.name,{})
 # Retain only evidence from the identical verifier, profile and actual GLB bytes.
 if selected and directory.name not in selected and prior.get('sha256')==digest and prior.get('verifier_signature')==signature and prior.get('profile_signature')==profile_signature:
  assert prior['motion']>.001 and prior['loop_error']<(.01 if directory.name=='betta' else .0001)
  if manifest['models'][directory.name].get('surface_contact_qa'):assert len(prior['surface_contact'])==5
  results.append({**prior,'verification_reused':True});reused.append(directory.name);continue
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(file));s=bpy.context.scene
 actions=list(bpy.data.actions);assert actions,directory.name
 end=max(a.frame_range.y for a in actions);start=min(a.frame_range.x for a in actions);meshes=[o for o in s.objects if o.type=='MESH'];poses=[];sensory_poses=[]
 for frame in [start,start+(end-start)*.25,end]:
  s.frame_set(int(frame),subframe=frame-int(frame));dg=bpy.context.evaluated_depsgraph_get();positions=[];sensory={}
  for o in meshes:
   ev=o.evaluated_get(dg);positions.extend(ev.matrix_world@v.co for v in ev.data.vertices)
   if o.name.startswith('Pelvic_Filament_'):sensory[o.name]=[ev.matrix_world@v.co for v in ev.data.vertices]
  assert all(math.isfinite(c) for v in positions for c in v);poses.append(positions);sensory_poses.append(sensory)
 motion=max((a-b).length for a,b in zip(poses[0],poses[1]));loop=max((a-b).length for a,b in zip(poses[0],poses[2]));assert motion>.001
 # Betta inherits a small nonzero endpoint difference from the licensed original.
 assert loop<(.01 if directory.name=='betta' else .0001),(directory.name,loop)
 contacts=[]
 if manifest['models'][directory.name].get('surface_contact_qa'):
  for frame in [start,start+(end-start)*.25,start+(end-start)*.50,start+(end-start)*.75,end]:
   s.frame_set(int(frame),subframe=frame-int(frame));contacts.append({'frame':frame,'fins':check_surface_contact(s)})
 expected_barbels=2*len(profile.get('barbels',[]));barbels=[o for o in meshes if o.name.startswith('Barbel_')];assert len(barbels)==expected_barbels,(directory.name,'Delivery mouth-barbel count',len(barbels),expected_barbels)
 adipose=[o for o in meshes if o.name.startswith('Dorsal_AdiposeFin')];assert len(adipose)==(1 if profile.get('adipose_fin') else 0),(directory.name,'Delivery adipose-fin count')
 sensory_motion={name:max((a-b).length for a,b in zip(points,sensory_poses[1][name])) for name,points in sensory_poses[0].items()};assert len(sensory_motion)==(2 if profile.get('pelvic_filaments') else 0) and all(value>.001 for value in sensory_motion.values()),(directory.name,'Delivery pelvic sensory-ray motion')
 assert hashlib.sha256(file.read_bytes()).hexdigest()==digest,('GLB changed during verification',directory.name)
 checked.append(directory.name);results.append({'verifier_signature':signature,'profile_signature':profile_signature,'verification_reused':False,'pelvic_sensory_motion':sensory_motion,'barbel_meshes':len(barbels),'adipose_fins':len(adipose),'surface_contact':contacts,'slug':directory.name,'sha256':digest,'vertices':len(poses[0]),'actions':[a.name for a in actions],'start':start,'end':end,'motion':motion,'loop_error':loop})
assert verifier_signature()==signature,'Verifier changed during execution'
report.write_text(json.dumps(results,indent=2)+'\n')
print('PASS delivery deformation',len(results),'measured',len(checked),'retained',len(reused))

"""Check preservation, real morph motion, loop closure and longitudinal wave timing."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'stingray'

def check_scene(label):
 s=bpy.context.scene;disc=bpy.data.objects.get('Maskray_ContinuousDisc');assert disc,label
 samples=[];head=[];front=[];rear=[]
 base=disc.data.vertices;rest=[disc.matrix_world@v.co for v in base]
 def nearest(x,y):return min(range(len(base)),key=lambda i:(rest[i].x-x)**2+(rest[i].y-y)**2)
 fi=nearest(-.60,-.67);ri=nearest(.0,-1.10);ci=nearest(-.65,0)
 for f in range(1,98):
  s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();o=disc.evaluated_get(dg);p=[o.matrix_world@v.co for v in o.data.vertices]
  assert all(all(math.isfinite(x) for x in v) for v in p),(label,f)
  if f in [1,25,49,73,97]:samples.append(p)
  front.append(p[fi].z);rear.append(p[ri].z);head.append(p[ci].z)
 motion=max((a-b).length for a,b in zip(samples[0],samples[1]));loop=max((a-b).length for a,b in zip(samples[0],samples[-1]));assert motion>.03,(label,motion);assert loop<.0001,(label,loop)
 front_peak=max(range(96),key=lambda i:front[i]);rear_peak=max(range(96),key=lambda i:rear[i]);lag=(rear_peak-front_peak)%96
 expected_lag=(rest[ri].x-rest[fi].x)/2.24*1.05*96
 assert abs(lag-expected_lag)<2,(label,lag,expected_lag);assert max(head)-min(head)<.001,(label,head)
 t=max(0,min(1,(abs(rest[fi].y)-.25)/.95));span=t*t*(3-2*t);envelope=math.sin(math.pi*max(.001,min(.999,(rest[fi].x+1.21)/2.24)))**.60;expected_amplitude=.245*span**1.5*envelope;observed_amplitude=(max(front)-min(front))/2;assert abs(expected_amplitude-observed_amplitude)<.001,(label,expected_amplitude,observed_amplitude)
 keys=[o for o in s.objects if o.type=='MESH' and o.data.shape_keys];assert len(keys)>=2
 return {'stage':label,'disc_vertices':len(base),'front_probe':list(rest[fi]),'rear_probe':list(rest[ri]),'morph_meshes':len(keys),'max_disc_displacement':motion,'loop_endpoint_distance':loop,'front_peak_frame':front_peak+1,'rear_peak_frame':rear_peak+1,'rear_lag_frames':lag,'expected_rear_lag_frames':expected_lag,'front_amplitude':observed_amplitude,'expected_front_amplitude':expected_amplitude,'head_vertical_range':max(head)-min(head),'packed_textures':all(i.packed_file for i in bpy.data.images if i.source=='FILE'),'probe_signals':{'front':front,'rear':rear}}

bpy.ops.wm.open_mainfile(filepath=str(OUT/'stingray-review.blend'));source=check_scene('blend_source')
bpy.ops.wm.read_factory_settings(use_empty=True);path=OUT/'stingray-review.glb';bpy.ops.import_scene.gltf(filepath=str(path));export=check_scene('glb_reimport');assert len(bpy.data.actions)==1,[a.name for a in bpy.data.actions]
source_signals=source.pop('probe_signals');export_signals=export.pop('probe_signals');roundtrip_error=max(abs(a-b) for key in source_signals for a,b in zip(source_signals[key],export_signals[key]));assert roundtrip_error<.0001,roundtrip_error
guard=json.loads((HERE/'preserved-assets.json').read_text());changed=[p for p,h in guard.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h];assert not changed,changed
report={'roundtrip_probe_error':roundtrip_error,'source_sha256':hashlib.sha256((OUT/'stingray-review.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':source,'export':export,'exported_actions':[a.name for a in bpy.data.actions],'preserved_files':len(guard),'changed_preserved_files':changed,'limits':['Artistic realism requires owner review.','No production replacement or deployed browser validation.']};(HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('VERIFIED',json.dumps(report),flush=True)

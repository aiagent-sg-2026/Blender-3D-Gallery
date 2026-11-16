"""Repair the previously fixed pelvic-base coordinate without rebuilding other geometry."""
import bpy,json,sys,hashlib,re,importlib.util
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;slug=sys.argv[sys.argv.index('--')+1];assert re.fullmatch('[a-z0-9-]+',slug) and slug not in ['barramundi','betta','stingray'];OUT=HERE/slug;source=OUT/(slug+'.blend');old_hash=hashlib.sha256(source.read_bytes()).hexdigest();C=json.loads((HERE/'profiles.json').read_text())[slug]
spec=importlib.util.spec_from_file_location('contact_profile_utils',HERE.parent/'fish-realism-review/revision-02/create_review.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
def profile(x):return [R.B.interp(list(zip(C['profile_x'],C[key])),x) for key in ['top','bottom','width']]
sys.path.insert(0,str(HERE));from fin_attachment import repair_pelvic_roots,check_surface_contact
from fin_weights import attach_fin_roots
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;repaired=repair_pelvic_roots(s,profile);assert len(repaired)==2,(slug,repaired);attach_fin_roots(s)
contacts=[]
for frame in [1,1+(s.frame_end-1)//4,s.frame_end]:s.frame_set(frame);contacts.append({'frame':frame,'fins':check_surface_contact(s)})
s.frame_set(13);s.render.filepath=str(OUT/'preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(source));bpy.ops.render.render(write_still=True)
camera=s.camera;camera.location=(-1.15,-7,.55);camera.rotation_euler=(Vector((-1.03,0,.02))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.65;s.render.filepath=str(OUT/'head-detail.png');bpy.ops.render.render(write_still=True)
camera.location=(-.4,-4,-1.7);camera.rotation_euler=(Vector((-.4,0,profile(-.4)[1]+.03))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.45;s.render.filepath=str(OUT/'pelvic-detail.png');bpy.ops.render.render(write_still=True)
if C.get('pectoral_filaments'):
 camera.location=(-.2,-7,.25);camera.rotation_euler=(Vector((-.35,0,-.27))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.5;s.render.filepath=str(OUT/'filament-detail.png');bpy.ops.render.render(write_still=True)
qa=json.loads((OUT/'qa.json').read_text());qa['status']='revise';qa.setdefault('attachment_revisions',[]).append({'prior_source_sha256':old_hash,'finding':'Fixed paired pelvic-base coordinate lay outside the curved skin despite correct dynamic weights','repair':'Only pelvic mesh bases reprojected onto an embedded ventrolateral root curve; body, materials and actions retained','repaired_meshes':repaired});qa['visual_checks']['surface_contact']='pending: inspect updated overall and ventral detail, then validate new exported geometry';(OUT/'qa.json').write_text(json.dumps(qa,indent=2)+'\n');(OUT/'attachment-repair.json').write_text(json.dumps({'slug':slug,'prior_source_sha256':old_hash,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'repaired':repaired,'source_contacts':contacts},indent=2)+'\n')
queue=json.loads((HERE/'queue.json').read_text());item=next(x for x in queue['items'] if x['slug']==slug);item['status']='revising_surface_contact';item['checks']['surface_contact']='pending';(HERE/'queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
print('REPAIRED',slug,repaired,flush=True)

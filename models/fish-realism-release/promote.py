"""Copy sealed original fish artwork and prepare its approved catalog override."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--from-root',type=Path,required=True);parser.add_argument('slugs',nargs='+');args=parser.parse_args();source_root=args.from_root.resolve()
if source_root==REPO:parser.error('Use a separate authoring checkout as --from-root.')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_queue=read(source_root/'models/fish-realism-qa/queue.json');approved={x['slug']:x for x in source_queue['items'] if x['status']=='qa_pass'}
prepared=[]
for slug in args.slugs:
 assert re.fullmatch('[a-z0-9-]+',slug) and slug in approved,('Not sealed by QA',slug)
 source=source_root/'models/fish-realism-qa'/slug;artifact=read(source/'artifacts.json');qa=read(source/'qa.json');motion=read(source/'motion-verification.json');browser=read(source/'browser-verification.json');validation=read(source/'gltf-validation.json')
 for name,expected in artifact['files'].items():
  assert Path(name).name==name and sha(source/name)==expected,('Artifact hash mismatch',slug,name)
 assert qa['reviewed_source_sha256']==sha(source/(slug+'.blend'))==motion['source_sha256']
 assert motion['glb_sha256']==sha(source/'model.glb')
 for label in ['source','export']:assert len(motion[label].get('surface_contact',[]))==5,('Posed fin contact QA required',slug,label)
 assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
 assert [r['width'] for r in browser['results']]==[1440,390]
 assert all(r['loaded_draft_sha256']==motion['glb_sha256'] and r['visible_swim_change'] and r['paused_stable'] and r['viewer_disposed'] and r['no_page_errors'] for r in browser['results'])
 assert all(value.startswith('pass:') for value in qa['visual_checks'].values())
 prepared.append((slug,source,artifact,read(source/'profile-snapshot.json')))

manifest=read(HERE/'releases.json');queue=read(REPO/'models/fish-realism-qa/queue.json');profiles=read(REPO/'models/fish-realism-qa/profiles.json')
for slug,source,artifact,profile in prepared:
 target=REPO/'models/fish-realism-qa'/slug;target.mkdir(exist_ok=True)
 for name in [*artifact['files'],'artifacts.json']:shutil.copy2(source/name,target/name)
 screen=REPO/'output/playwright/fish-realism-qa'/slug;screen.mkdir(parents=True,exist_ok=True)
 for name in ['desktop.png','mobile.png']:shutil.copy2(source_root/'output/playwright/fish-realism-qa'/slug/name,screen/name)
 profiles[slug]=profile
 queue['items']=[approved[slug] if item['slug']==slug else item for item in queue['items']]
 source_path=f'models/fish-realism-qa/{slug}/{slug}.blend';notes=f"Photo-informed original artwork: {profile['visual_species']}. Animated tail and fins; not a scanned specimen or taxonomic identification model."
 if profile.get('alias_note'):notes+=' '+profile['alias_note']
 item={'source':source_path,'preview':f'models/fish-realism-qa/{slug}/preview.png','acceptance':'agent_qa_pass','surface_contact_qa':'posed_source_glb_and_delivery_v1','license':'Original project geometry and textures; reuse in the owner’s projects authorized. Public redistribution terms not specified.','description':profile['fish_id']+'. Photo-informed Blender fish with looping swimming animation.'};manifest['models'][slug]=item
 out=HERE/slug;out.mkdir(exist_ok=True)
 display={'previewRotationY':0,'previewCameraDirection':profile.get('preview_camera_direction',[.12,.28,1]),'studioEnvironment':True,'environmentIntensity':.3,'textureAnisotropy':8,'previewLighting':{'hemisphereIntensity':.8,'directionalIntensity':1.4}}
 metadata={'id':'fish-'+slug,'source':source_path,'visual_species':profile['visual_species'],'accuracy_notes':notes,'display':display,'attribution':[{'credit':'Original Blender geometry and textures for this gallery. Reference photos guide appearance and are not embedded.'}]}
 (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 image=Image.open(source/'preview.png');image.thumbnail((560,420));image.save(out/'thumbnail.webp',quality=88)
for path,data in [(HERE/'releases.json',manifest),(REPO/'models/fish-realism-qa/queue.json',queue),(REPO/'models/fish-realism-qa/profiles.json',profiles)]:path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print('Prepared sealed artwork:',', '.join(args.slugs),'; export and browser release checks remain required.')

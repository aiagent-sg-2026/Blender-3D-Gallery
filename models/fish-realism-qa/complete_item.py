"""Seal one visually reviewed fish only after real artifact/browser gates pass."""
import sys,re,json,hashlib,subprocess,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];slug=sys.argv[1];assert re.fullmatch('[a-z0-9-]+',slug);OUT=HERE/slug
qa=json.loads((OUT/'qa.json').read_text());source_hash=hashlib.sha256((OUT/(slug+'.blend')).read_bytes()).hexdigest();assert qa['reviewed_source_sha256']==source_hash,'Visual review belongs to an older scene';assert all(v.startswith('pass:') for v in qa['visual_checks'].values())
subprocess.run(['node',str(HERE/'validate.mjs'),slug],cwd=REPO,check=True)
frames=OUT/'frames';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','12','-i',str(frames/'%03d.png'),'-filter_complex','[0:v]split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a',str(OUT/'swim.gif')],check=True)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,duration','-of','json',str(OUT/'swim.gif')]))['streams'][0];motion=json.loads((OUT/'motion-verification.json').read_text());span=motion['source']['frames'][-1]-1;duration=span/24;assert int(info['nb_read_frames'])==span//2 and abs(float(info['duration'])-duration)<.02
profiles=json.loads((HERE/'profiles.json').read_text());(OUT/'profile-snapshot.json').write_text(json.dumps(profiles[slug],indent=2)+'\n')
manifest={'slug':slug,'gif':info,'texture_cache':'Optional generated PNG cache is not required; source .blend and GLB contain packed textures.','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='artifacts.json' and not p.name.endswith('.blend1')}};(OUT/'artifacts.json').write_text(json.dumps(manifest,indent=2)+'\n')
q=json.loads((HERE/'queue.json').read_text());item=next(x for x in q['items'] if x['slug']==slug);item['status']='qa_pass';item['checks']={**{k:'pass' for k in item['checks']},'browser':'pass'};item['artifact_manifest']=str((OUT/'artifacts.json').relative_to(REPO));(HERE/'queue.json').write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n')
shutil.rmtree(frames)
for p in OUT.glob('*.blend1'):p.unlink()
print('COMPLETE',slug,f'QA, source, GLB, desktop/mobile browser and {duration:g}-second GIF')

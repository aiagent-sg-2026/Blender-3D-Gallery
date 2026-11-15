set -e
python3 - <<'PREFLIGHT'
from pathlib import Path
import subprocess
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='deafc76cd3d9146c6aee4e6246ac683f24c7a74a'
assert not subprocess.check_output(['git','diff','--name-only','--','src','scripts','models','public','data','package.json','package-lock.json','index.html','vite.config.js'],text=True).strip()
assert not Path('output/model0012-upstream-486').exists()
PREFLIGHT
git fetch --depth=100 --filter=blob:none origin 486fb02b027c2a178e9e718421060a0f64d2550d
git merge-base --is-ancestor HEAD FETCH_HEAD
git merge --ff-only --quiet FETCH_HEAD
mkdir -p output/model0012-upstream-486
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/model0012-upstream-486/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/model0012-upstream-486/build.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - > output/model0012-upstream-486/runtime.log 2>&1 <<'JS'
import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {spawn} from 'node:child_process';import {serveBuild} from './scripts/browser-test-utils.mjs';
const base='output/model0012-upstream-486',slugs=['rabbitfish','red-seabream','croaker'];
const assets=JSON.parse(await fs.readFile('models/catalog.json','utf8')).collections.flatMap(c=>c.assets);assert.equal(assets.length,567);
const child=async(script,env)=>new Promise((resolve,reject)=>{const p=spawn(process.execPath,[script],{stdio:'inherit',env:{...process.env,...env}});p.once('error',reject);p.once('exit',(code,signal)=>code===0?resolve():reject(new Error(script+' '+code+' '+signal)));});
const server=await serveBuild(),records=[];
try{
 for(const id of [...slugs.map(s=>'fish-'+s),'gjh-m057-premium-wall-shelf-corner']){const destination=base+'/'+id;
  await child('scripts/test-model-qa-browser.mjs',{MODEL_QA_ID:id,MODEL_QA_URL:server.url,MODEL_QA_OUTPUT:destination,MODEL_QA_INCLUDE_MOBILE:'0',MODEL_QA_REDUCED_MOTION:id.startsWith('fish-')?'1':'0'});
  const profiles=JSON.parse(await fs.readFile(destination+'/results.json','utf8'));assert.equal(profiles.length,2);
  const asset=assets.find(a=>a.id===id);assert.ok(asset);const original=await fs.readFile(asset.file),digest=createHash('sha256').update(original).digest('hex');assert.ok(profiles.every(p=>p.status==='PASS'&&p.modelId===id&&p.assetSha256===digest&&p.errors.length===0&&p.networkErrors.length===0));
  const url=profiles[0].metrics.resources[0].url,response=await fetch(url);assert.equal(response.status,200);const payload=Buffer.from(await response.arrayBuffer());assert.equal(payload.length,original.length);assert.equal(createHash('sha256').update(payload).digest('hex'),digest);
  records.push({id,profiles:2,reduced_motion:id.startsWith('fish-'),url,decoded_bytes:payload.length,sha256:digest,download_verified:true});
 }
 await child('scripts/test-gjh-m057-browser.mjs',{MALL_QA_DIR:base+'/m057-gallery'});
 const gallery=JSON.parse(await fs.readFile(base+'/m057-gallery/results.json','utf8'));assert.equal(gallery.results.length,3);assert.ok(gallery.results.every(r=>r.passed&&r.resetMatchesInitial&&r.reopenMatchesInitial&&r.closeStopsRendering&&r.requestConsolePageErrors.length===0));
 for(const name of ['corner-controls-lods-and-ownership','corner-touch-viewport']){
  const destination=base+'/shelf-'+name;
  await child('scripts/test-shelf-inspector-browser.mjs',{TEST_ARTIFACT_DIR:destination,SHELF_TEST:name});
  const cases=JSON.parse(await fs.readFile(destination+'/results.json','utf8'));assert.equal(cases.results.length,1);assert.equal(cases.results[0].name,name);assert.equal(cases.results[0].status,'PASS');
 }
 await child('models/fish-realism-release/test-browser.mjs',{FISH_LIVE_URL:server.url,FISH_SLUGS:slugs.join(','),FISH_BATCH:'model0012-upstream486',FISH_ENGINE:''});
 const fish=JSON.parse(await fs.readFile('models/fish-realism-release/live-all-model0012-upstream486-browser-verification.json','utf8'));assert.equal(fish.results.length,12);
 for(const r of fish.results){assert.ok(r.paused_stable&&r.visible_swim_change&&r.resumed_then_paused&&r.no_horizontal_overflow&&r.no_page_errors&&r.viewer_disposed);assert.ok(['chromium','webkit'].includes(r.engine));assert.equal(r.loaded_release_sha256,records.find(x=>x.id==='fish-'+r.slug).sha256);}
 await fs.writeFile(base+'/fish-motion-results.json',JSON.stringify(fish,null,2)+'\n');await fs.writeFile(base+'/acceptance.json',JSON.stringify({source_sha:'486fb02b027c2a178e9e718421060a0f64d2550d',catalog_entries:567,static_camera_profiles:8,fish_animation_profiles:12,m057_original_gallery_profiles:3,m057_original_shelf_cases:2,all_original_camera_assertions_retained:true,fish_protocol_original:true,fish_protocol_server:'provided local build URL; output mode live is not production',records},null,2)+'\n');
}finally{await server.close();}
JS
python3 - <<'PACKAGE'
from pathlib import Path
import json,hashlib,subprocess,tarfile
base=Path('output/model0012-upstream-486');head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='486fb02b027c2a178e9e718421060a0f64d2550d'
assert not subprocess.check_output(['git','diff','--name-only','--','src','scripts','models','public','data','package.json','package-lock.json','index.html','vite.config.js'],text=True).strip()
inputs={p for p in subprocess.check_output(['git','diff','--name-only','deafc76cd3d9146c6aee4e6246ac683f24c7a74a',head],text=True).splitlines() if p.startswith(('src/','scripts/','models/','public/','data/')) or p in ['package.json','package-lock.json','index.html','vite.config.js']}
for p in ['scripts/test-model-qa-browser.mjs','scripts/browser-test-utils.mjs','models/fish-realism-release/test-browser.mjs','models/fish-realism-qa/browser-runtime.mjs','scripts/test-gjh-m057-browser.mjs','scripts/test-shelf-inspector-browser.mjs']:inputs.add(p)
(base/'source-manifest.json').write_text(json.dumps({'source_sha':head,'basis_sha':'deafc76cd3d9146c6aee4e6246ac683f24c7a74a','scope':'All changed runtime files plus executed browser scripts; excluded historical output captures are not runtime inputs.','checked_out_files':[{'path':p,'bytes':Path(p).stat().st_size,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in sorted(inputs)]},indent=2)+'\n')
files=[p for p in base.rglob('*') if p.is_file() and (p.suffix!='.png' or p.name.endswith(('-loaded.png','-initial.png','-page.png')) or 'shelf-' in str(p))]
for r in json.loads((base/'fish-motion-results.json').read_text())['results']:files.append(Path(r['screenshot']))
assert len(list(base.glob('fish-*/results.json')))==3 and (base/'gjh-m057-premium-wall-shelf-corner/results.json').exists() and len(set(map(str,files)))==len(files)
(base/'evidence-manifest.json').write_text(json.dumps({'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2)+'\n');files.append(base/'evidence-manifest.json')
with tarfile.open('model0012-upstream-486-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('model0012-upstream-486-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PACKAGE

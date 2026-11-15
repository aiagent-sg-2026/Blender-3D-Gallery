set -e
python3 - <<'PREFLIGHT'
from pathlib import Path
import subprocess,json,shutil
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='2b8097334caf15fb18543c8982481c2d9f196b6d'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
base=Path('output/upstream-2b-motion-aware');assert not base.exists()
for slug in ['silver-pomfret','black-pomfret','indian-mackerel','spanish-mackerel','scad','yellowtail-scad']:
    for engine in ['chromium','webkit']:assert not (Path('output/playwright/fish-realism-release/live')/engine/slug).exists()
base.mkdir(parents=True);shutil.copytree('output/upstream-2b809733',base/'first-attempt')
(base/'first-attempt/failure.json').write_text(json.dumps({'job_id':'2b3859fa-c617-4674-b529-3b42836e97f2','status':'FAILED','profiles_passed':0,'observed_assertion':'Reset must restore the original static model view','setup_mismatch':'Generic exact screenshot comparisons were applied while the fish automatically swims under the default motion preference. src/fish-motion.js defaults playing to !prefers-reduced-motion; viewer reset changes the camera, not swim time.','correction':'Opt in to reduced motion for fixed-pose camera checks, retaining every original assertion. Separately execute original fish playback/pause/visible-motion tests on both engines.'},indent=2)+'\n')
PREFLIGHT
# Apply only the reviewed optional media preference patch; keep all assertions.
python3 - <<'PATCH_HARNESS'
from pathlib import Path
import hashlib,subprocess
p=Path('scripts/test-model-qa-browser.mjs');assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p)])
old="    const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: 'block', hasTouch: width === 390 });"
new="    // Exact reset screenshots need a fixed pose; exercise motion separately.\n    const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: 'block', hasTouch: width === 390,\n      ...(process.env.MODEL_QA_REDUCED_MOTION === '1' ? { reducedMotion: 'reduce' } : {}) });"
s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new));assert hashlib.sha256(p.read_bytes()).hexdigest()=='fcf6c5e60899d310d078ade42038ca16b913613bb60c8e4c181241304ce15ae3'
PATCH_HARNESS
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" --check scripts/test-model-qa-browser.mjs
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/upstream-2b-motion-aware/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/upstream-2b-motion-aware/build.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - > output/upstream-2b-motion-aware/runtime.log 2>&1 <<'JS'
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {chromium} from 'playwright';
import {serveBuild,launchOptions} from './scripts/browser-test-utils.mjs';
const base='output/upstream-2b-motion-aware',slugs=['silver-pomfret','black-pomfret','indian-mackerel','spanish-mackerel','scad','yellowtail-scad'];
const ids=[...slugs.map(s=>'fish-'+s),'mall-floor-direction-sign','ball-05','eight-ball-billiards'];
const catalog=JSON.parse(await fs.readFile('models/catalog.json','utf8')),assets=catalog.collections.flatMap(c=>c.assets);assert.equal(assets.length,567);
const child=async(script,env)=>new Promise((resolve,reject)=>{const p=spawn(process.execPath,[script],{stdio:'inherit',env:{...process.env,...env}});p.once('error',reject);p.once('exit',(code,signal)=>code===0?resolve():reject(new Error(script+' '+code+' '+signal)));});
const server=await serveBuild(),records=[];
try{
 const browser=await chromium.launch(launchOptions);
 try{
  const context=await browser.newContext({viewport:{width:1440,height:900},serviceWorkers:'block',reducedMotion:'no-preference'}),page=await context.newPage();
  await page.goto(server.url+'?model=fish-silver-pomfret');const button=page.locator('[data-fish-playback]');await button.waitFor({timeout:60000});await page.waitForFunction(()=>document.querySelector('#viewport canvas')&&document.querySelector('#viewer-status')?.textContent==='');
  assert.equal(await button.getAttribute('aria-pressed'),'true');const canvas=page.locator('#viewport canvas');await page.waitForTimeout(200);const moving=await canvas.screenshot();await page.waitForTimeout(200);assert.ok(!moving.equals(await canvas.screenshot()),'Default autoplay must visibly change the canvas');
  await button.click();await page.waitForTimeout(150);const paused=await canvas.screenshot({path:base+'/paused-probe.png'});await page.waitForTimeout(150);assert.ok(paused.equals(await canvas.screenshot()),'Paused pose must be stable');await fs.writeFile(base+'/motion-preflight.json',JSON.stringify({default_autoplay:true,default_visible_motion:true,pause_stable:true,source:'actual current gallery and GLB',server_url:server.url},null,2)+'\n');await context.close();
 }finally{await browser.close();}
 for(const id of ids){
  const destination=base+'/'+id,frozen=id.startsWith('fish-');
  await child('scripts/test-model-qa-browser.mjs',{MODEL_QA_ID:id,MODEL_QA_URL:server.url,MODEL_QA_OUTPUT:destination,MODEL_QA_INCLUDE_MOBILE:'0',MODEL_QA_REDUCED_MOTION:frozen?'1':'0'});
  const profiles=JSON.parse(await fs.readFile(destination+'/results.json','utf8'));assert.equal(profiles.length,2);
  const asset=assets.find(a=>a.id===id),original=await fs.readFile(asset.file),digest=createHash('sha256').update(original).digest('hex');assert.ok(profiles.every(p=>p.status==='PASS'&&p.modelId===id&&p.assetSha256===digest&&p.errors.length===0&&p.networkErrors.length===0));
  const url=profiles[0].metrics.resources[0].url,response=await fetch(url);assert.equal(response.status,200);const payload=Buffer.from(await response.arrayBuffer());assert.equal(payload.length,original.length);assert.equal(createHash('sha256').update(payload).digest('hex'),digest);
  records.push({id,profiles:2,reduced_motion:frozen,url,decoded_bytes:payload.length,sha256:digest,download_verified:true});
 }
 // Use the original fish protocol with a supplied LOCAL build URL so its
 // captures use an unoccupied output folder. This is not production acceptance.
 await child('models/fish-realism-release/test-browser.mjs',{FISH_LIVE_URL:server.url,FISH_SLUGS:slugs.join(','),FISH_BATCH:'model0011-upstream2b',FISH_ENGINE:''});
 const fish=JSON.parse(await fs.readFile('models/fish-realism-release/live-all-model0011-upstream2b-browser-verification.json','utf8'));assert.equal(fish.results.length,24);
 for(const r of fish.results){assert.ok(r.paused_stable&&r.visible_swim_change&&r.resumed_then_paused&&r.no_horizontal_overflow&&r.no_page_errors&&r.viewer_disposed);assert.ok(['chromium','webkit'].includes(r.engine));assert.equal(r.loaded_release_sha256,records.find(x=>x.id==='fish-'+r.slug).sha256);}
 await fs.writeFile(base+'/fish-motion-results.json',JSON.stringify(fish,null,2)+'\n');await fs.writeFile(base+'/acceptance.json',JSON.stringify({source_sha:'2b8097334caf15fb18543c8982481c2d9f196b6d',catalog_entries:567,static_camera_profiles:18,fish_animation_profiles:24,all_original_camera_assertions_retained:true,default_ball_and_assembly_profiles:4,fish_protocol_original:true,fish_protocol_server:'provided local build URL; output mode name live does not imply production',records},null,2)+'\n');
}finally{await server.close();}
JS
python3 - <<'PACKAGE'
from pathlib import Path
import json,hashlib,subprocess,tarfile,shutil
base=Path('output/upstream-2b-motion-aware');head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='2b8097334caf15fb18543c8982481c2d9f196b6d'
assert subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()==['scripts/test-model-qa-browser.mjs']
harness=Path('scripts/test-model-qa-browser.mjs');assert hashlib.sha256(harness.read_bytes()).hexdigest()=='fcf6c5e60899d310d078ade42038ca16b913613bb60c8e4c181241304ce15ae3';shutil.copy2(harness,base/'executed-runtime-harness.mjs')
inputs={p for p in subprocess.check_output(['git','diff','--name-only','4f8eb6a5',head],text=True).splitlines() if Path(p).is_file() and not p.startswith('docs/')};inputs.add(str(harness))
(base/'source-manifest.json').write_text(json.dumps({'source_sha':head,'intentional_qa_only_difference':str(harness),'runtime_script_sha256':'fcf6c5e60899d310d078ade42038ca16b913613bb60c8e4c181241304ce15ae3','checked_out_files':[{'path':p,'bytes':Path(p).stat().st_size,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in sorted(inputs)]},indent=2)+'\n')
files=[p for p in base.rglob('*') if p.is_file() and (p.suffix!='.png' or p.name.endswith('-loaded.png') or 'first-attempt' in p.parts or p.name=='paused-probe.png')]
for r in json.loads((base/'fish-motion-results.json').read_text())['results']:files.append(Path(r['screenshot']))
assert len(list(base.glob('*/results.json')))==9
(base/'evidence-manifest.json').write_text(json.dumps({'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2)+'\n');files.append(base/'evidence-manifest.json')
with tarfile.open('model0011-upstream-motion-aware-evidence.tar.gz','w:gz') as t:
    for p in files:t.add(p,arcname=str(p),recursive=False)
# Restore only this job's reviewed harness overlay, after preserving its bytes.
harness.write_bytes(subprocess.check_output(['git','show','HEAD:'+str(harness)]));assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
p=Path('model0011-upstream-motion-aware-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PACKAGE

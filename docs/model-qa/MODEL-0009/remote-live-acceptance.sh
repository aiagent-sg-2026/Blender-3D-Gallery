set -e
mkdir -p output
MODEL_QA_ID=ball-03 MODEL_QA_URL=https://yapweijun1996.github.io/Blender-3D-Gallery/ MODEL_QA_OUTPUT=output/live npx --yes node@24.21.0 scripts/test-model-qa-browser.mjs > output/runtime.log 2>&1
MODEL_QA_ID=eight-ball-billiards MODEL_QA_URL=https://yapweijun1996.github.io/Blender-3D-Gallery/ MODEL_QA_OUTPUT=output/live-assembly npx --yes node@24.21.0 scripts/test-model-qa-browser.mjs > output/runtime-assembly.log 2>&1
npx --yes node@24.21.0 --input-type=module - <<'JS'
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const revision=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
assert.equal(revision,'2b8d7e10a2bfd83fd665c08ef3568e020f300e1e');
const records=[],directory='output/live-exports';
await fs.mkdir(directory,{recursive:true});
for(const [id,label,file,sha] of [['ball-03','live','ball_03.glb','a78935075c2b991166b60fd9b4fba5248e5baf8c1fefa4ef2eec54a754701352'],['eight-ball-billiards','live-assembly','billiards-scene.glb','6e11310f233ca08c86cffa9b075500fd47d07396deb78b3e5ef06af611c3e7ff']]){
 const profiles=JSON.parse(await fs.readFile('output/'+label+'/results.json','utf8'));
 assert.equal(profiles.length,2);assert.ok(profiles.every(p=>p.modelId===id&&p.status==='PASS'&&p.assetSha256===sha&&p.errors.length===0&&p.networkErrors.length===0));
 const url=profiles[0].metrics.resources[0].url;assert.ok(profiles.every(p=>p.metrics.resources[0].url===url));
 const response=await fetch(url);assert.equal(response.status,200);const bytes=Buffer.from(await response.arrayBuffer());assert.equal(bytes.length,profiles[0].assetBytes);assert.equal(createHash('sha256').update(bytes).digest('hex'),sha);
 await fs.writeFile(directory+'/'+file,bytes);
 records.push({model_id:id,url,status:response.status,content_encoding:response.headers.get('content-encoding'),content_length_header:response.headers.get('content-length'),decoded_bytes:bytes.length,sha256:sha,matches_validated_candidate:true,browser_results:'output/'+label+'/results.json'});
}
const scripts={};
for(const file of ['scripts/test-model-qa-browser.mjs','scripts/browser-test-utils.mjs','tests/ball-03.test.mjs','tests/helpers/ball-geometry-checks.mjs'])scripts[file]=createHash('sha256').update(await fs.readFile(file)).digest('hex');
await fs.writeFile('output/live-deployment.json',JSON.stringify({observed_at:new Date().toISOString(),qa_release_head:revision,actions_run_id:43683566612,both_standalone_and_assembly_accepted:true,products_unchanged:true,execution_environment:{platform:process.platform,arch:process.arch,node:process.version},script_sha256:scripts,artifacts:records,physical_mobile:'Excluded by explicit owner instruction'},null,2)+'\n');
JS
BALL_03_QA_ASSET_DIR=output/live-exports npx --yes node@24.21.0 --test tests/ball-03.test.mjs > output/production-structure.log 2>&1
git diff --exit-code -- scripts tests models package.json package-lock.json
python3 - <<'PY'
from pathlib import Path
import tarfile,hashlib,json
files=[Path('output/live-deployment.json'),Path('output/production-structure.log'),Path('output/runtime.log'),Path('output/runtime-assembly.log')]
for stage in ['live','live-assembly']:
 files.append(Path('output')/stage/'results.json')
 for width in [1440,768]:
  for view in ['loaded','page','reset']:files.append(Path('output')/stage/f'{width}-{view}.png')
manifest={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
Path('output/evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(Path('output/evidence-manifest.json'))
with tarfile.open('live-evidence.tar.gz','w:gz') as archive:
 for p in files:archive.add(p,arcname=str(p),recursive=False)
p=Path('live-evidence.tar.gz');print(json.dumps({'evidence_tar':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files)}))
PY

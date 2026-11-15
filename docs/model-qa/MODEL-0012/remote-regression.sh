set -e
python3 - <<'PREFLIGHT'
from pathlib import Path
import subprocess
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='f58402b3e6a2b418cd6d17780ff1f6988cdc8175'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
assert not Path('output/model0012-regression').exists()
PREFLIGHT
git fetch --depth=100 --filter=blob:none origin c9968137e1c7ff670c2fc0261510d9ab391ebbe8
git merge-base --is-ancestor HEAD FETCH_HEAD
git merge --ff-only --quiet FETCH_HEAD
mkdir -p output/model0012-regression
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" -e "require('node:assert/strict').equal(process.version,'v24.21.0')"
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/model0012-regression/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/model0012-regression/build.log 2>&1
TEST_ARTIFACT_DIR=output/model0012-regression/game "$MODEL_QA_NODE_BIN" scripts/test-game-browser.mjs > output/model0012-regression/game.log 2>&1
TEST_ARTIFACT_DIR=output/model0012-regression/experience "$MODEL_QA_NODE_BIN" scripts/test-game-experience.mjs > output/model0012-regression/experience.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - > output/model0012-regression/runtime.log 2>&1 <<'JS'
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {serveBuild} from './scripts/browser-test-utils.mjs';
const base='output/model0012-regression';
const game=JSON.parse(await fs.readFile(base+'/game/results.json','utf8'));
const experience=JSON.parse(await fs.readFile(base+'/experience/results.json','utf8'));
assert.equal(game.results.length,46);assert.ok(game.results.every(x=>x.passed));assert.deepEqual(game.errors,[]);assert.deepEqual(game.selection,{from:null,case:null});
assert.equal(experience.results.length,31);assert.ok(experience.results.every(x=>x.passed));assert.deepEqual(experience.errors,[]);assert.equal(experience.selection,null);
const server=await serveBuild();
try{
 for(const [id,label,sha] of [['ball-06','candidate','111f5a5148ac12aa0beaf86c3f9fc7a3eae8bfccdfb9853197dce113780cbf50'],['eight-ball-billiards','assembly','6e11310f233ca08c86cffa9b075500fd47d07396deb78b3e5ef06af611c3e7ff']]){
  const destination=base+'/'+label;
  await new Promise((resolve,reject)=>{
   const child=spawn(process.execPath,['scripts/test-model-qa-browser.mjs'],{stdio:'inherit',env:{...process.env,MODEL_QA_ID:id,MODEL_QA_URL:server.url,MODEL_QA_OUTPUT:destination,MODEL_QA_INCLUDE_MOBILE:'0'}});
   child.once('error',reject);child.once('exit',(code,signal)=>code===0?resolve():reject(new Error('Runtime failed: '+id+' '+code+' '+signal)));
  });
  const profiles=JSON.parse(await fs.readFile(destination+'/results.json','utf8'));assert.equal(profiles.length,2);assert.ok(profiles.every(p=>p.status==='PASS'&&p.modelId===id&&p.assetSha256===sha&&p.errors.length===0&&p.networkErrors.length===0));
 }
 await fs.writeFile(base+'/acceptance.json',JSON.stringify({source_sha:'c9968137e1c7ff670c2fc0261510d9ab391ebbe8',game:{tests:46,passed:46,selection:game.selection},experience:{tests:31,passed:31,selection:experience.selection},catalog_entries:567,browser_profiles_passed:4,node:process.version,platform:process.platform,arch:process.arch,physical_mobile:'Excluded by owner; existing full-suite browser emulation scenarios retained'},null,2)+'\n');
}finally{await server.close();}
JS
git diff --exit-code -- src scripts models data public tests package.json package-lock.json vite.config.js index.html
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
base=Path('output/model0012-regression');head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='c9968137e1c7ff670c2fc0261510d9ab391ebbe8'
inputs=[Path(p.decode()) for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p and Path(p.decode()).is_file()]
(base/'source-manifest.json').write_text(json.dumps({'source_sha':head,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_out_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]},indent=2)+'\n')
files=[base/p for p in ['build.log','game.log','experience.log','runtime.log','game/results.json','experience/results.json','acceptance.json','source-manifest.json','candidate/results.json','assembly/results.json']]
for stage in ['candidate','assembly']:
 for width in [1440,768]:
  for view in ['loaded','page','reset']:files.append(base/stage/f'{width}-{view}.png')
(base/'evidence-manifest.json').write_text(json.dumps({'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2)+'\n');files.append(base/'evidence-manifest.json')
with tarfile.open('model0012-regression-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('model0012-regression-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PY

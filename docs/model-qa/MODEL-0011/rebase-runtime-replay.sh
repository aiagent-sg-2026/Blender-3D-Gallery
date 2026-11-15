set -e
python3 - <<'PY'
from pathlib import Path
import subprocess
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='fcb763f63dd8b7a5f77946d810412c28ac59b8bf'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
assert not Path('output/upstream-f58402b3').exists()
PY
git fetch --depth=40 --filter=blob:none origin f58402b3e6a2b418cd6d17780ff1f6988cdc8175
git merge-base --is-ancestor HEAD FETCH_HEAD
git merge --ff-only --quiet FETCH_HEAD
mkdir -p output/upstream-f58402b3
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" -e "require('node:assert/strict').equal(process.version,'v24.21.0')"
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/upstream-f58402b3/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/upstream-f58402b3/build.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - > output/upstream-f58402b3/runtime.log 2>&1 <<'JS'
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {serveBuild} from './scripts/browser-test-utils.mjs';
const ids=['gjh-areca-planter'];
const catalog=JSON.parse(await fs.readFile('models/catalog.json','utf8'));
const assets=catalog.collections.flatMap(c=>c.assets);assert.equal(assets.length,567);
const server=await serveBuild(),records=[];
try{
 for(const id of ids){
  const destination='output/upstream-f58402b3/'+id;
  await new Promise((resolve,reject)=>{
   const child=spawn(process.execPath,['scripts/test-model-qa-browser.mjs'],{stdio:'inherit',env:{...process.env,MODEL_QA_ID:id,MODEL_QA_URL:server.url,MODEL_QA_OUTPUT:destination,MODEL_QA_INCLUDE_MOBILE:'0'}});
   child.once('error',reject);child.once('exit',(code,signal)=>code===0?resolve():reject(new Error('Runtime child failed: '+id+' '+code+' '+signal)));
  });
  const profiles=JSON.parse(await fs.readFile(destination+'/results.json','utf8'));assert.equal(profiles.length,2);
  const asset=assets.find(a=>a.id===id),original=await fs.readFile(asset.file),digest=createHash('sha256').update(original).digest('hex');
  assert.ok(profiles.every(p=>p.status==='PASS'&&p.modelId===id&&p.assetSha256===digest&&p.errors.length===0&&p.networkErrors.length===0));
  const url=profiles[0].metrics.resources[0].url,response=await fetch(url);assert.equal(response.status,200);const payload=Buffer.from(await response.arrayBuffer());assert.equal(payload.length,original.length);assert.equal(createHash('sha256').update(payload).digest('hex'),digest);
  records.push({id,profiles:2,url,decoded_bytes:payload.length,sha256:digest,download_verified:true,results:destination+'/results.json'});
 }
 await fs.writeFile('output/upstream-f58402b3/acceptance.json',JSON.stringify({source_sha:'f58402b3e6a2b418cd6d17780ff1f6988cdc8175',catalog_entries:567,browser_profiles_passed:2,original_script_unchanged:true,records},null,2)+'\n');
}finally{await server.close();}
JS
git diff --exit-code -- src scripts models data public package.json package-lock.json vite.config.js index.html
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
base=Path('output/upstream-f58402b3');head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='f58402b3e6a2b418cd6d17780ff1f6988cdc8175'
inputs=[Path(p.decode()) for p in subprocess.check_output(['git','diff','--name-only','-z','fcb763f63dd8b7a5f77946d810412c28ac59b8bf',head]).split(b'\0') if p and Path(p.decode()).is_file() and not p.decode().startswith('docs/')]
manifest={'source_sha':head,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_out_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]};(base/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[p for p in base.rglob('*') if p.is_file()];assert len(list(base.glob('*/results.json')))==1
receipt={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]};(base/'evidence-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');files.append(base/'evidence-manifest.json')
with tarfile.open('upstream-f58402b3-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('upstream-f58402b3-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PY

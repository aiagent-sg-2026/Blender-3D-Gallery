set -e
python3 - <<'PY'
from pathlib import Path
import subprocess
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='1e94207991e702451ce931d3f76d30925a903453'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
assert not Path('output/upstream-ea9ed618').exists()
PY
git fetch --depth=5 --filter=blob:none origin ea9ed61873cd88c02436bf590c06c3e55df9d78a
git merge-base --is-ancestor HEAD FETCH_HEAD
git merge --ff-only --quiet FETCH_HEAD
mkdir -p output/upstream-ea9ed618
MODEL_QA_NODE_BIN=$(npx --yes node@24.21.0 -p 'process.execPath')
"$MODEL_QA_NODE_BIN" -e "require('node:assert/strict').equal(process.version,'v24.21.0')"
"$MODEL_QA_NODE_BIN" scripts/validate-assets.mjs > output/upstream-ea9ed618/build.log 2>&1
"$MODEL_QA_NODE_BIN" node_modules/vite/bin/vite.js build >> output/upstream-ea9ed618/build.log 2>&1
"$MODEL_QA_NODE_BIN" --input-type=module - > output/upstream-ea9ed618/runtime.log 2>&1 <<'JS'
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {serveBuild} from './scripts/browser-test-utils.mjs';
const ids=['mall-trash-bin','mall-directory-kiosk','mall-advertising-lightbox'];
const catalog=JSON.parse(await fs.readFile('models/catalog.json','utf8'));
const assets=catalog.collections.flatMap(c=>c.assets);assert.equal(assets.length,567);
const server=await serveBuild(),records=[];
try{
 for(const id of ids){
  const destination='output/upstream-ea9ed618/'+id;
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
 await fs.writeFile('output/upstream-ea9ed618/acceptance.json',JSON.stringify({source_sha:'ea9ed61873cd88c02436bf590c06c3e55df9d78a',catalog_entries:567,browser_profiles_passed:6,original_script_unchanged:true,records},null,2)+'\n');
}finally{await server.close();}
JS
git diff --exit-code -- src scripts models data public package.json package-lock.json vite.config.js index.html
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess,tarfile,datetime
base=Path('output/upstream-ea9ed618');head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='ea9ed61873cd88c02436bf590c06c3e55df9d78a'
inputs=[Path(p.decode()) for p in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if p and Path(p.decode()).is_file()]
manifest={'source_sha':head,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked_out_files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]};(base/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=[p for p in base.rglob('*') if p.is_file()];assert len(list(base.glob('*/results.json')))==3
receipt={'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]};(base/'evidence-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');files.append(base/'evidence-manifest.json')
with tarfile.open('upstream-ea9ed618-evidence.tar.gz','w:gz') as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
p=Path('upstream-ea9ed618-evidence.tar.gz');print(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'source_sha':head}))
PY

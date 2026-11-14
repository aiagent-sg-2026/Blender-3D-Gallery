import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {report} from '../qa-utils.mjs';

const here=path.dirname(new URL(import.meta.url).pathname),root=path.resolve(here,'../../../..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const read=async file=>JSON.parse(await fs.readFile(path.join(here,file)));
const names=['build','geometry','clearance','source-surfaces','adapter-source','browser','joint-renders'];
const checks=[];
for(const name of names){const file=`reports/${name}.json`,data=await read(file);assert.equal(data.status,'PASS',name);checks.push(file);}
const build=await read('reports/build.json'),layout=await read('layout.json'),browser=await read('reports/browser.json');
for(const file of build.files)assert.equal(hash(await fs.readFile(path.join(here,file.path))),file.sha256,file.path);
assert.deepEqual(browser.rows.map(r=>r.viewport.width),[1440,768,390,320,667]);assert.deepEqual(browser.errors,[]);
assert.equal(browser.geometrySha256,hash(await fs.readFile(path.join(here,'foundation-fitted.glb'))));
for(const source of [...Object.values(layout.sources),layout.adaptation_source])
  assert.equal(hash(await fs.readFile(path.join(root,source.path))),source.sha256,source.path);
const prior=JSON.parse(await fs.readFile(path.join(here,'../reports/delivery.json')));
for(const file of [...prior.files,...prior.checks.map(r=>({path:r.file,sha256:r.sha256}))])
  assert.equal(hash(await fs.readFile(path.join(here,'..',file.path))),file.sha256,file.path);
const files=[];
async function walk(relative=''){
  for(const entry of await fs.readdir(path.join(here,relative),{withFileTypes:true})){
    const file=path.join(relative,entry.name);
    if(file==='reports/delivery.json')continue;
    assert.ok(!entry.isSymbolicLink()&&!entry.name.endsWith('.tmp'));
    if(entry.isDirectory())await walk(file);
    else if(entry.isFile()){const bytes=await fs.readFile(path.join(here,file));files.push({path:file,bytes:bytes.length,sha256:hash(bytes)});}
  }
}
await walk();assert.ok(files.length>20);
await report(path.join(here,'reports/delivery.json'),{
  status:'VERIFIED_LOCAL_CANDIDATE',task:'FND-003',recordedAt:new Date().toISOString(),
  version:layout.version,checks,files,priorDeliveryAndInputHashesUnchanged:true,
  physicalDeviceTests:'waived by owner',browserBackend:browser.backend,published:false,
  scopeSha256:hash(await fs.readFile(path.join(root,'docs/virtual-mall-foundation-v1-scope.md'))),
  limits:['Module-fit/walking acceptance only; FND-004 onward remain open.','Software-renderer attempts timed out; final browser receipts use recorded Metal hardware.'],
});
console.log(`PASS: sealed ${checks.length} checks and ${files.length} files; original inputs and FND-001/002 identities preserved`);

import test from 'node:test'; import assert from 'node:assert/strict'; import fs from 'node:fs';
const root='models/mall-glass-showcase';
test('mall glass showcase host artifacts are complete and bounded',()=>{
  for(const f of ['exports/optimized.glb','sources/mall-glass-showcase.blend','previews/hero.png','previews/front.png','previews/rear.png','previews/side.png','previews/open.png','reports/assets.json']) assert.ok(fs.existsSync(`${root}/${f}`),`missing ${f}`);
  const r=JSON.parse(fs.readFileSync(`${root}/reports/assets.json`)); assert.equal(r.result,'PASS'); assert.ok(r.triangles<10000&&r.glb_bytes<1000000&&r.primitives<80); assert.equal(r.animations,1); assert.equal(r.validation.errors,0); assert.equal(r.validation.warnings,0);
});

import {loadCatalog} from '../scripts/catalog.mjs';
import {createHash} from 'node:crypto';
test('showcase uniquely registered with measured exported bytes and source proof',()=>{const c=loadCatalog();const a=c.collections.flatMap(c=>c.assets).filter(a=>a.id==='mall-glass-showcase');assert.equal(a.length,1);assert.equal(c.collections.find(c=>c.id==='mall-retail-showcases').assets.length,1);const report=JSON.parse(fs.readFileSync(root+'/reports/assets.json'));assert.equal(report.sha256,createHash('sha256').update(fs.readFileSync(a[0].file)).digest('hex'));const proof=JSON.parse(fs.readFileSync(root+'/reports/sources.json'));assert.equal(proof.source_sha256,createHash('sha256').update(fs.readFileSync(root+'/sources/mall-glass-showcase.blend')).digest('hex'));assert.equal(proof.original_source_unchanged,true);});

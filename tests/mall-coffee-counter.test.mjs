import {execFileSync} from 'node:child_process';
import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{createHash}from'node:crypto';import{loadCatalog}from'../scripts/catalog.mjs';
const root='models/mall-coffee-counter';
test('coffee-counter artifact and measured export evidence agree',()=>{
 for(const f of ['sources/mall-coffee-counter.blend','exports/optimized.glb','previews/hero.png','previews/front.png','previews/rear.png','previews/side.png','previews/rear-open.png','reports/assets.json','reports/sources.json'])assert.ok(fs.existsSync(root+'/'+f),f);
 const r=JSON.parse(fs.readFileSync(root+'/reports/assets.json'));assert.equal(r.result,'PASS');assert.ok(r.triangles<=10000&&r.glb_bytes<=1000000&&r.primitives<=80);assert.equal(r.sha256,createHash('sha256').update(fs.readFileSync(root+'/exports/optimized.glb')).digest('hex'));assert.equal(r.animation.frames,60);assert.ok(r.animation.opening_degrees>100);assert.equal(r.validation.errors,0);assert.equal(r.validation.warnings,0);
 const proof=JSON.parse(fs.readFileSync(root+'/reports/sources.json'));assert.equal(proof.source_sha256,createHash('sha256').update(fs.readFileSync(root+'/sources/mall-coffee-counter.blend')).digest('hex'));assert.equal(proof.original_source_unchanged,true);
});
test('unique coffee counter registration uses original mall017 scope',()=>{
 const c=loadCatalog(),entries=c.collections.flatMap(c=>c.assets).filter(a=>a.id==='mall-coffee-counter');assert.equal(entries.length,1);assert.equal(c.collections.find(c=>c.id==='mall-coffee-counters').assets.length,1);
 const m=JSON.parse(fs.readFileSync(root+'/metadata/mall-coffee-counter.json'));assert.equal(m.backlog_id,'shopping-mall-017');assert.equal(m.display.previewRotationY,0);assert.equal(entries[0].root,'ASSET_MallCoffeeCounter');assert.equal(entries[0].downloadable,false);
});

test('actual coffee counter GLB animation and clearance validate',()=>{execFileSync(process.execPath,[root+'/validate.mjs'],{stdio:'pipe'});});

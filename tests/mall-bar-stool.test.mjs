import {execFileSync} from 'node:child_process';
import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{createHash}from'node:crypto';import{loadCatalog}from'../scripts/catalog.mjs';
const root='models/mall-bar-stool';
test('bar-stool artifact and measured export evidence agree',()=>{
 for(const f of ['sources/mall-bar-stool.blend','exports/optimized.glb','previews/hero.png','previews/front.png','previews/rear.png','previews/side.png','previews/swivel.png','reports/assets.json','reports/sources.json'])assert.ok(fs.existsSync(root+'/'+f),f);
 const r=JSON.parse(fs.readFileSync(root+'/reports/assets.json'));assert.equal(r.result,'PASS');assert.ok(r.triangles<=8000&&r.glb_bytes<=800000&&r.primitives<=40);assert.equal(r.sha256,createHash('sha256').update(fs.readFileSync(root+'/exports/optimized.glb')).digest('hex'));assert.equal(r.animation.frames,60);assert.ok(r.animation.opening_degrees>89);assert.equal(r.validation.errors,0);assert.equal(r.validation.warnings,0);
 const proof=JSON.parse(fs.readFileSync(root+'/reports/sources.json'));assert.equal(proof.source_sha256,createHash('sha256').update(fs.readFileSync(root+'/sources/mall-bar-stool.blend')).digest('hex'));assert.equal(proof.original_source_unchanged,true);
});
test('unique bar stool registration uses original mall019 scope',()=>{
 const c=loadCatalog(),entries=c.collections.flatMap(c=>c.assets).filter(a=>a.id==='mall-bar-stool');assert.equal(entries.length,1);assert.equal(c.collections.find(c=>c.id==='mall-bar-stools').assets.length,1);
 const m=JSON.parse(fs.readFileSync(root+'/metadata/mall-bar-stool.json'));assert.equal(m.backlog_id,'shopping-mall-019');assert.equal(m.display.previewRotationY,0);assert.equal(entries[0].root,'ASSET_MallBarStool');assert.equal(entries[0].downloadable,false);
});

test('actual bar stool GLB animation and clearance validate',()=>{execFileSync(process.execPath,[root+'/validate.mjs'],{stdio:'pipe'});});

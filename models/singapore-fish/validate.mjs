import fs from 'node:fs';
import assert from 'node:assert/strict';
import validator from 'gltf-validator';
import { loadCatalog } from '../../scripts/catalog.mjs';
const collection=loadCatalog().collections.find(c=>c.id==='singapore-fish');
assert.equal(collection.assets.length,60);
const hashes=new Set();const reports=[];
for(const [i,a] of collection.assets.entries()){
 const bytes=fs.readFileSync(a.file);const r=await validator.validateBytes(new Uint8Array(bytes),{uri:a.file});
 assert.equal(r.issues.numErrors,0,JSON.stringify(r.issues));assert.equal(r.issues.numWarnings,0,JSON.stringify(r.issues));
 assert.equal(a.details.fish_id,`FISH-${String(i+1).padStart(3,'0')}`);
 assert.ok(fs.statSync(a.details.source).size>10000);
 const jsonLength=bytes.readUInt32LE(12);const gltf=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
 assert.ok(gltf.meshes.length>5);assert.equal(gltf.animations?.length,1);assert.equal(gltf.animations[0].name,"Swim_Loop");assert.ok(gltf.skins.length>0);assert.ok(!gltf.cameras?.length);
 assert.ok(a.bytes<1500000,'Web asset budget exceeded');
 hashes.add(bytes.toString('base64'));reports.push({id:a.details.fish_id,name:a.name,triangles:a.triangles,bytes:a.bytes,errors:r.issues.numErrors,warnings:r.issues.numWarnings});
}
assert.equal(hashes.size,60);
fs.writeFileSync(new URL('validation.json',import.meta.url),JSON.stringify(reports,null,2)+'\n');
console.log(`PASS: ${reports.length} distinct GLBs, no validation errors/warnings, source files present; ${reports.reduce((s,r)=>s+r.bytes,0)} total bytes.`);

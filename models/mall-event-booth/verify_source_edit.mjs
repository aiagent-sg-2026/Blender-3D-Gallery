import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';
import { Vector3 } from 'three';
const here=path.dirname(fileURLToPath(import.meta.url));
assert.ok(process.argv[2], 'Pass the isolated test_source_edit.py output directory');
const directory=path.resolve(process.argv[2]);
const paths=[path.join(here,'exports/mall-event-booth.glb'),path.join(directory,'baseline/exports/mall-event-booth.glb'),path.join(directory,'exports/mall-event-booth.glb')];
const execution=JSON.parse(fs.readFileSync(path.join(directory,'edit-execution.json')));
assert.equal(execution.status,'PASS');assert.deepEqual(execution.originalBefore,execution.originalAfter);
assert.equal(execution.baselineSourceSha256,execution.originalBefore.source);
assert.equal(execution.beforeLabel,'YOUR STORY');assert.equal(execution.afterLabel,'NEW STORY');
const groups=['BoothStructure','PosterPanel','DisplayContent'];
const results=[];
for(const file of paths){
  const bytes=fs.readFileSync(file);
  const validation=await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(validation.issues.numErrors,0);assert.equal(validation.issues.numWarnings,0);
  const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');gltf.scene.updateMatrixWorld(true);
  const hashes={};let zeroAreaTriangles=0;
  for(const group of groups){
    const hash=createHash('sha256');gltf.scene.getObjectByName(group).traverse(o=>{
      if(!o.isMesh)return;
      hash.update(JSON.stringify(o.matrixWorld.elements));
      for(const [name,attr] of Object.entries(o.geometry.attributes)){hash.update(name);hash.update(Buffer.from(attr.array.buffer,attr.array.byteOffset,attr.array.byteLength));}
      if(o.geometry.index)hash.update(Buffer.from(o.geometry.index.array.buffer,o.geometry.index.array.byteOffset,o.geometry.index.array.byteLength));
      const geometry=o.geometry,position=geometry.attributes.position;
      for(let i=0;i<(geometry.index?.count??position.count);i+=3){
        const points=[0,1,2].map(offset=>new Vector3().fromBufferAttribute(position,geometry.index?geometry.index.getX(i+offset):i+offset).applyMatrix4(o.matrixWorld));
        if(points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])).lengthSq()===0)zeroAreaTriangles++;
      }
      const m=o.material;hash.update(JSON.stringify({color:m.color.toArray(),metalness:m.metalness,roughness:m.roughness}));
    });hashes[group]=hash.digest('hex');
  }
  assert.equal(zeroAreaTriangles,0,'Source control/edit export must contain no degenerate triangles');
  results.push({asset:['shipped asset','same-toolchain source control','isolated edited source'][results.length],sha256:createHash('sha256').update(bytes).digest('hex'),zeroAreaTriangles,groupHashes:hashes,validation:{errors:0,warnings:0}});
}
// Compare edit effects against a real unchanged-source export with the same
// toolchain; canonical delivery intentionally preserves older vertex packing.
for(const group of groups) if(group==='PosterPanel')assert.notEqual(results[1].groupHashes[group],results[2].groupHashes[group]);else assert.equal(results[1].groupHashes[group],results[2].groupHashes[group],group);
const original=JSON.parse(fs.readFileSync(path.join(here,'reports/assets.json')));
assert.equal(results[0].sha256,original.sha256);
assert.equal(results[0].sha256,execution.originalBefore.glb);
const metadata=JSON.parse(fs.readFileSync(path.join(here,'metadata/mall-event-booth.json')));
assert.equal(execution.originalBefore.source,metadata.source_sha256);
const report={status:'PASS',edit:'YOUR STORY -> NEW STORY in an isolated copy of the saved Blender source',exportMode:'generate.py -- --export-source --no-render',comparisonBasis:'same-toolchain source control',blender:execution.blender,originalSourceSha256:execution.originalBefore.source,baselineSourceSha256:execution.baselineSourceSha256,changedGroups:['PosterPanel'],unchangedGroups:groups.filter(n=>n!=='PosterPanel'),originalAssetUnchanged:true,results};
fs.writeFileSync(path.join(here,'reports/source-edit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));

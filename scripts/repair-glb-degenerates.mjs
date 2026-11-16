import './node-glb-structure.mjs';
import {RIGID_FLAG,rigidScope,animationPayload} from './rigid-container-qa.mjs';
const rigidOptIn=process.argv.includes(RIGID_FLAG);
const splitShared=process.argv.includes('--split-shared-indices');
// Preserve authored vertex/shading/image/animation payloads; rewrite only indices.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const [input, output, evidence, sourceComparison] = process.argv.slice(2);
assert.ok(input && output && evidence && sourceComparison, 'Pass input, distinct output, receipt and reviewed source comparison');
assert.equal(new Set([input, output, evidence, sourceComparison].map(p => path.resolve(p))).size, 4, 'Use distinct input, output and evidence files');
const comparison = JSON.parse(await fs.readFile(sourceComparison, 'utf8'));
assert.equal(comparison.status, 'PASS');
const lineResidues = comparison.linePrecisionResidues ?? [];
const precisionLineNodes=comparison.precisionLineNodes??[];
if (lineResidues.length) {
  const flag = '--precision-line-tolerance-m=' + comparison.precisionLineToleranceM;
  assert.ok(process.argv.includes(flag), 'Analytic line residue removal requires the same explicit reviewed tolerance');
  assert.ok(Number.isFinite(comparison.precisionLineToleranceM) && comparison.precisionLineToleranceM > 0 && comparison.precisionLineToleranceM <= 1e-7);
  assert.ok(lineResidues.every(r => r.altitude <= comparison.precisionLineToleranceM));
  if(precisionLineNodes.length){
    assert.ok(process.argv.includes('--precision-line-nodes='+precisionLineNodes.join(',')),'Use the same exact reviewed line-node scope');
    assert.ok(lineResidues.every(r=>precisionLineNodes.includes(r.node)));
  }
}
const reviewedResidues = [...comparison.removedPositiveAreaResidues, ...lineResidues];
const reviewed = new Set(comparison.removedPositiveAreaResidues.map(r => r.key));
const reviewedLines=new Set(lineResidues.map(r=>(precisionLineNodes.length?r.node+':':'')+r.key));
const bytes = await fs.readFile(input);
assert.equal(bytes.readUInt32LE(0), 0x46546c67); assert.equal(bytes.readUInt32LE(4), 2);
assert.equal(bytes.readUInt32LE(8), bytes.length);
assert.equal(createHash('sha256').update(bytes).digest('hex'), comparison.before.sha256);
const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
const binaryOffset = 20 + bytes.readUInt32LE(12) + 8;
assert.equal(bytes.readUInt32LE(binaryOffset - 4), 0x004e4942);
let binary = Buffer.from(bytes.subarray(binaryOffset));
const scope=rigidOptIn?rigidScope(json):null;
if(!scope)assert.equal(json.animations?.length ?? 0, 0, 'Animation verification must be added before using this on animated models');
else assert.equal(comparison.rigidContainerStaticOnly,true,'Require a rigid-container source comparison');
const beforeAnimation=scope?animationPayload(json,binary):undefined;
const changedStaticNodes=new Set();
assert.equal(json.scenes.length, 1);
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
let zeroRemoved = 0, residueRemoved = 0;
const plans = new Map();
const splitIndexAccessors = [];
gltf.scene.traverse(object => {
  if (!object.isMesh) return;
  const association = gltf.parser.associations.get(object);
  const primitive = json.meshes[association.meshes].primitives[association.primitives];
  assert.equal(primitive.mode ?? 4, 4);
  assert.ok(primitive.indices !== undefined);
  const accessor = json.accessors[primitive.indices], view = json.bufferViews[accessor.bufferView];
  assert.equal(view.buffer, 0); assert.ok(!accessor.sparse && !view.byteStride);
  const width = { 5121: 1, 5123: 2, 5125: 4 }[accessor.componentType]; assert.ok(width);
  const { index, attributes: { position } } = object.geometry;
  const retained = [];
  for (let i = 0; i < index.count; i += 3) {
    const ids = [0, 1, 2].map(j => index.getX(i + j));
    const points = ids.map(j => new Vector3().fromBufferAttribute(position, j).applyMatrix4(object.matrixWorld));
    const area = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])).length() * .5;
    if (area === 0) { zeroRemoved++; continue; }
    const keys = points.map(p => p.toArray().map(x => Math.round(x / 1e-6)).join(','));
    const key = object.material.name + ':' + keys.map((_, j) => [keys[j], keys[(j + 1) % 3], keys[(j + 2) % 3]].join('|')).sort((a, b) => a.localeCompare(b))[0];
    if (reviewed.has(key)||reviewedLines.has((precisionLineNodes.length?object.name+':':'')+key)) { residueRemoved++; continue; }
    retained.push(...ids);
  }
  assert.ok(retained.length);
  if(scope&&retained.length!==index.count)for(const name of scope.assertStaticMesh(association.meshes))changedStaticNodes.add(name);
  const key=association.meshes+':'+association.primitives;
  if(plans.has(key)){
    assert.deepEqual(retained,plans.get(key).retained,'Shared primitive instances require identical retained indices; mesh duplication needs separate review');
  }else plans.set(key,{key,primitive,originalAccessor:primitive.indices,retained,width});
});
// Decide all masks before writing. Exporters can share an index accessor across
// distinct meshes whose vertex data collapses differently; opt-in cloning gives
// those primitives independent indices while retaining every original attribute.
const groups=new Map();
for(const plan of plans.values()){
  if(!groups.has(plan.originalAccessor))groups.set(plan.originalAccessor,[]);
  groups.get(plan.originalAccessor).push(plan);
}
const indexAccessors=new Set(json.meshes.flatMap(m=>m.primitives.map(p=>p.indices)));
const ranges=[...indexAccessors].map(id=>{const a=json.accessors[id],v=json.bufferViews[a.bufferView],start=(v.byteOffset??0)+(a.byteOffset??0);return {id,start,end:start+a.count*({5121:1,5123:2,5125:4}[a.componentType])};});
for(let i=0;i<ranges.length;i++)for(let j=i+1;j<ranges.length;j++)assert.ok(ranges[i].end<=ranges[j].start||ranges[j].end<=ranges[i].start,'Overlapping distinct index accessors require separate review');
const attributeViews=new Set(json.accessors.flatMap((a,i)=>indexAccessors.has(i)||a.bufferView===undefined?[]:[a.bufferView]));
const update=(accessor,retained)=>{
 accessor.count=retained.length;
 if(accessor.min)accessor.min=[retained.reduce((a,b)=>Math.min(a,b),Infinity)];
 if(accessor.max)accessor.max=[retained.reduce((a,b)=>Math.max(a,b),-Infinity)];
};
for(const[originalId,uses]of groups){
 const original=json.accessors[originalId],view=json.bufferViews[original.bufferView],width=uses[0].width;
 const offset=(view.byteOffset??0)+(original.byteOffset??0);
 const originalIndices=Array.from({length:original.count},(_,i)=>binary.readUIntLE(offset+i*width,width));
 const masks=new Map();
 for(const plan of uses){const key=JSON.stringify(plan.retained);if(!masks.has(key))masks.set(key,[]);masks.get(key).push(plan);}
 const variants=[...masks.values()];
 if(variants.length>1)assert.ok(splitShared,'Shared index accessor requires identical retained indices for every use; explicit --split-shared-indices is required');
 const unchanged=JSON.stringify(originalIndices);
 const keep=masks.get(unchanged)??variants[0];
 if(JSON.stringify(keep[0].retained)!==unchanged){
  const end=offset+keep[0].retained.length*width;
  for(const id of attributeViews){const other=json.bufferViews[id],start=other.byteOffset??0;
   assert.ok(other.buffer!==0||end<=start||offset>=start+other.byteLength,'Index writes overlap a non-index payload');
  }
  for(let i=0;i<keep[0].retained.length;i++)binary.writeUIntLE(keep[0].retained[i],offset+i*width,width);
 }
 const template=structuredClone(original);update(original,keep[0].retained);
 for(const variant of variants){
  if(variant===keep)continue;
  const retained=variant[0].retained,data=Buffer.alloc(Math.ceil(retained.length*width/4)*4);
  retained.forEach((v,i)=>data.writeUIntLE(v,i*width,width));
  const viewId=json.bufferViews.length,newId=json.accessors.length;
  json.bufferViews.push({buffer:0,byteOffset:binary.length,byteLength:retained.length*width,target:34963});
  const accessor={...template,bufferView:viewId,byteOffset:0};update(accessor,retained);json.accessors.push(accessor);
  for(const plan of variant)plan.primitive.indices=newId;
  binary=Buffer.concat([binary,data]);
  splitIndexAccessors.push({originalAccessor:originalId,newAccessor:newId,bufferView:viewId,primitives:variant.map(p=>p.key),triangles:retained.length/3});
 }
}
if(splitIndexAccessors.length)json.buffers[0].byteLength=binary.length;
assert.equal(zeroRemoved, comparison.before.zero);
assert.equal(residueRemoved, reviewedResidues.length);
const jsonData = Buffer.from(JSON.stringify(json));
const paddedJson = Buffer.alloc(Math.ceil(jsonData.length / 4) * 4, 0x20); jsonData.copy(paddedJson);
const result = Buffer.alloc(12 + 8 + paddedJson.length + 8 + binary.length);
result.writeUInt32LE(0x46546c67, 0); result.writeUInt32LE(2, 4); result.writeUInt32LE(result.length, 8);
result.writeUInt32LE(paddedJson.length, 12); result.writeUInt32LE(0x4e4f534a, 16); paddedJson.copy(result, 20);
const binHeader = 20 + paddedJson.length;
result.writeUInt32LE(binary.length, binHeader); result.writeUInt32LE(0x004e4942, binHeader + 4); binary.copy(result, binHeader + 8);
const validation = await validator.validateBytes(new Uint8Array(result));
assert.equal(validation.issues.numErrors, 0); assert.equal(validation.issues.numWarnings, 0);
const afterAnimation=scope?animationPayload(json,binary):undefined;
if(scope)assert.deepEqual(afterAnimation,beforeAnimation,'Animation binary/descriptor preservation failed');
await fs.writeFile(output, result, { flag: 'wx' });
await fs.writeFile(evidence, JSON.stringify({ status: 'PASS', zeroRemoved, residueRemoved,
  splitIndexAccessors,
  rigidContainer:scope?{changedStaticNodes:[...changedStaticNodes].sort(),animation:afterAnimation}:undefined,
  originalSha256: comparison.before.sha256, sha256: createHash('sha256').update(result).digest('hex'),
  preservation: 'Only triangle index streams, index accessor counts/min/max and explicitly split primitive index bindings changed; new index views are appended when needed. All original non-index binary payload bytes retained.',
  validation: validation.issues }, null, 2) + '\n', { flag: 'wx' });
console.log('PASS:', zeroRemoved, 'zero-area triangles and', residueRemoved, 'reviewed source precision residues removed');

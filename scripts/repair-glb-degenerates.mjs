import './node-glb-structure.mjs';
import {RIGID_FLAG,rigidScope,animationPayload} from './rigid-container-qa.mjs';
const rigidOptIn=process.argv.includes(RIGID_FLAG);
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
const binary = Buffer.from(bytes.subarray(binaryOffset));
const scope=rigidOptIn?rigidScope(json):null;
if(!scope)assert.equal(json.animations?.length ?? 0, 0, 'Animation verification must be added before using this on animated models');
else assert.equal(comparison.rigidContainerStaticOnly,true,'Require a rigid-container source comparison');
const beforeAnimation=scope?animationPayload(json,binary):undefined;
const changedStaticNodes=new Set();
assert.equal(json.scenes.length, 1);
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
let zeroRemoved = 0, residueRemoved = 0;
const usedAccessors = new Map();
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
  if (usedAccessors.has(primitive.indices)) {
    assert.deepEqual(retained, usedAccessors.get(primitive.indices), 'Shared index accessor requires identical retained indices for every use');
    return;
  }
  usedAccessors.set(primitive.indices, retained);
  const offset = (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
  for (let i = 0; i < retained.length; i++) binary.writeUIntLE(retained[i], offset + i * width, width);
  accessor.count = retained.length;
  if (accessor.min) accessor.min = [retained.reduce((a, b) => Math.min(a, b), Infinity)];
  if (accessor.max) accessor.max = [retained.reduce((a, b) => Math.max(a, b), -Infinity)];
});
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
  rigidContainer:scope?{changedStaticNodes:[...changedStaticNodes].sort(),animation:afterAnimation}:undefined,
  originalSha256: comparison.before.sha256, sha256: createHash('sha256').update(result).digest('hex'),
  preservation: 'Only triangle index streams and index accessor counts/min/max changed; all other binary payload bytes retained.',
  validation: validation.issues }, null, 2) + '\n', { flag: 'wx' });
console.log('PASS:', zeroRemoved, 'zero-area triangles and', residueRemoved, 'reviewed source precision residues removed');

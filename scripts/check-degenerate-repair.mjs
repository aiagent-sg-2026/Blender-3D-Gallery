import './node-glb-structure.mjs';
import {RIGID_FLAG,rigidScope,animationPayload,compareNativeClips} from './rigid-container-qa.mjs';
const rigidOptIn=process.argv.includes(RIGID_FLAG);
import { materialDefinitions } from './node-glb-structure.mjs';
// Independent comparison of static delivered GLBs, including numerical residue.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const [beforePath, afterPath, output] = process.argv.slice(2);
const allowNormalDrift = process.argv.includes('--allow-normal-drift');
const lineArgument = process.argv.find(value => value.startsWith('--precision-line-tolerance-m='));
const precisionLineToleranceM = lineArgument ? Number(lineArgument.split('=')[1]) : 0;
const lineNodesArgument=process.argv.find(v=>v.startsWith('--precision-line-nodes='));
const precisionLineNodes=lineNodesArgument?lineNodesArgument.split('=')[1].split(',').sort():[];
assert.ok(!precisionLineNodes.length||(precisionLineToleranceM>0&&precisionLineNodes.every(Boolean)&&new Set(precisionLineNodes).size===precisionLineNodes.length),'Line-node scope requires a tolerance and unique exact node names');
assert.ok(Number.isFinite(precisionLineToleranceM) && precisionLineToleranceM >= 0 && precisionLineToleranceM <= 1e-7,
  'Explicit reviewed line tolerance must be finite and at most 0.1 micrometre');
assert.ok(beforePath && afterPath && output, 'Pass original GLB, repaired GLB and receipt path');
const POSITION_QUANTIZATION = 1e-6;
const NUMERICAL_RESIDUE_ALTITUDE = 1e-7;
async function inspect(file) {
  const bytes = await fs.readFile(file);
  const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
  assert.ok(precisionLineNodes.every(name=>json.nodes.some(n=>n.name===name)),'Line-node scope contains an unknown node');
  const resolvedMaterials = materialDefinitions(json, bytes.subarray(28 + bytes.readUInt32LE(12)));
  const validation = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(validation.issues.numErrors, 0); assert.equal(validation.issues.numWarnings, 0);
  if(rigidOptIn)rigidScope(json);
  else assert.equal(json.animations?.length ?? 0, 0, 'Animated assets require separate state/clip comparison');
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const surfaces = new Map(), roots = {}, linePrecisionResidues = [];
  let triangles = 0, zero = 0, invalidNormals = 0;
  gltf.scene.traverse(object => {
    if (object.name.startsWith('ASSET_')) roots[object.name] = object.matrixWorld.toArray();
    if (!object.isMesh) return;
    const { index, attributes: { position, normal } } = object.geometry;
    assert.ok(normal);
    for (let i = 0; i < normal.count; i++) {
      const length = Math.hypot(normal.getX(i), normal.getY(i), normal.getZ(i));
      if (!Number.isFinite(length) || Math.abs(length - 1) > .01) invalidNormals++;
    }
    for (let i = 0; i < (index?.count ?? position.count); i += 3) {
      const ids = [0, 1, 2].map(j => index ? index.getX(i + j) : i + j);
      const points = ids.map(j => new Vector3().fromBufferAttribute(position, j).applyMatrix4(object.matrixWorld));
      assert.ok(points.every(p => p.toArray().every(Number.isFinite)));
      const area = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])).length() * .5;
      triangles++;
      if (area === 0) { zero++; continue; }
      const quantized = points.map(p => p.toArray().map(x => Math.round(x / POSITION_QUANTIZATION)));
      const rotations = quantized.map((_, j) => ({ j, key: [0, 1, 2].map(k => quantized[(j + k) % 3].join(',')).join('|') }));
      rotations.sort((a, b) => a.key.localeCompare(b.key));
      const rotation = rotations[0];
      const key = object.material.name + ':' + rotation.key;
      const quantizedArea = new Vector3(...quantized[1]).sub(new Vector3(...quantized[0]))
        .cross(new Vector3(...quantized[2]).sub(new Vector3(...quantized[0]))).lengthSq();
      const normals = [0, 1, 2].map(k => new Vector3().fromBufferAttribute(normal, ids[(rotation.j + k) % 3]).toArray());
      const longestEdge = Math.max(...points.map((p, j) => p.distanceTo(points[(j + 1) % 3])));
      const orderedPoints = [0, 1, 2].map(k => points[(rotation.j + k) % 3].toArray());
      const record = { area, altitude: 2 * area / longestEdge, quantizedCollinear: quantizedArea === 0,
        material: object.material.name, points: orderedPoints, normals };
      if (precisionLineToleranceM && (!precisionLineNodes.length||precisionLineNodes.includes(object.name)) && record.altitude <= precisionLineToleranceM) {
        // Explicit calibration for reviewed analytic lines. Grid rounding can
        // make a radial line non-collinear, so use its actual perpendicular error.
        linePrecisionResidues.push({ key, node:object.name, area, altitude: record.altitude,
          quantizedCollinear: record.quantizedCollinear, points:record.points });
        continue;
      }
      if (!surfaces.has(key)) surfaces.set(key, []);
      surfaces.get(key).push(record);
    }
  });
  const bounds = new Box3().setFromObject(gltf.scene);
  return { file, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), triangles, zero,
    invalidNormals, bounds: { min: bounds.min.toArray(), max: bounds.max.toArray() }, roots,
    materialDefinitions: json.materials, resolvedMaterialDefinitions: resolvedMaterials,
    animationPayload: rigidOptIn?animationPayload(json,bytes.subarray(28+bytes.readUInt32LE(12))):undefined,
    clipData: rigidOptIn?gltf.animations:undefined,
    issues: validation.issues, surfaces, linePrecisionResidues };
}
const summarize = value => ({ ...value, surfaces: undefined, clipData: undefined });
let receipt;
try {
  const before = await inspect(beforePath), after = await inspect(afterPath);
  const removed = [], added = [], unmatchedOld = [], unmatchedNew = [], pairs = [];
  let changedNormalTriangles = 0, maxNormalDelta = 0;
  for (const [key, old] of before.surfaces) {
    const current = after.surfaces.get(key) ?? [];
    unmatchedOld.push(...old.slice(current.length).map(record => ({ key, record })));
    for (let i = 0; i < Math.min(old.length, current.length); i++) pairs.push({ old: old[i], current: current[i], rotation: 0 });
  }
  for (const [key, current] of after.surfaces) {
    unmatchedNew.push(...current.slice(before.surfaces.get(key)?.length ?? 0).map(record => ({ key, record, used: false })));
  }
  // Quantization hashes are only an accelerator: two coordinates on opposite
  // sides of a grid boundary can still be arbitrarily close in actual distance.
  const centroidCell = r => [0, 1, 2].map(axis => Math.floor(r.points.reduce((sum, p) => sum + p[axis], 0) / 3 / POSITION_QUANTIZATION));
  const buckets = new Map();
  for (const candidate of unmatchedNew) {
    const key = candidate.record.material + ':' + centroidCell(candidate.record).join(',');
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(candidate);
  }
  for (const old of unmatchedOld) {
    const cell = centroidCell(old.record); let best;
    for (let x = -1; x <= 1; x++) for (let y = -1; y <= 1; y++) for (let z = -1; z <= 1; z++) {
      const key = old.record.material + ':' + [cell[0] + x, cell[1] + y, cell[2] + z].join(',');
      for (const candidate of buckets.get(key) ?? []) {
        if (candidate.used) continue;
        for (let rotation = 0; rotation < 3; rotation++) {
          const distance = Math.max(...old.record.points.map((p, j) => Math.hypot(...p.map((v, k) => v - candidate.record.points[(j + rotation) % 3][k]))));
          if (distance <= POSITION_QUANTIZATION && (!best || distance < best.distance)) best = { candidate, rotation, distance };
        }
      }
    }
    if (best) {
      best.candidate.used = true;
      pairs.push({ old: old.record, current: best.candidate.record, rotation: best.rotation });
    } else removed.push({ key: old.key, area: old.record.area, altitude: old.record.altitude, quantizedCollinear: old.record.quantizedCollinear });
  }
  added.push(...unmatchedNew.filter(r => !r.used).map(r => r.key));
  let maxPositionDeltaM = 0;
  for (const pair of pairs) {
    const delta = Math.max(...pair.old.normals.flatMap((n, j) => n.map((v, k) => Math.abs(v - pair.current.normals[(j + pair.rotation) % 3][k]))));
    maxPositionDeltaM = Math.max(maxPositionDeltaM, ...pair.old.points.map((p, j) => Math.hypot(...p.map((v, k) => v - pair.current.points[(j + pair.rotation) % 3][k]))));
    maxNormalDelta = Math.max(maxNormalDelta, delta);
    if (delta > 1e-4) changedNormalTriangles++;
  }
  receipt = { status: 'PENDING', before: summarize(before), after: summarize(after),
    positionToleranceM: POSITION_QUANTIZATION, maxPositionDeltaM, numericalResidueAltitudeLimitM: NUMERICAL_RESIDUE_ALTITUDE,
    removedPositiveAreaResidues: removed, addedSurfaceKeys: added,
    addedSurfaceDetails: unmatchedNew.filter(r => !r.used).map(r => ({ key: r.key, ...r.record })),
    changedNormalTriangles, maxNormalDelta };
  if (precisionLineToleranceM) {
    receipt.precisionLineToleranceM = precisionLineToleranceM;
    if(precisionLineNodes.length)receipt.precisionLineNodes=precisionLineNodes;
    receipt.linePrecisionResidues = before.linePrecisionResidues;
    receipt.afterLinePrecisionResidues = after.linePrecisionResidues;
  }
  assert.equal(after.zero, 0); assert.equal(after.invalidNormals, 0);
  assert.ok(maxPositionDeltaM <= POSITION_QUANTIZATION, 'Matched surface vertex displacement exceeds tolerance');
  assert.equal(added.length, 0, 'Unintended oriented/material surfaces added');
  assert.ok(removed.every(r => r.altitude <= NUMERICAL_RESIDUE_ALTITUDE && r.quantizedCollinear), 'Meaningful original surfaces removed');
  if (!allowNormalDrift) assert.equal(changedNormalTriangles, 0, 'Delivered shading normals must be preserved');
  assert.equal(before.triangles - after.triangles, before.zero + removed.length +
    before.linePrecisionResidues.length - after.linePrecisionResidues.length);
  assert.deepEqual(after.roots, before.roots, 'Asset root transforms preserved');
  for (const side of ['min', 'max']) after.bounds[side].forEach((v, i) => assert.ok(Math.abs(v - before.bounds[side][i]) < 1e-6));
  assert.deepEqual(after.resolvedMaterialDefinitions, before.resolvedMaterialDefinitions,
    'Material definitions or embedded texture payloads changed');
  if(rigidOptIn){
    receipt.rigidContainerStaticOnly=true;
    if(allowNormalDrift)receipt.nativeClipComparison=compareNativeClips(before.clipData,after.clipData);
    else assert.deepEqual(after.animationPayload,before.animationPayload,'Canonical animation descriptor/accessor payload changed');
  }
  receipt.status = 'PASS';
  await fs.writeFile(output, JSON.stringify(receipt, null, 2) + '\n');
  console.log('PASS: GLB geometry repair; zero degenerate triangles; bounds, roots, material surfaces preserved within stated numeric limits');
} catch (error) {
  await fs.writeFile(output, JSON.stringify({ ...receipt, status: 'FAIL', error: error.message }, null, 2) + '\n');
  throw error;
}

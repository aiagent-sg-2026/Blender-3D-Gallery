// Independent comparison of static delivered GLBs, including numerical residue.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const [beforePath, afterPath, output] = process.argv.slice(2);
const allowNormalDrift = process.argv.includes('--allow-normal-drift');
assert.ok(beforePath && afterPath && output, 'Pass original GLB, repaired GLB and receipt path');
const POSITION_QUANTIZATION = 1e-6;
const NUMERICAL_RESIDUE_ALTITUDE = 1e-7;
async function inspect(file) {
  const bytes = await fs.readFile(file);
  const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
  const validation = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(validation.issues.numErrors, 0); assert.equal(validation.issues.numWarnings, 0);
  assert.equal(json.animations?.length ?? 0, 0, 'Animated assets require separate state/clip comparison');
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const surfaces = new Map(), roots = {};
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
      const record = { area, altitude: 2 * area / longestEdge, quantizedCollinear: quantizedArea === 0, normals };
      if (!surfaces.has(key)) surfaces.set(key, []);
      surfaces.get(key).push(record);
    }
  });
  const bounds = new Box3().setFromObject(gltf.scene);
  return { file, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), triangles, zero,
    invalidNormals, bounds: { min: bounds.min.toArray(), max: bounds.max.toArray() }, roots,
    materialDefinitions: json.materials, issues: validation.issues, surfaces };
}
const summarize = value => ({ ...value, surfaces: undefined });
let receipt;
try {
  const before = await inspect(beforePath), after = await inspect(afterPath);
  const removed = [], added = [];
  let changedNormalTriangles = 0, maxNormalDelta = 0;
  for (const [key, old] of before.surfaces) {
    const current = after.surfaces.get(key) ?? [];
    removed.push(...old.slice(current.length).map(record => ({ key, area: record.area, altitude: record.altitude, quantizedCollinear: record.quantizedCollinear })));
    for (let i = 0; i < Math.min(old.length, current.length); i++) {
      const delta = Math.max(...old[i].normals.flatMap((n, j) => n.map((v, k) => Math.abs(v - current[i].normals[j][k]))));
      maxNormalDelta = Math.max(maxNormalDelta, delta);
      if (delta > 1e-4) changedNormalTriangles++;
    }
  }
  for (const [key, current] of after.surfaces) {
    if (current.length > (before.surfaces.get(key)?.length ?? 0)) added.push(key);
  }
  receipt = { status: 'PENDING', before: summarize(before), after: summarize(after),
    positionQuantizationM: POSITION_QUANTIZATION, numericalResidueAltitudeLimitM: NUMERICAL_RESIDUE_ALTITUDE,
    removedPositiveAreaResidues: removed, addedSurfaceKeys: added, changedNormalTriangles, maxNormalDelta };
  assert.equal(after.zero, 0); assert.equal(after.invalidNormals, 0);
  assert.equal(added.length, 0, 'Unintended oriented/material surfaces added');
  assert.ok(removed.every(r => r.altitude <= NUMERICAL_RESIDUE_ALTITUDE && r.quantizedCollinear), 'Meaningful original surfaces removed');
  if (!allowNormalDrift) assert.equal(changedNormalTriangles, 0, 'Delivered shading normals must be preserved');
  assert.equal(before.triangles - after.triangles, before.zero + removed.length);
  assert.deepEqual(after.roots, before.roots, 'Asset root transforms preserved');
  for (const side of ['min', 'max']) after.bounds[side].forEach((v, i) => assert.ok(Math.abs(v - before.bounds[side][i]) < 1e-6));
  const materials = values => {
    assert.equal(new Set(values.map(m => m.name)).size, values.length);
    return values.slice().sort((a, b) => a.name.localeCompare(b.name));
  };
  assert.deepEqual(materials(after.materialDefinitions), materials(before.materialDefinitions));
  receipt.status = 'PASS';
  await fs.writeFile(output, JSON.stringify(receipt, null, 2) + '\n');
  console.log('PASS: static GLB repair; zero degenerate triangles; bounds, roots, material surfaces preserved within stated numeric limits');
} catch (error) {
  await fs.writeFile(output, JSON.stringify({ ...receipt, status: 'FAIL', error: error.message }, null, 2) + '\n');
  throw error;
}

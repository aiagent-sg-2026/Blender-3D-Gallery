// Compare actual old/new GLBs; never infer quality from the source generator.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const [before, after, output] = process.argv.slice(2);
assert.ok(before && after && output, 'Pass baseline collection, repaired collection, receipt path');
const ids = ['mall-queue-post', 'mall-queue-short', 'mall-queue-long'];
const expectedRemoved = [480, 960, 960];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const quantize = point => point.map(value => Math.round(value * 1e6)).join(',');
async function inspect(folder, id) {
  const bytes = await fs.readFile(path.join(folder, 'exports', id + '.glb'));
  const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
  const validation = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(validation.issues.numErrors, 0); assert.equal(validation.issues.numWarnings, 0);
  assert.equal(json.scenes.length, 1); assert.equal(json.images?.length ?? 0, 0);
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const triangles = new Map(), modules = {}, bounds = new Box3().setFromObject(gltf.scene);
  let count = 0, zero = 0, invalidNormals = 0;
  gltf.scene.traverse(object => {
    if (object.name.startsWith('MODULE_') && !object.isMesh) modules[object.name] = object.getWorldPosition(new Vector3()).toArray();
    if (!object.isMesh) return;
    const geometry = object.geometry, positions = geometry.attributes.position, normal = geometry.attributes.normal;
    assert.ok(normal, 'Expected exported shading normals');
    const indices = geometry.index, indicesCount = indices?.count ?? positions.count;
    if (object.name.startsWith('MODULE_') && !object.parent.name.startsWith('MODULE_')) modules[object.name] = object.getWorldPosition(new Vector3()).toArray();
    if (normal) for (let i = 0; i < normal.count; i++) {
      const length = Math.hypot(normal.getX(i), normal.getY(i), normal.getZ(i));
      if (!Number.isFinite(length) || Math.abs(length - 1) > .01) invalidNormals++;
    }
    for (let i = 0; i < indicesCount; i += 3) {
      const points = [0, 1, 2].map(offset => new Vector3().fromBufferAttribute(positions, indices ? indices.getX(i + offset) : i + offset).applyMatrix4(object.matrixWorld));
      const area = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0])).length() * .5;
      count++;
      if (area === 0) { zero++; continue; }
      const keys = points.map(point => quantize(point.toArray()));
      const oriented = keys.map((_, index) => [keys[index], keys[(index + 1) % 3], keys[(index + 2) % 3]].join('|')).sort()[0];
      const key = object.material.name + ':' + oriented;
      triangles.set(key, (triangles.get(key) ?? 0) + 1);
    }
  });
  return { bytes: bytes.length, sha256: hash(bytes), count, zero, invalidNormals,
    dimensions: bounds.getSize(new Vector3()).toArray(), min: bounds.min.toArray(), max: bounds.max.toArray(),
    modules, materialDefinitions: json.materials, issues: validation.issues, triangles };
}
const results = [];
try {
  for (const [index, id] of ids.entries()) {
    const old = await inspect(before, id), current = await inspect(after, id);
    const removed = [...old.triangles].filter(([key, count]) => current.triangles.get(key) !== count);
    const added = [...current.triangles].filter(([key, count]) => old.triangles.get(key) !== count);
    const record = { id, before: { ...old, triangles: undefined }, after: { ...current, triangles: undefined },
      nondegenerateSurfaceDifferences: { removed: removed.length, added: added.length },
      surfaceToleranceM: 1e-6 };
    results.push(record);
    assert.equal(current.zero, 0, id + ': no remaining zero-area triangles');
    assert.equal(old.zero, expectedRemoved[index]);
    assert.equal(old.count - current.count, expectedRemoved[index]);
    assert.equal(current.invalidNormals, 0);
    const namedMaterials = values => {
      assert.equal(new Set(values.map(m => m.name)).size, values.length, 'Named material identities must be unique in this kit');
      return values.slice().sort((a, b) => a.name.localeCompare(b.name));
    };
    assert.deepEqual(namedMaterials(current.materialDefinitions), namedMaterials(old.materialDefinitions), id + ': named material definitions preserved');
    for (const key of ['dimensions', 'min', 'max']) current[key].forEach((value, i) => assert.ok(Math.abs(value - old[key][i]) < 1e-6, id + ': ' + key));
    assert.deepEqual(current.modules, old.modules, id + ': module pivots preserved');
    assert.equal(removed.length, 0, id + ': original nondegenerate oriented/material surfaces retained');
    assert.equal(added.length, 0, id + ': no unintended surfaces added');
  }
  await fs.writeFile(output, JSON.stringify({ status: 'PASS', results }, null, 2) + '\n');
  console.log('PASS: 2400 degenerate triangles removed; oriented material surfaces, bounds and module pivots preserved');
} catch (error) {
  await fs.writeFile(output, JSON.stringify({ status: 'FAIL', error: error.message, results }, null, 2) + '\n');
  throw error;
}

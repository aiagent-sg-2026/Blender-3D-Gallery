import assert from 'node:assert/strict';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Box3 } from 'three';
import validator from 'gltf-validator';
import { readGlb } from './glb.mjs';

const dir = fileURLToPath(new URL('.', import.meta.url));
const report = JSON.parse(fs.readFileSync(dir + 'reports/sources.json'));
const original = await readGlb(dir + 'exports/optimized.glb');
const edited = await readGlb(dir + 'reports/source-edit/edited.glb');
assert.notDeepEqual(original.bytes, edited.bytes);
const validation = await validator.validateBytes(new Uint8Array(edited.bytes));
assert.equal(validation.issues.numErrors, 0);
assert.equal(validation.issues.numWarnings, 0);
const before = original.scene.getObjectByName(report.edited_mesh);
const after = edited.scene.getObjectByName(report.edited_mesh);
assert.ok(before && after);
const beforeBounds = new Box3().setFromObject(before, true);
const afterBounds = new Box3().setFromObject(after, true);
assert.ok(Math.abs(beforeBounds.max.x - .5) < 1e-6);
assert.ok(Math.abs(afterBounds.max.x - .485) < 1e-6, 'Upper plinth becomes widest after platform edit');
assert.ok(Math.abs(afterBounds.min.x + .485) < 1e-6);
assert.ok(edited.json.materials.some(material => material.name === 'Matte finish' &&
  Math.abs(material.pbrMetallicRoughness.roughnessFactor - .77) < 1e-5));
// Bevel evaluation and vertex deduplication may change the exported vertex count.
for (const name of ['BATCH_Satinmetal', 'BATCH_Clearblister']) {
  assert.deepEqual(original.scene.getObjectByName(name).geometry.attributes.position.array,
    edited.scene.getObjectByName(name).geometry.attributes.position.array, 'Unedited geometry remains identical');
}
console.log('PASS saved source platform edit and matte roughness survive GLB export');

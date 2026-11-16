import assert from 'node:assert/strict';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const dir = fileURLToPath(new URL('.', import.meta.url));
async function read(relative) {
  const bytes = fs.readFileSync(dir + relative);
  const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  return { bytes, json, scene: gltf.scene };
}
const source = await read('exports/optimized.glb');
const reexport = await read('reports/source-edit/source-reexport.glb');
const edited = await read('reports/source-edit/edited.glb');
assert.deepEqual(source.bytes, reexport.bytes, 'Saved source exports the exact tested artifact');
assert.notDeepEqual(source.bytes, edited.bytes);
const validation = await validator.validateBytes(new Uint8Array(edited.bytes));
assert.equal(validation.issues.numErrors, 0); assert.equal(validation.issues.numWarnings, 0);
const bounds = asset => new Box3().setFromObject(asset.scene.getObjectByName('BATCH_Laminate'), true).getSize(new Vector3());
assert.ok(Math.abs(bounds(edited).x / bounds(source).x - .92) < 1e-5, 'Real mesh edit survives batching');
assert.ok(edited.json.materials.some(material => Math.abs(material.pbrMetallicRoughness.roughnessFactor - .77) < 1e-5));
console.log('PASS saved source identity, persistent mesh edit and material edit, Khronos 0 errors / 0 warnings');

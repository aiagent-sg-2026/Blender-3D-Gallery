import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import validator from 'gltf-validator';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {report} from './qa-utils.mjs';

const here = path.dirname(new URL(import.meta.url).pathname);
const whitebox = path.join(here, 'whitebox');
const hash = data => createHash('sha256').update(data).digest('hex');
const layout = JSON.parse(await fs.readFile(path.join(whitebox, 'layout.json')));
const manifest = JSON.parse(await fs.readFile(path.join(whitebox, 'runtime/source-manifest.json')));
const build = JSON.parse(await fs.readFile(path.join(here, 'reports/geometry-build.json')));
assert.equal(hash(await fs.readFile(path.join(whitebox, 'layout.json'))), build.layout_sha256);
for (const file of [...manifest.files.map(f => ({...f, path: 'whitebox/runtime/' + f.path})), ...build.files]) {
  const bytes = await fs.readFile(path.join(here, file.path));
  assert.equal(bytes.length, file.bytes, file.path);
  assert.equal(hash(bytes), file.sha256, file.path);
}
const bytes = await fs.readFile(path.join(whitebox, 'foundation-v1.glb'));
const checked = await validator.validateBytes(new Uint8Array(bytes), {uri: 'foundation-v1.glb'});
assert.equal(checked.issues.numErrors, 0);
assert.equal(checked.issues.numWarnings, 0);
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const meshes = [];
gltf.scene.traverse(o => { if (o.isMesh) meshes.push(o); });
assert.equal(meshes.length, 43);
for (const part of layout.parts) {
  const object = meshes.find(o => o.userData.layout_id === part.id);
  assert.ok(object, part.id);
  const bounds = new T.Box3().setFromObject(object);
  const center = bounds.getCenter(new T.Vector3()).toArray();
  const size = bounds.getSize(new T.Vector3()).toArray();
  for (let i = 0; i < 3; i++) {
    assert.ok(Math.abs(center[i] - part.center[i]) < .00001, `${part.id} centre ${i}`);
    assert.ok(Math.abs(size[i] - part.size[i]) < .00001, `${part.id} size ${i}`);
  }
}
await report(path.join(here, 'reports/artifact-validation.json'), {
  status: 'PASS', checkedAt: new Date().toISOString(),
  manifestFiles: manifest.files.length, buildFiles: build.files.length,
  matchingGlbParts: meshes.length, toleranceMetres: .00001,
  validator: {version: checked.validatorVersion, issues: checked.issues},
  note: 'GLB world bounds are compared against the authoritative +Y-up layout; browser traversal loads this same GLB.',
});
console.log('PASS: runtime/build hashes, GLB validator and 43 exported part bounds');

import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const here = path.dirname(fileURLToPath(import.meta.url));
const packages = process.argv.slice(2);
assert.equal(packages.length, 2, 'Pass the reviewed Texel Density 2026.1.1 and Print3D 1.5.0 ZIP paths');
const expectedHashes = ['ca5554ec5c08a830c344ddc08a4c4f8f2e619178ac05ef582ea0293ab540308d',
  '3e3121a8052d52ce1fe8fd13bc6431679018f0cf1cb51ac0224fc47073a8e12a'];
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
for (const [i, file] of packages.entries()) {
  assert.equal(sha256(await fs.readFile(file)), expectedHashes[i], `Package differs from reviewed official bytes: ${file}`);
}
const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'blender-p0-check-'));
const config = path.join(temporary, 'config'), extensions = path.join(temporary, 'extensions');
await fs.mkdir(config); await fs.mkdir(extensions);
let receipt, log = '';
try {
  const args = ['--background', '--factory-startup', '--disable-autoexec', '--threads', '2',
    '--python-exit-code', '23', '--python', path.join(here, 'probe.py'), '--', '--output', temporary,
    '--packages', ...packages.map(file => path.resolve(file))];
  const code = await new Promise((resolve, reject) => {
    const child = spawn(process.env.BLENDER_BIN || '/Applications/Blender.app/Contents/MacOS/Blender', args, {
      env: { ...process.env, BLENDER_USER_CONFIG: config, BLENDER_USER_EXTENSIONS: extensions },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const timeout = setTimeout(() => child.kill('SIGTERM'), 90000);
    child.stdout.on('data', data => { log += data; });
    child.stderr.on('data', data => { log += data; });
    child.on('error', error => { clearTimeout(timeout); reject(error); });
    child.on('close', code => { clearTimeout(timeout); resolve(code); });
  });
  assert.equal(code, 0, log.slice(-6000));
  const observations = JSON.parse(await fs.readFile(path.join(temporary, 'observations.json'), 'utf8'));
  assert.equal(observations.status, 'PASS');
  const bytes = await fs.readFile(path.join(temporary, 'closed-cube.glb'));
  const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
  assert.equal(json.scenes.length, 1, 'No non-fixture scenes in the binary');
  assert.equal(json.meshes.length, 1, 'No non-fixture meshes in the binary');
  const validation = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(validation.issues.numErrors, 0);
  assert.equal(validation.issues.numWarnings, 0);
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  const meshes = [];
  gltf.scene.traverse(object => { if (object.isMesh) meshes.push(object); });
  assert.equal(meshes.length, 1);
  assert.equal((meshes[0].geometry.index?.count ?? meshes[0].geometry.attributes.position.count) / 3, 12);
  const size = new THREE.Box3().setFromObject(gltf.scene).getSize(new THREE.Vector3()).toArray();
  assert.ok(size.every(value => Math.abs(value - 1) < 1e-6));
  receipt = { status: 'PASS', checkedAt: new Date().toISOString(),
    packageSha256: expectedHashes, probeSha256: sha256(await fs.readFile(path.join(here, 'probe.py'))),
    observations, glb: { bytes: bytes.length, sha256: sha256(bytes), scenes: 1, meshes: 1, triangles: 12, size, issues: validation.issues },
    scope: 'Fresh isolated registration and background calls on owned fixtures. The native TD setter context failure is expected and is not headless setter support.' };
  console.log('PASS: registration, density measurements, geometry reports and independent GLB checks; background TD setter requires a real editor.');
} catch (error) {
  receipt = { status: 'FAIL', error: error.message, logTail: log.slice(-6000) };
  throw error;
} finally {
  const destination = path.join(here, 'background.json');
  await fs.writeFile(destination + '.tmp', JSON.stringify(receipt, null, 2) + '\n');
  await fs.rename(destination + '.tmp', destination);
  await fs.rm(temporary, { recursive: true, force: true });
}

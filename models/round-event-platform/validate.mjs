// Asset quality gate adapted from the self-checkout-machine template.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {Box3, Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const file = new URL('exports/optimized.glb', import.meta.url);
const bytes = fs.readFileSync(file);
const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
const validation = await validator.validateBytes(new Uint8Array(bytes), {maxIssues: 1000});
fs.writeFileSync(new URL('reports/khronos.json', import.meta.url), JSON.stringify(validation, null, 2) + '\n');
assert.equal(validation.issues.numErrors, 0);
assert.equal(validation.issues.numWarnings, 0);
assert.ok(json.buffers.every(b => !b.uri));
for (const key of ['images', 'textures', 'animations', 'cameras']) assert.ok(!json[key]?.length, key);
assert.ok(!json.extensions?.KHR_lights_punctual);
assert.equal(json.materials.length, 3);
assert.deepEqual(json.materials.map(m => m.name), ['Platform_Top', 'Platform_Edge', 'Platform_BaseTrim']);
for (const material of json.materials) {
  assert.equal(material.pbrMetallicRoughness.metallicFactor, 0);
  assert.ok(!material.emissiveFactor?.some(v => v > 0));
  assert.ok(!material.doubleSided);
  assert.ok(!material.alphaMode || material.alphaMode === 'OPAQUE');
}
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const root = gltf.scene.getObjectByName('ASSET_RoundEventPlatform');
assert.ok(root);
assert.deepEqual(root.position.toArray(), [0, 0, 0]);
assert.equal(root.userData.units, 'metres');
assert.equal(root.userData.origin, 'floor centre');
const bounds = new Box3().setFromObject(gltf.scene, true);
const dimensions = bounds.getSize(new Vector3()).toArray();
for (let i = 0; i < 3; i++) assert.ok(Math.abs(dimensions[i] - [8, .3, 8][i]) < 1e-6);
assert.ok(Math.abs(bounds.min.y) < 1e-7);
assert.ok(Math.abs(bounds.min.x + bounds.max.x) < 1e-7);
assert.ok(Math.abs(bounds.min.z + bounds.max.z) < 1e-7);
let triangles = 0, meshes = 0, vertices = 0, uvAreaMin = Infinity, areaMin = Infinity;
const parts = [];
gltf.scene.traverse(obj => {
  if (!obj.isMesh) return;
  meshes++;
  const geometry = obj.geometry;
  const {position, normal, uv} = geometry.attributes;
  assert.ok(position && normal && uv, 'position, normals and UVs are exported');
  assert.equal(position.count, uv.count);
  for (const attribute of [position, normal, uv]) assert.ok([...attribute.array].every(Number.isFinite));
  assert.ok([...uv.array].every(v => v >= 0 && v <= 1), 'padded unit UV atlas');
  vertices += position.count;
  const count = geometry.index?.count ?? position.count;
  triangles += count / 3;
  const index = i => geometry.index ? geometry.index.getX(i) : i;
  for (let i = 0; i < position.count; i++) {
    const p = new Vector3().fromBufferAttribute(position, i).applyMatrix4(obj.matrixWorld);
    const n = new Vector3().fromBufferAttribute(normal, i).transformDirection(obj.matrixWorld);
    assert.ok(Math.hypot(p.x, p.z) <= 4.000001, 'circular footprint');
    assert.ok(Math.abs(n.length() - 1) < 1e-6);
    assert.ok(p.x * n.x + p.z * n.z + (p.y - .15) * n.y > 0, 'outward normals');
  }
  for (let i = 0; i < count; i += 3) {
    const ids = [index(i), index(i + 1), index(i + 2)];
    const [a, b, c] = ids.map(j => new Vector3().fromBufferAttribute(position, j));
    const area = b.clone().sub(a).cross(c.clone().sub(a)).length() / 2;
    assert.ok(area > 1e-9, 'nondegenerate triangle');
    areaMin = Math.min(areaMin, area);
    const [u, v, w] = ids.map(j => [uv.getX(j), uv.getY(j)]);
    const uvArea = Math.abs((v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])) / 2;
    assert.ok(uvArea > 1e-12, 'nondegenerate UV triangle');
    uvAreaMin = Math.min(uvAreaMin, uvArea);
  }
  parts.push({name: obj.name, material: obj.material.name, triangles: count / 3});
});
assert.equal(meshes, 3, 'one opaque primitive per shared material');
assert.equal(json.meshes.length, 1);
assert.ok(triangles < 8000);
assert.ok(bytes.length < 1.5 * 1024 * 1024);
const report = {
  result: 'PASS', id: 'round-event-platform', triangles, vertices,
  stored_meshes: json.meshes.length, runtime_meshes: meshes, mesh_primitives: meshes,
  opaque_draw_calls_per_pass: meshes, materials: json.materials.length, glb_bytes: bytes.length,
  dimensions, bounds: {min: bounds.min.toArray(), max: bounds.max.toArray()},
  minimum_triangle_area_m2: areaMin, minimum_uv_triangle_area: uvAreaMin,
  animations: gltf.animations.length, sha256: createHash('sha256').update(bytes).digest('hex'),
  validation: {errors: validation.issues.numErrors, warnings: validation.issues.numWarnings, version: validator.version()},
  budget: {triangles_exclusive: 8000, bytes_exclusive: 1572864, materials: 3, mesh_primitives: 3}, parts
};
fs.writeFileSync(new URL('reports/assets.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

import assert from 'node:assert/strict';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const dir = fileURLToPath(new URL('.', import.meta.url));
const bytes = fs.readFileSync(dir + 'exports/optimized.glb');
const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
const validation = await validator.validateBytes(new Uint8Array(bytes), { maxIssues: 100 });
fs.writeFileSync(dir + 'reports/khronos.json', JSON.stringify(validation, null, 2) + '\n');
assert.equal(validation.issues.numErrors, 0);
assert.equal(validation.issues.numWarnings, 0);
assert.ok(json.buffers.every(buffer => !buffer.uri));
assert.ok(!json.images?.length && !json.textures?.length && !json.cameras?.length);
assert.ok(!json.extensions?.KHR_lights_punctual);
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const root = gltf.scene.getObjectByName('ASSET_TVWallMounted');
assert.ok(root);
assert.deepEqual(root.position.toArray(), [0, 0, 0]);
assert.equal(root.userData.units, 'metres');
assert.equal(gltf.animations.length, 0);
const parts = {};
let triangles = 0, vertices = 0, primitives = 0;
gltf.scene.traverse(object => {
  if (!object.isMesh) return;
  const geometry = object.geometry, position = geometry.attributes.position, index = geometry.index;
  assert.ok(geometry.attributes.normal);
  assert.ok([...position.array].every(Number.isFinite));
  const count = index?.count ?? position.count;
  assert.equal(count % 3, 0);
  const a = new Vector3(), b = new Vector3(), c = new Vector3();
  for (let i = 0; i < count; i += 3) {
    a.fromBufferAttribute(position, index ? index.getX(i) : i);
    b.fromBufferAttribute(position, index ? index.getX(i + 1) : i + 1);
    c.fromBufferAttribute(position, index ? index.getX(i + 2) : i + 2);
    assert.ok(b.sub(a).cross(c.sub(a)).lengthSq() > 1e-20, 'nondegenerate triangle');
  }
  triangles += count / 3;
  vertices += position.count;
  primitives += Math.max(1, geometry.groups.length);
  const bounds = new Box3().setFromObject(object, true);
  parts[object.name] = { min: bounds.min.toArray(), max: bounds.max.toArray(), triangles: count / 3 };
});
for (const name of ['PANEL_Housing', 'SCREEN_StandbyPanel', 'MOUNT_VESAWallBracket']) {
  assert.ok(parts[name], 'required editable module ' + name);
}
const bounds = new Box3().setFromObject(root, true), dimensions = bounds.getSize(new Vector3()).toArray();
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-5, `${a} != ${b}`);
near(dimensions[0], 1.23); near(dimensions[1], .72); near(dimensions[2], .146);
near(bounds.min.y, 1.11); near(bounds.max.y, 1.83);
near(bounds.min.x + bounds.max.x, 0); near(bounds.min.z + bounds.max.z, 0);
const panel = parts.PANEL_Housing, screen = parts.SCREEN_StandbyPanel, bracket = parts.MOUNT_VESAWallBracket;
near(panel.max[0] - panel.min[0], 1.23); near(panel.max[1] - panel.min[1], .72);
near((screen.max[0] - screen.min[0]) / (screen.max[1] - screen.min[1]), 16 / 9);
assert.ok(screen.max[2] > panel.max[2], 'front is +Z');
assert.ok(bracket.min[2] < panel.min[2] && bracket.max[2] > panel.min[2], 'bracket joins rear of panel');
near(bracket.min[2], root.userData.wall_plane_gltf_z);
const screenMaterial = gltf.scene.getObjectByName('SCREEN_StandbyPanel').material;
assert.ok(screenMaterial.emissive.toArray().every(value => value > 0 && value < .02));
assert.equal(screenMaterial.transparent, false);
assert.ok(triangles < 20000); assert.ok(bytes.length < 1.5 * 1024 * 1024);
assert.ok(json.materials.length <= 3); assert.ok(primitives <= 3);
assert.equal(json.materials.length, new Set(json.materials.map(material => material.name)).size);
const report = {
  result: 'PASS', id: 'tv-wall-mounted', glb_bytes: bytes.length, triangles, vertices,
  meshes: Object.keys(parts).length, primitives, materials: json.materials.length,
  dimensions, dimensions_order: 'width, height, depth (glTF X,Y,Z)',
  bounds: { min: bounds.min.toArray(), max: bounds.max.toArray() },
  panel_dimensions: [panel.max[0] - panel.min[0], panel.max[1] - panel.min[1], panel.max[2] - panel.min[2]],
  active_screen_diagonal_inches: Math.hypot(screen.max[0] - screen.min[0], screen.max[1] - screen.min[1]) / .0254,
  screen_emissive_factor: screenMaterial.emissive.toArray(),
  sha256: createHash('sha256').update(bytes).digest('hex'),
  validation: { errors: validation.issues.numErrors, warnings: validation.issues.numWarnings },
  images: json.images?.length ?? 0, animations: gltf.animations.length, parts,
};
fs.writeFileSync(dir + 'reports/assets.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

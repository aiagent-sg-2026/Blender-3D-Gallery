import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const dir = fileURLToPath(new URL('.', import.meta.url));
const spec = JSON.parse(fs.readFileSync(dir + 'backlog.json'));
const source = JSON.parse(fs.readFileSync(dir + 'reports/source-geometry.json'));
const bytes = fs.readFileSync(dir + 'exports/optimized.glb');
const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
const validation = await validator.validateBytes(new Uint8Array(bytes), { maxIssues: 100 });
fs.writeFileSync(dir + 'reports/khronos.json', JSON.stringify(validation, null, 2) + '\n');
assert.equal(validation.issues.numErrors, 0);
assert.equal(validation.issues.numWarnings, 0);
assert.ok(!json.images?.length && !json.textures?.length && !json.cameras?.length);
assert.ok(!json.extensions?.KHR_lights_punctual);
assert.ok(json.buffers.every(buffer => buffer.uri === undefined));
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const root = gltf.scene.getObjectByName(spec.root);
assert.ok(root);
assert.deepEqual(root.position.toArray(), [0, 0, 0]);
assert.equal(root.userData.units, 'metres');
assert.equal(root.userData.front_axis, 'Blender -Y / glTF +Z');
assert.equal(gltf.animations.length, 0);

const positionsByMaterial = new Map();
let meshes = 0, primitives = 0, triangles = 0, vertices = 0;
gltf.scene.traverse(object => {
  if (!object.isMesh) return;
  meshes++;
  const geometry = object.geometry;
  const positions = geometry.attributes.position;
  const normals = geometry.attributes.normal;
  assert.ok(normals);
  assert.ok([...positions.array, ...normals.array].every(Number.isFinite));
  const list = [];
  for (let i = 0; i < positions.count; i++) list.push(new Vector3().fromBufferAttribute(positions, i).applyMatrix4(object.matrixWorld));
  positionsByMaterial.set(object.material.name, list);
  const index = geometry.index;
  const count = index?.count ?? positions.count;
  triangles += count / 3;
  vertices += positions.count;
  primitives += Math.max(geometry.groups.length, 1);
  const edgeA = new Vector3(), edgeB = new Vector3();
  for (let i = 0; i < count; i += 3) {
    const a = list[index ? index.getX(i) : i];
    const b = list[index ? index.getX(i + 1) : i + 1];
    const c = list[index ? index.getX(i + 2) : i + 2];
    assert.ok(edgeA.subVectors(b, a).cross(edgeB.subVectors(c, a)).lengthSq() > 1e-20, 'nondegenerate triangle');
  }
});
assert.equal(meshes, 2);
assert.equal(primitives, 2);
assert.equal(json.materials.length, 2);
assert.ok(triangles <= spec.budget.triangles);
assert.ok(bytes.length <= spec.budget.bytes);
const bounds = new Box3().setFromObject(gltf.scene, true);
const dimensions = bounds.getSize(new Vector3()).toArray();
assert.ok(dimensions.every(d => Math.abs(d-.22)<.002));
assert.ok(bounds.getCenter(new Vector3()).length()<1e-6, 'centre origin');
// Check every evaluated key vertex against the real merged GLB, allowing float32 rounding.
const buckets = new Map();
for (const [name, positions] of positionsByMaterial) {
  const map = new Map();
  for (const p of positions) {
    const key = p.toArray().map(v => Math.round(v * 1e5)).join(',');
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(p);
  }
  buckets.set(name, map);
}
function containsPosition(material, position) {
  const p = new Vector3(...position);
  const cell = position.map(v => Math.round(v * 1e5));
  for (let x = -1; x <= 1; x++) for (let y = -1; y <= 1; y++) for (let z = -1; z <= 1; z++) {
    const candidates = buckets.get(material).get([cell[0] + x, cell[1] + y, cell[2] + z].join(',')) ?? [];
    if (candidates.some(candidate => candidate.distanceTo(p) < 2e-6)) return true;
  }
  return false;
}
assert.equal(source.topology_vertices, 60);
assert.equal(source.panels.filter(p => p.sides===5).length, 12);
assert.equal(source.panels.filter(p => p.sides===6).length, 20);
for (const panel of source.panels) {
  assert.equal(panel.material, panel.sides===5 ? 'Black panels' : 'White panels');
  assert.ok(panel.positions.every(p => containsPosition(panel.material,p)), panel.name);
}
const report = {
  result: 'PASS', id: spec.slug, glb_bytes: bytes.length, triangles, vertices, meshes, primitives,
  materials: json.materials.length, textures: json.textures?.length ?? 0, animations: gltf.animations.length,
  dimensions_m: dimensions, bounds_m: { min: bounds.min.toArray(), max: bounds.max.toArray() },
  nodes: json.nodes.length, topology_vertices: 60, pentagons: 12, hexagons: 20,
  sha256: createHash('sha256').update(bytes).digest('hex'), budget: spec.budget,
  validation: { errors: validation.issues.numErrors, warnings: validation.issues.numWarnings },
};
fs.writeFileSync(dir + 'reports/assets.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

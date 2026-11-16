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
// One embedded tangent-space normal map for the pebbled grain; nothing external, no cameras or lights.
assert.equal(json.images?.length, 1);
assert.equal(json.textures?.length, 1);
assert.ok(json.images.every(image => image.bufferView !== undefined && image.uri === undefined));
assert.ok(!json.cameras?.length && !json.extensions?.KHR_lights_punctual);
assert.ok(json.buffers.every(buffer => buffer.uri === undefined));
const orangeMaterial = json.materials.find(m => m.name === 'Pebbled orange rubber');
const blackMaterial = json.materials.find(m => m.name === 'Black channel rubber');
assert.ok(orangeMaterial?.normalTexture && !blackMaterial?.normalTexture);
assert.equal(orangeMaterial.pbrMetallicRoughness.metallicFactor, 0);

// Node has no image decoder: parse geometry from a copy without the texture binding.
const jsonLength = bytes.readUInt32LE(12);
const bin = bytes.subarray(28 + jsonLength, 28 + jsonLength + bytes.readUInt32LE(20 + jsonLength));
const geometryJson = structuredClone(json);
delete geometryJson.images;
delete geometryJson.textures;
delete geometryJson.samplers;
for (const material of geometryJson.materials) delete material.normalTexture;
const jsonChunk = Buffer.from(JSON.stringify(geometryJson));
const paddedJson = Buffer.alloc(Math.ceil(jsonChunk.length / 4) * 4, 0x20);
jsonChunk.copy(paddedJson);
const binHeader = Buffer.alloc(8);
binHeader.writeUInt32LE(bin.length, 0);
binHeader.writeUInt32LE(0x004e4942, 4);
const header = Buffer.alloc(20);
header.writeUInt32LE(0x46546c67, 0);
header.writeUInt32LE(2, 4);
header.writeUInt32LE(20 + paddedJson.length + 8 + bin.length, 8);
header.writeUInt32LE(paddedJson.length, 12);
header.writeUInt32LE(0x4e4f534a, 16);
const geometryGlb = Buffer.concat([header, paddedJson, binHeader, bin]);
const gltf = await new GLTFLoader().parseAsync(geometryGlb.buffer.slice(geometryGlb.byteOffset, geometryGlb.byteOffset + geometryGlb.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const root = gltf.scene.getObjectByName(spec.root);
assert.ok(root);
assert.deepEqual(root.position.toArray(), [0, 0, 0]);
assert.equal(root.userData.units, 'metres');
assert.equal(root.userData.front_axis, 'Blender -Y / glTF +Z');
assert.equal(gltf.animations.length, 0);

const R = source.radius_m, groove = source.channel_radius_m;
const centre = new Vector3(0, R, 0);
const byMaterial = new Map();
let meshes = 0, primitives = 0, triangles = 0, vertices = 0;
gltf.scene.traverse(object => {
  if (!object.isMesh) return;
  meshes++;
  const geometry = object.geometry;
  const positions = geometry.attributes.position;
  assert.ok(geometry.attributes.normal && geometry.attributes.uv);
  assert.ok([...positions.array, ...geometry.attributes.normal.array].every(Number.isFinite));
  const list = [];
  for (let i = 0; i < positions.count; i++) list.push(new Vector3().fromBufferAttribute(positions, i).applyMatrix4(object.matrixWorld));
  const index = geometry.index, count = index?.count ?? positions.count;
  const tris = [];
  const edgeA = new Vector3(), edgeB = new Vector3();
  for (let i = 0; i < count; i += 3) {
    const t = [0, 1, 2].map(k => index ? index.getX(i + k) : i + k);
    assert.ok(edgeA.subVectors(list[t[1]], list[t[0]]).cross(edgeB.subVectors(list[t[2]], list[t[0]])).lengthSq() > 1e-20, 'nondegenerate triangle');
    tris.push(t);
  }
  byMaterial.set(object.material.name, { list, tris });
  triangles += count / 3;
  vertices += positions.count;
  primitives++;
});
assert.equal(primitives, 2);
assert.equal(json.meshes.length, 1);
assert.equal(json.materials.length, 2);
assert.ok(triangles <= spec.budget.triangles);
assert.ok(bytes.length <= spec.budget.bytes);

const bounds = new Box3().setFromObject(gltf.scene, true);
const dimensions = bounds.getSize(new Vector3()).toArray();
// The pole sits in the seam crossing, so the lowest skin vertex is a few hundredths of a mm above the datum.
assert.ok(bounds.min.y >= -1e-6 && bounds.min.y < 2e-4, 'resting on floor datum');
assert.ok(Math.abs(bounds.min.x + bounds.max.x) < 1e-5 && Math.abs(bounds.min.z + bounds.max.z) < 1e-5, 'centred on origin');
// Extreme axis points fall inside seam channels, so measured extents are up to 0.3 mm under the 238.6 mm skin diameter.
for (const d of dimensions) assert.ok(d <= 2 * R + 1e-5 && d > 2 * R - 3e-4, 'size 7 diameter');
assert.ok(Math.abs(2 * Math.PI * R - 0.749) < 0.01, 'size 7 circumference 74.9 cm');

const orange = byMaterial.get('Pebbled orange rubber'), black = byMaterial.get('Black channel rubber');
assert.ok(orange.list.every(p => Math.abs(p.distanceTo(centre) - R) < 1e-4), 'orange shell on sphere surface');
assert.ok(black.list.every(p => p.distanceTo(centre) < R + 1e-4 && p.distanceTo(centre) > R - groove - 1e-4), 'channels recessed');

// Every sampled seam point has recessed black channel geometry beneath it.
for (const [name, points] of Object.entries(source.seams)) {
  for (const point of points) {
    const p = new Vector3(...point);
    const bottom = p.clone().sub(centre).setLength(R - groove * 0.9).add(centre);
    assert.ok(black.list.some(v => v.distanceTo(bottom) < groove * 0.8), `channel under ${name}`);
    assert.ok(!orange.list.some(v => v.distanceTo(p) < groove * 0.8), `no orange skin over ${name}`);
  }
}

function components({ list, tris }) {
  const key = v => v.toArray().map(x => Math.round(x * 1e6)).join(',');
  const ids = list.map(key), parent = new Map(ids.map(id => [id, id]));
  const find = a => { while (parent.get(a) !== a) { parent.set(a, parent.get(parent.get(a))); a = parent.get(a); } return a; };
  for (const [a, b, c] of tris) { parent.set(find(ids[b]), find(ids[a])); parent.set(find(ids[c]), find(ids[a])); }
  return new Set(ids.map(find)).size;
}
const panels = components(orange);
assert.equal(panels, source.panels, 'eight orange panels separated by channels');

const report = {
  result: 'PASS', id: spec.slug, glb_bytes: bytes.length, triangles, vertices, meshes, primitives,
  materials: json.materials.length, textures: json.textures.length, animations: gltf.animations.length,
  dimensions_m: dimensions, bounds_m: { min: bounds.min.toArray(), max: bounds.max.toArray() },
  diameter_m: 2 * R, circumference_m: source.circumference_m, channel_width_m: 2 * groove, channel_depth_m: groove,
  panels, seams: Object.keys(source.seams),
  sha256: createHash('sha256').update(bytes).digest('hex'), budget: spec.budget,
  validation: { errors: validation.issues.numErrors, warnings: validation.issues.numWarnings, infos: validation.issues.numInfos },
};
fs.writeFileSync(dir + 'reports/assets.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

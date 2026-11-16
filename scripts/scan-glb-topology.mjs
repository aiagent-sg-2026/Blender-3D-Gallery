// Read-only default-pose GLB audit. Input: {assets:[{id,file,file_sha256}]}.
// Hashes bind evidence to actual files; this does not certify animation or devices.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Matrix4, Quaternion, Vector3, Box3 } from 'three';
import validator from 'gltf-validator';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [manifest, destination] = process.argv.slice(2);
assert.ok(manifest && destination, 'Pass an inventory manifest and separate report directory');
const inventory = JSON.parse(await fs.readFile(manifest, 'utf8'));
assert.ok(Array.isArray(inventory.assets));
await fs.mkdir(path.join(destination, 'glb'), { recursive: true });
const readers = { 5120: ['getInt8', 1], 5121: ['getUint8', 1], 5122: ['getInt16', 2], 5123: ['getUint16', 2], 5125: ['getUint32', 4], 5126: ['getFloat32', 4] };
const sizes = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
for (const asset of inventory.assets) {
  assert.match(asset.id, /^[a-z0-9][a-z0-9-]*$/);
  assert.match(asset.file_sha256, /^[a-f0-9]{64}$/);
  assert.ok(!path.isAbsolute(asset.file));
  const input = path.resolve(root, asset.file);
  assert.ok(input.startsWith(root + path.sep), 'Inventory file must remain inside the repository');
  const bytes = await fs.readFile(input);
  assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.file_sha256);
  assert.equal(bytes.readUInt32LE(0), 0x46546c67);
  assert.equal(bytes.readUInt32LE(4), 2);
  assert.equal(bytes.readUInt32LE(8), bytes.length);
  let json, bin;
  for (let offset = 12; offset < bytes.length;) {
    const length = bytes.readUInt32LE(offset), type = bytes.readUInt32LE(offset + 4);
    assert.ok(offset + 8 + length <= bytes.length);
    const body = bytes.subarray(offset + 8, offset + 8 + length);
    if (type === 0x4e4f534a) json = JSON.parse(body.toString('utf8'));
    if (type === 0x004e4942) bin = body;
    offset += 8 + length;
  }
  assert.ok(json && bin);
  const unsafe = [...(json.buffers ?? []), ...(json.images ?? [])].filter(x => x.uri && !x.uri.startsWith('data:'));
  const validation = await validator.validateBytes(new Uint8Array(bytes), { uri: asset.file, maxIssues: 1000,
    externalResourceFunction: async () => { throw new Error('External resource denied in read-only scan'); } });
  const cache = new Map();
  function accessor(index) {
    if (cache.has(index)) return cache.get(index);
    const a = json.accessors[index];
    assert.ok(!a.sparse, 'Sparse accessor requires a separate decoder');
    const bv = json.bufferViews[a.bufferView]; assert.equal(bv.buffer, 0);
    const [method, width] = readers[a.componentType], components = sizes[a.type];
    const view = new DataView(bin.buffer, bin.byteOffset, bin.byteLength), values = [];
    for (let i = 0; i < a.count; i++) {
      const value = [];
      for (let c = 0; c < components; c++) value.push(view[method]((bv.byteOffset ?? 0) + (a.byteOffset ?? 0) + i * (bv.byteStride ?? width * components) + c * width, true));
      values.push(value);
    }
    cache.set(index, values); return values;
  }
  const scenes = json.scenes ?? [], defaultIndex = json.scene ?? 0;
  const hasMesh = index => {
    const stack = [...(scenes[index]?.nodes ?? [])], visited = new Set();
    while (stack.length) { const i = stack.pop(); if (visited.has(i)) continue; visited.add(i); if (json.nodes[i].mesh !== undefined) return true; stack.push(...(json.nodes[i].children ?? [])); }
    return false;
  };
  const defaultHasMesh = hasMesh(defaultIndex), scanIndex = defaultHasMesh ? defaultIndex : scenes.findIndex((_, i) => hasMesh(i));
  const primitives = [], bounds = new Box3();
  function visit(index, parent, ancestry = new Set()) {
    assert.ok(!ancestry.has(index), 'Node cycle');
    const node = json.nodes[index], local = node.matrix ? new Matrix4().fromArray(node.matrix) : new Matrix4().compose(
      new Vector3(...(node.translation ?? [0, 0, 0])), new Quaternion(...(node.rotation ?? [0, 0, 0, 1])), new Vector3(...(node.scale ?? [1, 1, 1])));
    const world = parent.clone().multiply(local);
    if (node.mesh !== undefined) for (const [pi, primitive] of json.meshes[node.mesh].primitives.entries()) {
      const positions = accessor(primitive.attributes.POSITION), indices = primitive.indices !== undefined ? accessor(primitive.indices).map(x => x[0]) : positions.map((_, i) => i);
      const points = positions.map(p => new Vector3(...p).applyMatrix4(world));
      let nonfinite = 0, exactZero = 0, nearZero = 0, triangles = 0;
      for (const point of points) { if (point.toArray().every(Number.isFinite)) bounds.expandByPoint(point); else nonfinite++; }
      const mode = primitive.mode ?? 4;
      if (mode === 4) for (let i = 0; i < indices.length; i += 3) {
        const a = points[indices[i]], b = points[indices[i + 1]], c = points[indices[i + 2]];
        assert.ok(a && b && c, 'Index outside position accessor');
        const area = b.clone().sub(a).cross(c.clone().sub(a)).length() * .5;
        if (area === 0) exactZero++;
        if (area <= 1e-12) nearZero++;
        triangles++;
      }
      let nonfiniteNormals = 0, nonunitNormals = 0;
      if (primitive.attributes.NORMAL !== undefined) for (const normal of accessor(primitive.attributes.NORMAL)) {
        if (!normal.every(Number.isFinite)) nonfiniteNormals++;
        else if (Math.abs(Math.hypot(...normal) - 1) > .01) nonunitNormals++;
      }
      primitives.push({ node: node.name ?? String(index), nodeIndex: index, meshIndex: node.mesh, primitive: pi,
        material: primitive.material, vertices: positions.length, triangles, mode, nonfinitePositions: nonfinite,
        exactZeroAreaTriangles: exactZero, nearZeroAreaTriangles: nearZero, nearZeroAreaThresholdM2: 1e-12,
        nonfiniteNormals, nonunitNormals, hasUv0: primitive.attributes.TEXCOORD_0 !== undefined });
    }
    for (const child of node.children ?? []) visit(child, world, new Set([...ancestry, index]));
  }
  if (scanIndex >= 0 && unsafe.length === 0 && validation.issues.numErrors === 0) for (const i of scenes[scanIndex].nodes ?? []) visit(i, new Matrix4());
  const metrics = { bytes: bytes.length, scenes: scenes.length, defaultScene: defaultIndex, defaultSceneHasMesh: defaultHasMesh, inspectedScene: scanIndex,
    meshOccurrences: new Set(primitives.map(p => p.nodeIndex)).size, primitives: primitives.length,
    triangles: primitives.reduce((s, p) => s + p.triangles, 0), images: json.images?.length ?? 0, materials: json.materials?.length ?? 0,
    dimensions: bounds.isEmpty() ? null : bounds.getSize(new Vector3()).toArray(),
    bounds: bounds.isEmpty() ? null : { min: bounds.min.toArray(), max: bounds.max.toArray() },
    exactZeroAreaTriangles: primitives.reduce((s, p) => s + p.exactZeroAreaTriangles, 0),
    nearZeroAreaTriangles: primitives.reduce((s, p) => s + p.nearZeroAreaTriangles, 0) };
  const result = { id: asset.id, sha256: asset.file_sha256, status: validation.issues.numErrors || unsafe.length ? 'HOLD_FORMAT' : 'SCANNED',
    validation: validation.issues, externalResources: unsafe.map(x => x.uri), metrics, primitives,
    images: json.images ?? [], materials: (json.materials ?? []).map(m => ({ name: m.name, pbrMetallicRoughness: m.pbrMetallicRoughness, normalTexture: m.normalTexture, occlusionTexture: m.occlusionTexture, emissiveTexture: m.emissiveTexture })),
    extensionsRequired: json.extensionsRequired ?? [],
    interpretation: 'Bind/default-pose structural measurements; no rendered appearance or browser/device performance acceptance.' };
  await fs.writeFile(path.join(destination, 'glb', asset.id + '.json'), JSON.stringify(result, null, 2) + '\n');
}
console.log(`GLB validation and raw geometry scanned: ${inventory.assets.length}`);

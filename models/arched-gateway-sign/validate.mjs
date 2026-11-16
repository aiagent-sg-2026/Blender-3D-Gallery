// Based on self-checkout-machine/validate.mjs; measure the actual clear aperture.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {Box3, Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const dir = fileURLToPath(new URL('.', import.meta.url));
const spec = JSON.parse(fs.readFileSync(dir + 'backlog.json'));
const bytes = fs.readFileSync(dir + 'exports/optimized.glb');
const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
const validation = await validator.validateBytes(new Uint8Array(bytes), {uri: 'optimized.glb'});
fs.writeFileSync(dir + 'reports/khronos.json', JSON.stringify(validation, null, 2) + '\n');
assert.equal(validation.issues.numErrors, 0);
assert.equal(validation.issues.numWarnings, 0);
assert.ok(json.buffers.every(b => !b.uri));
assert.ok(!json.images?.length && !json.textures?.length && !json.cameras?.length);
assert.ok(!json.extensions?.KHR_lights_punctual);
assert.equal(json.materials.length, 3);
assert.equal(json.meshes.length, 3);
assert.equal(json.meshes.reduce((n, m) => n + m.primitives.length, 0), 3);
assert.ok(json.materials.every(m => !m.alphaMode || m.alphaMode === 'OPAQUE'));
const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
gltf.scene.updateMatrixWorld(true);
const root = gltf.scene.getObjectByName(spec.root);
assert.ok(root);
assert.deepEqual(root.position.toArray(), [0, 0, 0]);
assert.equal(root.userData.units, 'metres');
assert.equal(gltf.animations.length, 0);
const bounds = new Box3().setFromObject(gltf.scene, true);
const dimensions = bounds.getSize(new Vector3()).toArray();
for (const [i, expected] of [12, 6, 1.3].entries()) assert.ok(Math.abs(dimensions[i] - expected) < 1e-6);
assert.ok(Math.abs(bounds.min.y) < 1e-7);
assert.ok(Math.abs(bounds.min.x + bounds.max.x) < 1e-6);
assert.ok(Math.abs(bounds.min.z + bounds.max.z) < 1e-6);

let triangles = 0, vertices = 0, minArea = Infinity;
const parts = {}, worldTriangles = [], groundPoints = [];
gltf.scene.traverse(o => {
  if (!o.isMesh) return;
  const geo = o.geometry, position = geo.attributes.position;
  assert.ok(geo.attributes.normal);
  assert.ok([...position.array, ...geo.attributes.normal.array].every(Number.isFinite));
  const points = Array.from({length: position.count}, (_, i) => new Vector3().fromBufferAttribute(position, i).applyMatrix4(o.matrixWorld));
  groundPoints.push(...points.filter(p => p.y < 3));
  const count = geo.index?.count ?? position.count;
  triangles += count / 3;
  vertices += position.count;
  for (let i = 0; i < count; i += 3) {
    const t = [0, 1, 2].map(j => points[geo.index ? geo.index.getX(i + j) : i + j]);
    const area = t[1].clone().sub(t[0]).cross(t[2].clone().sub(t[0])).length() / 2;
    assert.ok(area > 1e-12, `nondegenerate ${o.name}/${i / 3}`);
    minArea = Math.min(minArea, area);
    worldTriangles.push(t);
  }
  const b = new Box3().setFromObject(o, true);
  parts[o.name] = {min: b.min.toArray(), max: b.max.toArray(), triangles: count / 3};
});
for (const name of spec.features) assert.ok(parts[name], name);
assert.ok(triangles < spec.budget.triangles);
assert.ok(bytes.length < spec.budget.bytes);
const band = root.getObjectByName('SIGN_Band');
assert.equal(band.parent, root);
assert.ok(band.material.name.startsWith('Sign band warm white'));
const anchor = root.getObjectByName('SIGN_TextAnchor').getWorldPosition(new Vector3());
assert.ok(anchor.z > parts.SIGN_Band.max[2], 'text anchor faces glTF +Z');
assert.ok(Math.abs(anchor.y - band.getWorldPosition(new Vector3()).y) < 1e-6);

// Clip actual exported triangles, retaining the curved underside rather than its AABB.
function clip(poly, axis, limit, sign) {
  const result = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    const da = sign * (a.getComponent(axis) - limit), db = sign * (b.getComponent(axis) - limit);
    if (da >= 0) result.push(a);
    if ((da >= 0) !== (db >= 0)) result.push(a.clone().lerp(b, da / (da - db)));
  }
  return result;
}
const left = Math.max(...groundPoints.filter(p => p.x < 0).map(p => p.x));
const right = Math.min(...groundPoints.filter(p => p.x > 0).map(p => p.x));
const clearWidth = right - left;
function overheadHeight(x0, x1) {
  let height = Infinity;
  for (const t of worldTriangles) {
    if (Math.max(...t.map(p => p.y)) < 1) continue;
    const poly = clip(clip(t, 0, x0, 1), 0, x1, -1);
    if (poly.length) height = Math.min(height, ...poly.map(p => p.y));
  }
  return height;
}
const rawHeight = overheadHeight(left, right);
// Millimetre floor gives a conservative documented rectangular aperture.
const clearHeight = Math.floor(rawHeight * 1000) / 1000;
assert.ok(clearWidth > 10.6 && clearHeight > 3.9);
let intersections = 0;
for (const t of worldTriangles) {
  let poly = t;
  for (const [axis, limit, sign] of [[0, left + 1e-5, 1], [0, right - 1e-5, -1],
    [1, 1e-5, 1], [1, clearHeight - 1e-5, -1],
    [2, bounds.min.z - .01, 1], [2, bounds.max.z + .01, -1]]) poly = clip(poly, axis, limit, sign);
  if (poly.length >= 3) intersections++;
}
assert.equal(intersections, 0, 'clear rectangular through passage');
const report = {
  result: 'PASS', id: spec.slug, glb_bytes: bytes.length, triangles, vertices,
  meshes: json.meshes.length, primitives: 3, materials: 3, textures: 0, animations: 0,
  dimensions, bounds: {min: bounds.min.toArray(), max: bounds.max.toArray()},
  sha256: createHash('sha256').update(bytes).digest('hex'), min_triangle_area_m2: minArea,
  aperture: {clear_width_metres: clearWidth, clear_height_metres: clearHeight,
    raw_minimum_overhead_metres: rawHeight, centre_clear_height_metres: overheadHeight(-1e-6, 1e-6),
    through_depth_metres: dimensions[2], triangle_intersections: intersections,
    method: 'Ground-level jamb extremities; overhead triangle clipping across full width; open rectangular volume clipped against every exported triangle, 10 micrometre boundary tolerance.'},
  sign_band: {node: 'SIGN_Band', dimensions: new Box3().setFromObject(band, true).getSize(new Vector3()).toArray(),
    text_anchor: anchor.toArray()},
  validation: {errors: validation.issues.numErrors, warnings: validation.issues.numWarnings},
  budget: spec.budget, parts
};
fs.writeFileSync(dir + 'reports/assets.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

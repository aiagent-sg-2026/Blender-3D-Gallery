import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const dir = fileURLToPath(new URL('.', import.meta.url));
const evidence = JSON.parse(fs.readFileSync(dir + 'reports/sources.json'));
const original = fs.readFileSync(dir + 'exports/optimized.glb');
const edited = fs.readFileSync(path.join(os.tmpdir(), 'tv-wall-mounted-source-edit/edited.glb'));
assert.equal(createHash('sha256').update(edited).digest('hex'), evidence.edited_glb_sha256);
const result = await validator.validateBytes(new Uint8Array(edited));
assert.equal(result.issues.numErrors, 0); assert.equal(result.issues.numWarnings, 0);
const load = buffer => new GLTFLoader().parseAsync(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength), '');
const a = await load(original), b = await load(edited);
const positions = scene => [...scene.getObjectByName(evidence.edited_mesh).geometry.attributes.position.array];
const before = positions(a.scene), after = positions(b.scene);
assert.notDeepEqual(before, after);
// Exporter vertex deduplication can differ after reopening a native source.
// Compare the actual coordinate sets in both directions, independent of indexing.
const triples = array => Array.from({ length: array.length / 3 }, (_, i) => array.slice(i * 3, i * 3 + 3));
const expected = triples(before).map(([x, y, z]) => [x * .92, y, z]);
const actual = triples(after);
const matches = (one, other) => one.every(v => other.some(w => v.every((n, i) => Math.abs(n - w[i]) < 1e-6)));
assert.ok(matches(expected, actual) && matches(actual, expected), 'saved mesh edit matches scaled vertex coordinates');
assert.equal(a.scene.getObjectByName(evidence.edited_mesh).geometry.index.count,
             b.scene.getObjectByName(evidence.edited_mesh).geometry.index.count);
assert.ok(Math.abs(b.scene.getObjectByName(evidence.edited_mesh).material.roughness - .77) < 1e-5);
evidence.saved_edit_reexport = 'PASS: changed mesh positions and material survive save/reopen/export';
fs.writeFileSync(dir + 'reports/sources.json', JSON.stringify(evidence, null, 2) + '\n');
console.log(evidence.saved_edit_reexport);

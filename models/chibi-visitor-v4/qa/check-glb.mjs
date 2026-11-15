// Structural QA for the exported GLB (gates G1, G2, G5, G7). Usage, from the repository root:
//   node models/chibi-visitor-v4/qa/check-glb.mjs <glb> <out.json>
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';

const require = createRequire(process.cwd() + '/');
const validator = require('gltf-validator');
const [file, outFile] = process.argv.slice(2);
const buf = readFileSync(file);
const report = await validator.validateBytes(new Uint8Array(buf));
const jsonLen = buf.readUInt32LE(12);
const g = JSON.parse(buf.slice(20, 20 + jsonLen).toString());
const acc = g.accessors;
const checks = {};
const set = (id, status, detail) => { checks[id] = { status, detail }; };

set('QA-21 GLB header', buf.toString('ascii', 0, 4) === 'glTF' && buf.readUInt32LE(4) === 2 && buf.readUInt32LE(8) === buf.length ? 'PASS' : 'FAIL',
  `magic glTF, version ${buf.readUInt32LE(4)}, declared length ${buf.readUInt32LE(8)} vs file ${buf.length}`);
set('QA-22 Khronos validator', report.issues.numErrors === 0 && report.issues.numWarnings === 0 ? 'PASS' : 'FAIL',
  `${report.issues.numErrors} errors, ${report.issues.numWarnings} warnings, ${report.issues.numInfos} infos, ${report.issues.numHints} hints`);

let mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9], finite = true, noNormals = [], noUv = [];
for (const m of g.meshes) for (const p of m.primitives) {
  const a = acc[p.attributes.POSITION];
  for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], a.min[k]); mx[k] = Math.max(mx[k], a.max[k]); finite &&= Number.isFinite(a.min[k]) && Number.isFinite(a.max[k]); }
  if (!('NORMAL' in p.attributes)) noNormals.push(m.name);
  if (!('TEXCOORD_0' in p.attributes) && p.material !== undefined && g.materials[p.material].pbrMetallicRoughness?.baseColorTexture) noUv.push(m.name);
}
const height = mx[1] - mn[1];
set('QA-06 finite transforms/bounds', finite && g.nodes.every(n => !n.matrix || n.matrix.every(Number.isFinite)) ? 'PASS' : 'FAIL', `bounds min ${mn.map(v => +v.toFixed(4))} max ${mx.map(v => +v.toFixed(4))}`);
set('QA-07 normals', noNormals.length === 0 ? 'PASS' : 'FAIL', noNormals.length ? `missing on ${noNormals}` : 'every primitive has NORMAL');
set('QA-08 scale/bounds/origin', Math.abs(height - 1.0) < 0.02 && Math.abs(mn[1]) < 1e-3 ? 'PASS' : 'FAIL', `height ${height.toFixed(4)} m, feet at y=${mn[1].toFixed(4)}, +Y up`);
set('QA-09 UV mapping', noUv.length === 0 ? 'PASS' : 'FAIL', noUv.length ? `textured material without UV on ${noUv}` : 'textured primitives have TEXCOORD_0');
const images = g.images ?? [];
set('QA-10 missing textures', images.every(i => i.bufferView !== undefined) ? 'PASS' : 'FAIL', `${images.length} image(s), all embedded in the GLB`);
set('QA-11 PBR/colour space', g.materials.every(m => m.pbrMetallicRoughness) ? 'PASS' : 'FAIL', `${g.materials.length} metallic-roughness materials; base-colour image is sRGB by glTF definition`);
set('QA-15 clip inventory', (g.animations ?? []).length === 0 ? 'N_A' : 'PASS', 'static asset: documented no armature and no animation');
set('QA-13/14 rig and weights', (g.skins ?? []).length === 0 ? 'N_A' : 'FAIL', 'static asset, no skin (documented in metadata.json)');
const tris = report.info.totalTriangleCount, draw = report.info.drawCallCount;
set('QA-29 bytes/triangles', buf.length <= 4e6 && tris <= 150000 ? 'PASS' : 'FAIL', `${buf.length} bytes (<=4,000,000), ${tris} triangles (<=150,000); budgets are this project's own, not a device guarantee`);
set('QA-30 textures/draw calls', images.length <= 2 && draw <= 30 ? 'PASS' : 'FAIL', `${images.length} texture(s), ${draw} draw calls (<=30)`);

const out = {
  file, bytes: buf.length, sha256: createHash('sha256').update(buf).digest('hex'),
  generator: report.info.generator, validator: validator.version?.() ?? 'gltf-validator',
  triangles: tris, vertices: report.info.totalVertexCount, drawCalls: draw, materials: report.info.materialCount,
  nodes: g.nodes.map(n => n.name), checks, validatorMessages: report.issues.messages,
};
writeFileSync(outFile, JSON.stringify(out, null, 2));
for (const [k, v] of Object.entries(checks)) console.log(v.status.padEnd(5), k, '-', v.detail);
console.log('sha256', out.sha256);

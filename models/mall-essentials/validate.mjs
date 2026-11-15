// Validate real exports and record reproducible measurements, not target dimensions.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';

const root = path.dirname(fileURLToPath(import.meta.url));
const reports = [];
for (const id of ['mall-directory-kiosk', 'mall-advertising-lightbox', 'mall-trash-bin', 'mall-display-shelf']) {
  const bytes = fs.readFileSync(path.join(root, 'exports', id + '.glb'));
  const validation = await validator.validateBytes(new Uint8Array(bytes), { uri: id + '.glb' });
  if (validation.issues.numErrors || validation.issues.numWarnings) throw Error(JSON.stringify(validation.issues));
  const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
  if (json.images?.length || json.buffers.some(buffer => buffer.uri)) throw Error('Expected self-contained, texture-free export');
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const bounds = new Box3().setFromObject(gltf.scene);
  let triangles = 0, vertices = 0, primitives = 0, zeroAreaTriangles = 0;
  gltf.scene.traverse(object => {
    if (!object.isMesh) return;
    primitives++;
    const geometry = object.geometry;
    vertices += geometry.attributes.position.count;
    triangles += (geometry.index?.count ?? geometry.attributes.position.count) / 3;
    const position = geometry.attributes.position;
    for (let i = 0; i < (geometry.index?.count ?? position.count); i += 3) {
      const p = [0, 1, 2].map(offset => new Vector3().fromBufferAttribute(position,
        geometry.index ? geometry.index.getX(i + offset) : i + offset).applyMatrix4(object.matrixWorld));
      if (p[1].clone().sub(p[0]).cross(p[2].clone().sub(p[0])).lengthSq() === 0) zeroAreaTriangles++;
    }
  });
  const metadata = JSON.parse(fs.readFileSync(path.join(root, 'metadata', id + '.json')));
  if (metadata.topology_repair && zeroAreaTriangles) throw Error(id + ': degenerate geometry regressed');
  if (Math.abs(bounds.min.y) > .001 || triangles > 20000 || bytes.length > 700000 || primitives > 8) throw Error('Furniture budget/origin violation');
  reports.push({ id, glb_bytes: bytes.length, triangles, vertices, primitives, zero_area_triangles: zeroAreaTriangles,
    materials: json.materials.length, animations: (json.animations ?? []).length,
    dimensions: bounds.getSize(new Vector3()).toArray(), bounds: { min: bounds.min.toArray(), max: bounds.max.toArray() },
    sha256: createHash('sha256').update(bytes).digest('hex'),
    validation: { errors: validation.issues.numErrors, warnings: validation.issues.numWarnings, validator: validation.validatorVersion }
  });
}
fs.mkdirSync(path.join(root, 'reports'), { recursive: true });
fs.writeFileSync(path.join(root, 'reports', 'assets.json'), JSON.stringify(reports, null, 2) + '\n');
console.log(JSON.stringify(reports, null, 2));

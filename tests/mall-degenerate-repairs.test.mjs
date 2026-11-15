import '../scripts/node-glb-structure.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { loadCatalog } from '../scripts/catalog.mjs';

// Add each asset only with its verified source/export repair.
const repairedIds = ['mall-trash-bin', 'mall-directory-kiosk', 'mall-advertising-lightbox', 'mall-waste-sorting-station', 'mall-service-desk', 'mall-display-shelf', 'mall-floor-direction-sign', 'mall-event-booth', 'gjh-areca-planter', 'gjh-m057-premium-wall-shelf-corner'];
const catalog = loadCatalog();
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
for (const id of repairedIds) {
  test(id + ': repaired delivered geometry contains no zero-area triangles', async () => {
    const asset = catalog.collections.flatMap(c => c.assets).find(a => a.id === id);
    assert.ok(asset);
    const bytes = fs.readFileSync(asset.file);
    const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
    gltf.scene.updateMatrixWorld(true);
    let zero = 0;
    gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      const { index, attributes: { position, normal } } = object.geometry;
      assert.ok(normal, 'Shading normals must be retained');
      for (let i = 0; i < position.count; i++) {
        assert.ok([position.getX(i), position.getY(i), position.getZ(i)].every(Number.isFinite));
        assert.ok(Math.abs(Math.hypot(normal.getX(i), normal.getY(i), normal.getZ(i)) - 1) < .01);
      }
      for (let i = 0; i < (index?.count ?? position.count); i += 3) {
        const p = [0, 1, 2].map(offset => new Vector3().fromBufferAttribute(position,
          index ? index.getX(i + offset) : i + offset).applyMatrix4(object.matrixWorld));
        if (p[1].clone().sub(p[0]).cross(p[2].clone().sub(p[0])).lengthSq() === 0) zero++;
      }
    });
    assert.equal(zero, 0, id + ': actual GLB must contain no zero-area triangles');
    const metadata = JSON.parse(fs.readFileSync(asset.metadata));
    const folder = asset.metadata.slice(0, asset.metadata.lastIndexOf('/metadata/'));
    assert.equal(metadata.metrics.sha256, hash(bytes));
    assert.equal(metadata.source_sha256, hash(fs.readFileSync(folder + '/' + metadata.paths.source)));
    assert.equal(metadata.metrics.zero_area_triangles, 0);
  });
}

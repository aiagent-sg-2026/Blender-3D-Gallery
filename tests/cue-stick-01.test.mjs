import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Matrix3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

async function inspect(file) {
  const bytes = fs.readFileSync(`${process.env.CUE_01_ASSET_DIR || 'models/eight-ball-billiards/exports'}/${file}`);
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  const root = gltf.scene.getObjectByName('ASSET_Cue_01');
  assert.ok(root, 'Cue 01 must remain an independently named asset');
  const rows = [];
  root.traverse(ob => {
    if (!ob.isMesh) return;
    const geometry = ob.geometry;
    // All four authored pieces share the cue's world X axis. The short tip
    // is wider than it is long, so its longest bounding-box axis is unsuitable.
    const axis = 0;
    const normalMatrix = new Matrix3().getNormalMatrix(ob.matrixWorld);
    const position = geometry.getAttribute('position'), normal = geometry.getAttribute('normal');
    const index = geometry.index;
    const row = { name: ob.name, caps: [], sides: [] };
    for (let i = 0; i < index.count; i += 3) {
      const ids = [0, 1, 2].map(k => index.getX(i + k));
      const points = ids.map(id => new Vector3().fromBufferAttribute(position, id).applyMatrix4(ob.matrixWorld));
      const face = points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0]));
      assert.ok(face.lengthSq() > 1e-18, 'No degenerate triangle');
      face.normalize();
      const group = Math.abs(face.getComponent(axis)) > 1 - 1e-5 ? row.caps : row.sides;
      for (const id of ids) {
        const n = new Vector3().fromBufferAttribute(normal, id);
        assert.ok(Math.abs(n.length() - 1) < 1e-5, 'Exported normals must be unit length');
        n.applyNormalMatrix(normalMatrix);
        group.push(n.dot(face));
      }
    }
    assert.ok(row.caps.length && row.sides.length);
    rows.push(row);
  });
  assert.equal(rows.length, 4, 'Preserve butt, shaft, ferrule and tip meshes');
  return rows;
}

for (const file of ['cue_01.glb', 'billiards-scene.glb']) {
  test(`${file}: Cue 01 end-cap normals follow their planar geometry`, async () => {
    for (const row of await inspect(file)) {
      assert.ok(Math.min(...row.caps) > .9999, `${row.name}: cap must shade as a plane, not a rounded bulge`);
    }
  });
  test(`${file}: Cue 01 smooth side normals exclude the flat caps`, async () => {
    for (const row of await inspect(file)) {
      // A smooth radial normal differs from a 16-sided facet normal by at
      // most pi/16 radians: cos(pi/16) = .980785. Allow float rounding.
      assert.ok(Math.min(...row.sides) > .98, `${row.name}: side normal is pulled toward an end cap`);
    }
  });
}

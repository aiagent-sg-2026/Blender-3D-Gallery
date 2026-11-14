import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Box3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

async function load(file) {
  const bytes = fs.readFileSync(file);
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  gltf.scene.updateMatrixWorld(true);
  return gltf.scene;
}

for (const file of ['table.glb', 'billiards-scene.glb']) {
  test(`${file}: all twelve sights are seated in the wooden rails`, async () => {
    const scene = await load(`${process.env.POOL_TABLE_ASSET_DIR || 'models/eight-ball-billiards/exports'}/${file}`);
    const table = scene.getObjectByName('ASSET_Table');
    assert.ok(table);
    const sights = [], rails = [];
    table.traverse(ob => {
      if (ob.name.startsWith('Rail_sight')) sights.push(ob);
      if (ob.name.startsWith('Long_rail')) rails.push(ob);
    });
    // GLTFLoader sanitizes spaces and periods in names.
    assert.equal(sights.length, 12);
    assert.equal(rails.length, 4);
    const railBoxes = rails.map(ob => new Box3().setFromObject(ob));
    for (const sight of sights) {
      const box = new Box3().setFromObject(sight);
      const rail = railBoxes.find(r => box.min.x >= r.min.x && box.max.x <= r.max.x && box.min.z >= r.min.z && box.max.z <= r.max.z);
      assert.ok(rail, `${sight.name}: a supporting rail must cover the entire disc`);
      assert.ok(box.min.y < rail.max.y, `${sight.name}: base must be seated below the rail surface`);
      const proud = box.max.y - rail.max.y;
      assert.ok(proud >= .00005 && proud <= .00015, `${sight.name}: top should sit 0.1 mm proud, got ${proud} m`);
    }
  });
  test(`${file}: slate is supported by the cabinet without moving the playing surface`, async () => {
    const scene = await load(`${process.env.POOL_TABLE_ASSET_DIR || 'models/eight-ball-billiards/exports'}/${file}`);
    const table = scene.getObjectByName('ASSET_Table');
    let slate, cabinet;
    table.traverse(ob => {
      if (ob.name.includes('slate_and_green_cloth')) slate = ob;
      if (ob.name.includes('solid_walnut_cabinet')) cabinet = ob;
    });
    assert.ok(slate && cabinet);
    const bed = new Box3().setFromObject(slate), support = new Box3().setFromObject(cabinet);
    assert.ok(bed.min.y <= support.max.y, 'The slate underside must contact the cabinet, not float above it');
    assert.ok(support.max.y - bed.min.y <= .00015, 'Only a small seating overlap is allowed');
    assert.ok(Math.abs(bed.max.y - .7785) < 1e-6, 'Preserve the authored and gameplay playing height');
    assert.ok(Math.abs(bed.max.x - bed.min.x - 2.30) < 1e-6);
    assert.ok(Math.abs(bed.max.z - bed.min.z - 1.18) < 1e-6);
  });
}

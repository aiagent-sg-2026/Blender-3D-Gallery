import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import validator from 'gltf-validator';
import { AnimationMixer, Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const file = 'models/mall-basket-cart/exports/interactive-shopping-cart.glb';

test('interactive shopping cart GLB meets its asset and rig contract', async () => {
  const bytes = fs.readFileSync(file);
  const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString('utf8'));
  const report = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(report.issues.numErrors, 0);
  assert.equal(report.issues.numWarnings, 0);
  assert.ok(bytes.length <= 2_000_000);
  assert.ok(json.buffers.every(buffer => !buffer.uri));
  const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
  assert.ok(gltf.scene.getObjectByName('ASSET_InteractiveShoppingCart'));
  for (const name of ['FrontLeft', 'FrontRight', 'RearLeft', 'RearRight']) {
    const wheel = gltf.scene.getObjectByName(`Wheel_${name}`);
    const clip = gltf.animations.find(clip => clip.name === `Roll_${name}`);
    assert.ok(wheel && clip);
    const original = wheel.quaternion.clone();
    const mixer = new AnimationMixer(gltf.scene);
    mixer.clipAction(clip).play(); mixer.setTime(1);
    assert.ok(wheel.quaternion.angleTo(original) > .5, `${name} wheel actually turns`);
    mixer.stopAllAction();
  }
  for (const name of ['FrontLeft', 'FrontRight']) {
    const swivel = gltf.scene.getObjectByName(`Steer_${name}`);
    const clip = gltf.animations.find(clip => clip.name === `Steer_${name}`);
    assert.ok(swivel && clip);
    const original = swivel.quaternion.clone();
    const mixer = new AnimationMixer(gltf.scene);
    mixer.clipAction(clip).play(); mixer.setTime(1);
    assert.ok(swivel.quaternion.angleTo(original) > .3, `${name} caster actually steers`);
    mixer.stopAllAction();
  }
  assert.ok(gltf.animations.find(clip => clip.name === 'PlaceItem')?.tracks.some(track => new Set(track.values).size > 2));
  let triangles = 0;
  gltf.scene.traverse(node => { if (node.isMesh) triangles += (node.geometry.index?.count ?? node.geometry.attributes.position.count) / 3; });
  assert.ok(triangles <= 15_000, `triangles: ${triangles}`);
  const bounds = new Box3().setFromObject(gltf.scene, true);
  const [width, height, length] = bounds.getSize(new Vector3()).toArray();
  assert.ok(Math.abs(width - .60) < .03, `width ${width}`);
  assert.ok(Math.abs(height - 1.00) < .03, `height ${height}`);
  assert.ok(Math.abs(length - 1.05) < .03, `length ${length}`);
  assert.ok(Math.abs(bounds.min.y) < .01, 'wheel contact at floor');
});

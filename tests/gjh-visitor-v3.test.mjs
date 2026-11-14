import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { AnimationMixer, Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';
import { createVisitorCustomization } from '../models/gjh-visitor-v3/customization.js';

const path = new URL('../models/gjh-visitor-v3/exports/gjh-visitor-v3.glb', import.meta.url);
async function load() {
  const bytes = await fs.readFile(path);
  return new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
}

test('v3 exports a bounded, valid skinned visitor and the intended clips', async () => {
  const bytes = await fs.readFile(path);
  const report = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(report.issues.numErrors, 0);
  assert.ok(bytes.length < 2 * 1024 * 1024);
  const gltf = await load();
  const meshes = [];
  gltf.scene.traverse(node => { if (node.isMesh) meshes.push(node); });
  assert.ok(meshes.length <= 28, `draw calls: ${meshes.length}`);
  assert.ok(meshes.every(mesh => mesh.isSkinnedMesh));
  const bounds = new Box3().setFromObject(gltf.scene);
  assert.ok(Math.abs(bounds.min.y) < .002);
  assert.ok(Math.abs(bounds.max.y - 1.78) < .01);
  for (const name of ['Body', 'Spine', 'Neck', 'Head', 'LeftShoulder', 'RightShoulder', 'LeftElbow', 'RightElbow', 'LeftHand', 'RightHand', 'LeftHip', 'RightHip', 'LeftKnee', 'RightKnee', 'LeftFoot', 'RightFoot', 'LeftThumb', 'RightThumb', 'LeftFinger0', 'RightFinger0'])
    assert.ok(gltf.scene.getObjectByName(name)?.isBone, `missing bone ${name}`);
  assert.deepEqual(gltf.animations.map(clip => clip.name).sort(), ['carry', 'idle', 'pick_up', 'point', 'push_cart', 'run', 'sit_down', 'stand_up', 'turn_left', 'turn_right', 'walk', 'wave']);
});

test('appearance changes are independent, reversible and reject unsupported values', async () => {
  const gltf = await load();
  const custom = createVisitorCustomization(gltf.scene);
  const parts = prefix => { const out = []; gltf.scene.traverse(n => { if (n.isMesh && n.name.startsWith(prefix)) out.push(n); }); return out; };
  const hairAlt = parts('V3_hair_alt_'), jacket = parts('V3_jacket_'), pack = parts('V3_backpack_');
  assert.ok(hairAlt.length && jacket.length && pack.length);
  assert.ok(hairAlt.every(p => !p.visible));
  custom.apply({hair: 'short', outfit: 'tee', skin: 'dark', hairColor: 'brown', backpack: false, badge: false, watch: false});
  assert.ok(hairAlt.every(p => p.visible));
  assert.ok(jacket.every(p => !p.visible));
  assert.ok(pack.every(p => !p.visible));
  assert.throws(() => custom.apply({skin: 'unknown'}), TypeError);
  assert.equal(custom.state.skin, 'dark');
  custom.apply({hair: 'wavy', outfit: 'hoodie', skin: 'light', backpack: true, badge: true, watch: true});
  assert.ok(jacket.every(p => p.visible));
  assert.ok(hairAlt.every(p => !p.visible));
  custom.dispose();
});

test('actual exported locomotion clips keep at least one shoe near the floor', async () => {
  const gltf = await load();
  const shoes = [];
  gltf.scene.traverse(node => { if (node.isSkinnedMesh && node.name.startsWith('V3_shoes_')) shoes.push(node); });
  assert.ok(shoes.length);
  for (const name of ['idle', 'walk', 'run', 'push_cart', 'sit_down', 'stand_up', 'pick_up', 'turn_left', 'turn_right']) {
    const clip = gltf.animations.find(item => item.name === name);
    const mixer = new AnimationMixer(gltf.scene);
    mixer.clipAction(clip).play();
    let worst = 0;
    for (let frame = 0; frame <= 40; frame++) {
      mixer.setTime(clip.duration * frame / 40);
      gltf.scene.updateMatrixWorld(true);
      let floor = Infinity;
      for (const mesh of shoes) {
        const positions = mesh.geometry.attributes.position;
        for (let i = 0; i < positions.count; i++) {
          const point = new Vector3().fromBufferAttribute(positions, i);
          mesh.applyBoneTransform(i, point);
          point.applyMatrix4(mesh.matrixWorld);
          floor = Math.min(floor, point.y);
        }
      }
      worst = Math.max(worst, Math.abs(floor));
    }
    assert.ok(worst < .012, `${name}: floor error ${worst}`);
    mixer.stopAllAction();
  }
});

test('every contract clip plays in Three.js without invalid transforms', async () => {
  const gltf = await load();
  for (const clip of gltf.animations) {
    const mixer = new AnimationMixer(gltf.scene);
    mixer.clipAction(clip).play();
    for (let i = 0; i <= 10; i++) {
      mixer.setTime(clip.duration * i / 10);
      gltf.scene.updateMatrixWorld(true);
    }
    gltf.scene.traverse(n => { if (n.isBone) assert.ok(n.matrixWorld.elements.every(Number.isFinite), `${clip.name}: ${n.name}`); });
    mixer.stopAllAction();
  }
});

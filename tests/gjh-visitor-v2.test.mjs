import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { AnimationMixer, Box3, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';
import { createVisitorCustomization } from '../models/gjh-mall-visitor-v2/customization.js';

const path = new URL('../models/gjh-mall-visitor-v2/exports/gjh-mall-visitor-v2.glb', import.meta.url);
async function load() {
  const bytes = await fs.readFile(path);
  return new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
}

test('v2 exports a bounded, valid skinned visitor and the intended clips', async () => {
  const bytes = await fs.readFile(path);
  const report = await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(report.issues.numErrors, 0);
  assert.equal(report.issues.numWarnings, 0);
  assert.ok(bytes.length < 2 * 1024 * 1024);
  const gltf = await load();
  const meshes = [];
  gltf.scene.traverse(node => { if (node.isMesh) meshes.push(node); });
  assert.ok(meshes.length <= 20, `draw calls: ${meshes.length}`);
  assert.ok(meshes.every(mesh => mesh.isSkinnedMesh));
  const bounds = new Box3().setFromObject(gltf.scene);
  assert.ok(Math.abs(bounds.min.y) < .002);
  assert.ok(Math.abs(bounds.max.y - 1.72) < .01);
  for (const name of ['Body', 'Spine', 'Neck', 'Head', 'LeftShoulder', 'RightShoulder', 'LeftElbow', 'RightElbow', 'LeftHand', 'RightHand', 'LeftHip', 'RightHip', 'LeftKnee', 'RightKnee', 'LeftFoot', 'RightFoot', 'LeftThumb', 'RightThumb', 'LeftFinger0', 'RightFinger0'])
    assert.ok(gltf.scene.getObjectByName(name)?.isBone, `missing bone ${name}`);
  assert.deepEqual(gltf.animations.map(clip => clip.name).sort(), ['elevator', 'idle', 'pickup', 'place', 'push', 'sit', 'sprint', 'stand', 'walk']);
});

test('appearance changes are independent, reversible and reject unsupported values', async () => {
  const gltf = await load();
  const custom = createVisitorCustomization(gltf.scene);
  const visible = name => gltf.scene.getObjectByName(name).visible;
  assert.equal(visible('V2_hair_alt_Swept_chestnut_hair'), false);
  assert.equal(visible('V2_outfit_alt_Hoodie_slate'), false);
  custom.apply({hair:'short', outfit:'hoodie', skin:'dark', hairColor:'black', glasses:false, backpack:false, watch:false});
  assert.equal(visible('V2_hair_alt_Swept_chestnut_hair'), true);
  assert.equal(visible('V2_hair_Swept_chestnut_hair'), false);
  assert.equal(visible('V2_outfit_alt_Hoodie_slate'), true);
  assert.equal(visible('V2_outfit_GJH_emerald_polo'), false);
  assert.equal(visible('V2_glasses_Glasses_and_eyes'), false);
  assert.equal(visible('V2_backpack_Backpack_charcoal'), false);
  assert.throws(() => custom.apply({skin:'unknown'}), TypeError);
  assert.equal(custom.state.skin, 'dark');
  custom.apply({hair:'swept', outfit:'polo', skin:'light', glasses:true, backpack:true, watch:true});
  assert.equal(visible('V2_hair_Swept_chestnut_hair'), true);
  assert.equal(visible('V2_outfit_alt_Hoodie_slate'), false);
  custom.dispose();
});

test('actual exported locomotion clips keep at least one shoe near the floor', async () => {
  const gltf = await load();
  const shoes = [];
  gltf.scene.traverse(node => { if (node.isSkinnedMesh && node.name.startsWith('V2_shoes_')) shoes.push(node); });
  assert.ok(shoes.length);
  for (const name of ['idle', 'walk', 'sprint', 'push']) {
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

test('LOD preserves customization slots, skin and clips with fewer triangles', async () => {
  const bytes=await fs.readFile(new URL('../models/gjh-mall-visitor-v2/exports/gjh-mall-visitor-v2-lod1.glb', import.meta.url));
  const report=await validator.validateBytes(new Uint8Array(bytes));
  assert.equal(report.issues.numErrors,0);assert.equal(report.issues.numWarnings,0);
  const low=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  createVisitorCustomization(low.scene).apply({outfit:'hoodie',hair:'short',skin:'dark'});
  let triangles=0;low.scene.traverse(n=>{if(n.isMesh){assert.ok(n.isSkinnedMesh);triangles+=n.geometry.index.count/3;}});
  assert.ok(triangles<7000 && triangles>4000);
  const high=await load();assert.deepEqual(low.animations.map(a=>a.name).sort(),high.animations.map(a=>a.name).sort());
});

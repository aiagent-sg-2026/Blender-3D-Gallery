import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBall,assertSphere,assertClothContact,assertNumberMarks } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.BALL_02_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
for(const file of ['ball_02.glb','billiards-scene.glb']){
  test(`${file}: Ball02 preserves its full-size blue resin body`,async()=>{
    const {body,meshes}=await loadBall(file,2,directory);assert.equal(meshes.length,5);assertSphere(body,.23);
    const color=body.material.color;for(const [key,value] of [['r',.015],['g',.09],['b',.55]])assert.ok(Math.abs(color[key]-value)<1e-6);
  });
  test(`${file}: Ball02 has outward, close-fitting number marks on both sides`,async()=>{
    const {meshes}=await loadBall(file,2,directory);assertNumberMarks(meshes,2);
  });
}
test('assembled Ball02 is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',2,directory);assertClothContact(gltf,body);
});

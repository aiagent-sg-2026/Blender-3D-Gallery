import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBall,assertSphere,assertClothContact,assertNumberMarks } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.BALL_06_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
for(const file of ['ball_06.glb','billiards-scene.glb']){
  test(`${file}: Ball06 preserves its full-size green resin body`,async()=>{
    const {body,meshes}=await loadBall(file,6,directory);assert.equal(meshes.length,5);assertSphere(body,.23);
    const color=body.material.color;for(const [key,value] of [['r',.012],['g',.3],['b',.105]])assert.ok(Math.abs(color[key]-value)<1e-6);
  });
  test(`${file}: Ball06 has outward, close-fitting number marks on both sides`,async()=>{
    const {meshes}=await loadBall(file,6,directory);assertNumberMarks(meshes,6);
  });
}
test('assembled Ball06 is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',6,directory);assertClothContact(gltf,body);
});

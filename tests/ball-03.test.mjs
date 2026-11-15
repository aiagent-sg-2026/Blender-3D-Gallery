import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBall,assertSphere,assertClothContact,assertNumberMarks } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.BALL_03_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
for(const file of ['ball_03.glb','billiards-scene.glb']){
  test(`${file}: Ball03 preserves its full-size red resin body`,async()=>{
    const {body,meshes}=await loadBall(file,3,directory);assert.equal(meshes.length,5);assertSphere(body,.23);
    const color=body.material.color;for(const [key,value] of [['r',.61],['g',.018],['b',.025]])assert.ok(Math.abs(color[key]-value)<1e-6);
  });
  test(`${file}: Ball03 has outward, close-fitting number marks on both sides`,async()=>{
    const {meshes}=await loadBall(file,3,directory);assertNumberMarks(meshes,3);
  });
}
test('assembled Ball03 is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',3,directory);assertClothContact(gltf,body);
});

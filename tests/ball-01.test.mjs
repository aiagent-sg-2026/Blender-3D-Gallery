import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBall,assertSphere,assertClothContact,assertNumberMarks } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.BALL_01_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
for(const file of ['ball_01.glb','billiards-scene.glb']){
  test(`${file}: Ball01 preserves its full-size yellow resin body`,async()=>{
    const {body,meshes}=await loadBall(file,1,directory);assert.equal(meshes.length,5);assertSphere(body,.23);
    const color=body.material.color;for(const [key,value] of [['r',.92],['g',.56],['b',.012]])assert.ok(Math.abs(color[key]-value)<1e-6);
  });
  test(`${file}: Ball01 has outward, close-fitting number marks on both sides`,async()=>{
    const {meshes}=await loadBall(file,1,directory);assertNumberMarks(meshes,1);
  });
}
test('assembled Ball01 is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',1,directory);assertClothContact(gltf,body);
});

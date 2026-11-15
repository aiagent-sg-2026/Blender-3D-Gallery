import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBall,assertSphere,assertClothContact } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.CUE_BALL_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
for(const file of ['ball_00.glb','billiards-scene.glb'])test(`${file}: cue ball retains57.15mm spherical geometry and smooth outward normals`,async()=>{
  const {body,meshes}=await loadBall(file,0,directory);assert.equal(meshes.length,1,'Cue ball has one unnumbered resin body');assertSphere(body,.24);
});
test('assembled cue ball is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',0,directory);assertClothContact(gltf,body);
});

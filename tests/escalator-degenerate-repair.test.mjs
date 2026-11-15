import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{execFileSync}from'node:child_process';
import{AnimationMixer,LoopOnce}from'three';import'../scripts/node-glb-structure.mjs';
const root='models/escalator/';
test('escalator retains fixed surfaces and all candidate motion contracts after reviewed cleanup',()=>{
 execFileSync(process.execPath,[root+'validate.mjs'],{stdio:'pipe'});
 const r=JSON.parse(fs.readFileSync(root+'reports/circulation-final/assets.json'));
 assert.equal(r.triangles,65394);assert.equal(r.animations,60);assert.equal(r.candidateEvidence.reviewedStaticTriangleRemovals,14);
});
test('all sixty delivered rigid clips play without moving any repaired static mesh',async()=>{
 const {GLTFLoader}=await import('three/addons/loaders/GLTFLoader.js');const bytes=fs.readFileSync(root+'exports/optimized.glb');
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 assert.equal(gltf.animations.length,60);const proof=JSON.parse(fs.readFileSync(root+'reports/topology-repair.json'));
 gltf.scene.updateMatrixWorld(true);const fixed=Object.fromEntries(proof.static_nodes.map(n=>[n,gltf.scene.getObjectByName(n).matrixWorld.toArray()]));let samples=0;
 for(const clip of gltf.animations){const targets=[...new Set(clip.tracks.map(t=>t.name.slice(0,t.name.lastIndexOf('.'))))].map(n=>{const o=gltf.scene.getObjectByName(n);assert.ok(o,'Actual animation binding '+n);return o;});let baseline=null,moved=false;const mixer=new AnimationMixer(gltf.scene),action=mixer.clipAction(clip);action.setLoop(LoopOnce,1);action.clampWhenFinished=true;action.play();
  for(const fraction of [0,.19,.5,.9,1]){mixer.setTime(clip.duration*fraction);gltf.scene.updateMatrixWorld(true);gltf.scene.traverse(o=>{
   assert.ok([...o.position,...o.quaternion,...o.scale].every(Number.isFinite));assert.ok(Math.abs(o.quaternion.length()-1)<1e-5);assert.ok(o.scale.toArray().every(s=>Math.abs(s-1)<1e-5));
  });for(const[n,m]of Object.entries(fixed))assert.deepEqual(gltf.scene.getObjectByName(n).matrixWorld.toArray(),m);const pose=JSON.stringify(targets.map(o=>o.matrixWorld.toArray()));if(fraction===0)baseline=pose;else if(fraction<1&&pose!==baseline)moved=true;samples++;}
  assert.ok(moved,clip.name+' must visibly move its bound nodes');action.stop();mixer.uncacheRoot(gltf.scene);
 }
 fs.writeFileSync(root+'reports/topology-runtime.json',JSON.stringify({status:'PASS',clips:60,tracks:120,samples,static_nodes:Object.keys(fixed),scope:'Actual Three.js AnimationMixer, finite/unit transforms and repaired static matrices; Gallery remains orbit-only'},null,2)+'\n');
});
test('saved escalator source edit preserves other meshes, clips and canonical files',()=>{
 execFileSync(process.execPath,[root+'verify_source_edit.mjs'],{stdio:'pipe'});
 const r=JSON.parse(fs.readFileSync(root+'reports/circulation-final/source-edit-export-proof.json'));
 assert.equal(r.unchanged_sibling_meshes,137);assert.equal(r.exact_60_clip_payload_preserved,true);
});

import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import validator from 'gltf-validator';
import {report} from '../../verification/foundation-v1/qa-utils.mjs';

const here=path.dirname(new URL(import.meta.url).pathname);
const executable=process.env.BLENDER_BIN||'/Applications/Blender.app/Contents/MacOS/Blender';
const temporary=await fs.mkdtemp(path.join(os.tmpdir(),'blender-knowledge-'));
const hash=buffer=>createHash('sha256').update(buffer).digest('hex');
let result,observed;const exports=[];
try{
  const run=spawnSync(executable,['--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','23','--python',here+'/knowledge-probe.py','--',temporary],{encoding:'utf8',timeout:90000,maxBuffer:2e6});
  assert.equal(run.status,0,run.stderr+run.stdout);
  observed=JSON.parse(await fs.readFile(temporary+'/observations.json'));
  assert.equal(observed.background,true);assert.equal(observed.view3d_poll,false);assert.equal(observed.primitive_poll,true);
  assert.equal(observed.object_copy_shares_mesh,true);assert.equal(observed.linked_edit_changes_original,true);assert.equal(observed.data_copy_isolates_edit,true);
  assert.equal(observed.source_vertices,8);assert.equal(observed.source_faces,6);assert.equal(observed.source_manifold,true);assert.ok(Math.abs(observed.source_volume_m3-6)<1e-6);
  for(const name of ['cube-uv.glb','cube-no-uv.glb','cube-unit-scale-001.glb','cube-animated.glb']){
    const bytes=await fs.readFile(path.join(temporary,name));
    const validation=await validator.validateBytes(new Uint8Array(bytes),{uri:name});assert.equal(validation.issues.numErrors,0);
    const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
    const bounds=new T.Box3().setFromObject(gltf.scene),meshes=[];
    gltf.scene.traverse(o=>{if(o.isMesh)meshes.push(o);});assert.equal(meshes.length,1);
    const mesh=meshes[0],triangles=(mesh.geometry.index?.count??mesh.geometry.attributes.position.count)/3;
    assert.equal(triangles,12);
    assert.ok(Math.abs(mesh.material.roughness-.42)<1e-6);assert.ok(Math.abs(mesh.material.metalness-.15)<1e-6);
    const entry={file:name,sha256:hash(bytes),bytes:bytes.length,vertices:mesh.geometry.attributes.position.count,triangles,
      center:bounds.getCenter(new T.Vector3()).toArray(),size:bounds.getSize(new T.Vector3()).toArray(),
      roughness:mesh.material.roughness,metalness:mesh.material.metalness,
      animations:gltf.animations.map(c=>({name:c.name,duration:c.duration,tracks:c.tracks.map(t=>t.name)})),issues:validation.issues};
    exports.push(entry);
    if(name==='cube-animated.glb'){
      assert.equal(gltf.animations.length,1);assert.ok(gltf.animations[0].tracks.some(t=>t.name.endsWith('.position')));
      const positionTrack=gltf.animations[0].tracks.find(t=>t.name.endsWith('.position'));
      entry.sampleStart=positionTrack.times[0];entry.sampleEnd=positionTrack.times[positionTrack.times.length-1];
      entry.sampleMidpoint=(entry.sampleStart+entry.sampleEnd)/2;
      const mixer=new T.AnimationMixer(gltf.scene);mixer.clipAction(gltf.animations[0]).setLoop(T.LoopOnce,1).play();
      mixer.setTime(entry.sampleMidpoint);gltf.scene.updateMatrixWorld(true);
      entry.midpoint=new T.Box3().setFromObject(gltf.scene).getCenter(new T.Vector3()).toArray();assert.ok(Math.abs(entry.midpoint[0]-4.5)<.02,JSON.stringify(entry));
    }
  }
  for(const record of exports.filter(r=>r.file!=='cube-unit-scale-001.glb')){
    for(const [a,b]of record.center.map((v,i)=>[v,[4,6,5][i]]))assert.ok(Math.abs(a-b)<1e-5);
    for(const [a,b]of record.size.map((v,i)=>[v,[1,3,2][i]]))assert.ok(Math.abs(a-b)<1e-5);
  }
  assert.ok(exports[0].vertices>exports[1].vertices,'UV seams must be isolated from smooth-normal splitting in this fixture');
  const scaleRatio=exports[2].size[0]/exports[1].size[0];assert.ok(Math.abs(scaleRatio-1)<1e-5,'Review the version-specific unit observation if exporter behavior changes');
  const failed=spawnSync(executable,['--background','--factory-startup','--disable-autoexec','--threads','2','--python-exit-code','23','--python-expr',"raise RuntimeError('KnowledgeProbeExpectedFailure')"],{encoding:'utf8',timeout:30000,maxBuffer:1e6});
  assert.equal(failed.status,23);
  result={status:'PASS',checkedAt:new Date().toISOString(),observations:observed,exports,
    sceneUnitScale001GeometryRatio:scaleRatio,expectedExceptionExitCode:failed.status,
    scriptSha256:hash(await fs.readFile(here+'/knowledge-probe.py')),
    scope:'Generic isolated Blender experiments and Node GLB load; no installed extension, production model, active scene, browser visual or phone compatibility claim.'};
  console.log('PASS: context, shared mesh ownership, axes, UV split, material factors, action playback, units and CLI failure propagation');
}catch(e){result={status:'FAIL',error:e.message,observations:observed,exports};throw e;}
finally{await report(here+'/probe-results.json',result);await fs.rm(temporary,{recursive:true,force:true});}

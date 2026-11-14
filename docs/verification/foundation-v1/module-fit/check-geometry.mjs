import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {Box3,Vector3} from 'three';
import {OBB} from 'three/addons/math/OBB.js';
import validator from 'gltf-validator';
import {readGlb} from '../../../../models/mall-shopfront-door/glb.mjs';
import {report} from '../qa-utils.mjs';

const here=path.dirname(new URL(import.meta.url).pathname),root=path.resolve(here,'../../../..');
const hash=b=>createHash('sha256').update(b).digest('hex');
const layout=JSON.parse(await fs.readFile(here+'/layout.json'));
const input=here+'/foundation-fitted.glb',gltf=await readGlb(input),scene=gltf.scene;
const bounds=o=>new Box3().setFromObject(o);
const near=(a,b)=>assert.ok(Math.abs(a-b)<.00001,`${a} != ${b}`);
const integrity=[];
for(const record of Object.values(layout.sources)){
  const sha=hash(await fs.readFile(path.join(root,record.path)));
  assert.equal(sha,record.sha256,record.path);integrity.push({path:record.path,sha256:sha});
}
assert.equal(hash(await fs.readFile(path.join(root,layout.adaptation_source.path))),layout.adaptation_source.sha256);
const prior=JSON.parse(await fs.readFile(here+'/../reports/delivery.json'));
for(const f of [...prior.files,...prior.checks.map(r=>({path:r.file,sha256:r.sha256}))])
  assert.equal(hash(await fs.readFile(path.join(here,'..',f.path))),f.sha256,f.path);
const validation=[];
for(const file of ['foundation-fitted.glb','exports/fascia-run-348.glb']){
  const bytes=await fs.readFile(path.join(here,file)),v=await validator.validateBytes(new Uint8Array(bytes),{uri:file});
  assert.equal(v.issues.numErrors,0,file);assert.equal(v.issues.numWarnings,0,file);
  validation.push({file,sha256:hash(bytes),bytes:bytes.length,issues:v.issues});
}
for(const record of layout.objects){
  const object=scene.getObjectByName(record.name);assert.ok(object,record.name);
  const b=bounds(object),lo=[record.min[0],record.min[2],-record.max[1]],hi=[record.max[0],record.max[2],-record.min[1]];
  for(let i=0;i<3;i++){near(b.min.toArray()[i],lo[i]);near(b.max.toArray()[i],hi[i]);}
}
const meshes=root=>{const objects=[];root.traverse(o=>{if(o.isMesh)objects.push(o);});return objects;};
const componentBox=o=>{
  o.geometry.computeBoundingBox();const b=o.geometry.boundingBox;
  return new OBB(b.getCenter(new Vector3()),b.getSize(new Vector3()).multiplyScalar(.5).subScalar(.00001)).applyMatrix4(o.matrixWorld);
};
const joints=[];
for(const label of ['A','B'])for(const run of ['Left','Right']){
  const bays=[0,1,2].map(i=>scene.getObjectByName(`Partition_${label}_${run}_${i}`));
  const posts=bays.flatMap(b=>meshes(b).filter(o=>/^POST_(Left|Right)/.test(o.name)));
  assert.equal(posts.length,4,'Three bays must have four posts');
  for(let i=1;i<3;i++){
    const find=(o,prefix)=>{let found;o.traverse(c=>{if(c.name.startsWith(prefix))found=c;});return found;};
    const right=find(bays[i-1],'CONNECTOR_Right'),left=find(bays[i],'CONNECTOR_Left');
    assert.ok(right&&left);const separation=right.getWorldPosition(new Vector3()).distanceTo(left.getWorldPosition(new Vector3()));near(separation,0);
    let overlaps=0;
    for(const a of meshes(bays[i-1]))for(const b of meshes(bays[i]))if(bounds(a).intersectsBox(bounds(b))&&componentBox(a).intersectsOBB(componentBox(b)))overlaps++;
    assert.equal(overlaps,0);joints.push({label,run,joint:i,separation,componentOverlaps:overlaps});
  }
  const fascia=bounds(scene.getObjectByName(`Fascia_Run_${label}_${run}`)),runBounds=new Box3();for(const b of bays)runBounds.union(bounds(b));
  near(fascia.min.z,runBounds.min.z);near(fascia.max.z,runBounds.max.z);near(fascia.min.y,2.4);near(fascia.max.y,3);
  const doorFascia=bounds(scene.getObjectByName(`Fascia_Door_${label}`));
  near(Math.min(Math.abs(fascia.min.z-doorFascia.max.z),Math.abs(fascia.max.z-doorFascia.min.z)),0);
  const sign=meshes(scene.getObjectByName(`Fascia_Run_${label}_${run}`)).filter(o=>o.name.startsWith('SIGN_ReplaceableFace'));assert.equal(sign.length,1);
}
for(const label of ['A','B'])for(const sign of [-1,1]){
  const r=bounds(scene.getObjectByName(`Shell_return_${label}_${sign}`));
  near(sign<0?-r.max.z:r.min.z,4.53);near(sign<0?-r.min.z:r.max.z,4.74);
  const wall=bounds(scene.getObjectByName(`Shell_${label==='A'?'west':'east'}_store_${sign<0?'north':'south'}`));
  near(sign<0?-wall.max.z:wall.min.z,4.74);
}
const floors=layout.objects.filter(o=>o.kind==='floor');assert.equal(floors.length,224);
let floorJoints=0;
for(const a of floors){const b=bounds(scene.getObjectByName(a.name));near(b.min.y,-.03);near(b.max.y,0);
  for(const other of floors){if(a.name>=other.name)continue;const c=bounds(scene.getObjectByName(other.name)),dx=Math.abs(a.position_blender_m[0]-other.position_blender_m[0]),dz=Math.abs(a.position_blender_m[1]-other.position_blender_m[1]);
    if(dx<.00001&&Math.abs(dz-1.2)<.00001){near(Math.min(Math.abs(b.max.z-c.min.z),Math.abs(c.max.z-b.min.z)),0);floorJoints++;}
    if(dz<.00001&&Math.abs(dx-1.2)<.00001){near(Math.min(Math.abs(b.max.x-c.min.x),Math.abs(c.max.x-b.min.x)),0);floorJoints++;}
  }
}
assert.ok(floorJoints>300);assert.equal(layout.objects.filter(o=>o.kind==='ceiling').length,223);
const sweepScript=path.join(root,'docs/verification/p0-assembly/check-door-sweep.mjs'),scriptHash=hash(await fs.readFile(sweepScript));
const temporary=await fs.mkdtemp(path.join(os.tmpdir(),'fnd003-sweep-'));
let sweep;
try{console.log(execFileSync(process.execPath,[sweepScript,input,path.join(temporary,'sweep.json')],{encoding:'utf8',maxBuffer:2e6}));sweep=JSON.parse(await fs.readFile(path.join(temporary,'sweep.json')));}finally{await fs.rm(temporary,{recursive:true,force:true});}
assert.equal(hash(await fs.readFile(sweepScript)),scriptHash);assert.equal(sweep.records.length,2);assert.equal(sweep.pass,true);
assert.ok(sweep.records.every(r=>Math.abs(r.openClearWidthMetres-1.734)<.001));assert.ok(sweep.simultaneous.minimumCentralGapMetres>2.8);
await report(here+'/reports/geometry.json',{status:'PASS',checkedAt:new Date().toISOString(),validation,matchingInstanceBounds:layout.objects.length,inputIntegrity:integrity,priorDeliveryUnchanged:true,partitionJoints:joints,floorJoints,sweep:{...sweep,oracleSha256:scriptHash},limits:'Component OBB and 1-degree pose sampling; not continuous collision or construction certification.'});
console.log('PASS: exported dimensions, shared posts, fascia seams, floor joins, installed door clearance and input preservation');

import fs from 'node:fs';
import path from 'node:path';
import {Box3,Vector3} from 'three';
import {OBB} from 'three/addons/math/OBB.js';
import {readGlb} from '../../../models/mall-shopfront-door/glb.mjs';
const input=process.argv[2]??'docs/verification/p0-assembly/fit-study.glb';
const output=process.argv[3]??'docs/verification/p0-assembly/door-sweep.json';
const {scene}=await readGlb(input);const records=[];
const rootDoors=[];scene.traverse(o=>{if(/^Door(?:_[AB])?$/.test(o.name))rootDoors.push(o)});
if(!rootDoors.length)throw Error('No expected door wrapper found');
const floors=[];scene.traverse(o=>{if(/^Floor_/.test(o.name)&&!o.isMesh){const b=new Box3().setFromObject(o);if(!b.isEmpty())floors.push(b)}});
if(!floors.length)throw Error('No floor cells found');
const meshes=[];scene.traverse(o=>{if(o.isMesh)meshes.push(o)});
const box=o=>new Box3().setFromObject(o);
const body=o=>{o.geometry.computeBoundingBox();const b=o.geometry.boundingBox;const c=b.getCenter(new Vector3()),s=b.getSize(new Vector3()).multiplyScalar(.5);s.subScalar(.00001);return new OBB(c,s).applyMatrix4(o.matrixWorld)};
const find=(root,prefix)=>{let result;root.traverse(o=>{if(o.name.startsWith(prefix))result=o});if(!result)throw Error('Missing '+prefix);return result};
for(const door of rootDoors){
 const left=find(door,'HINGE_Left'),right=find(door,'HINGE_Right');
 const moving=[];for(const pivot of [left,right])pivot.traverse(o=>{if(o.isMesh)moving.push(o)});
 const movingSet=new Set(moving);
 // Bearings intentionally share the hinge axis. All other fixed frame/nearby parts remain obstacles.
 const obstacles=meshes.filter(o=>!movingSet.has(o)&&!o.name.startsWith('HINGE_Barrel_'));
 const closed=box(door);const broad=closed.clone().expandByScalar(1.15);
 const nearby=obstacles.filter(o=>broad.intersectsBox(box(o))).map(o=>({object:o,box:box(o),obb:body(o)}));
 const collisions=[];let outsideFloor=0;let maxOutsideExtent=0;let openWidth=0;const modes=[];
 for(const mode of ['left-only','right-only','both']){
  let samples=0;
  for(let deg=0;deg<=90;deg++){
   left.rotation.y=mode==='right-only'?0:-deg*Math.PI/180;right.rotation.y=mode==='left-only'?0:deg*Math.PI/180;scene.updateMatrixWorld(true);samples++;
   for(const part of moving){
    const b=box(part),obb=body(part);
    for(const obstacle of nearby)if(b.intersectsBox(obstacle.box)&&obb.intersectsOBB(obstacle.obb))collisions.push({mode,degrees:deg,part:part.name,obstacle:obstacle.object.name});
    const pos=part.geometry.attributes.position;
    for(let i=0;i<pos.count;i++){
     const v=new Vector3().fromBufferAttribute(pos,i).applyMatrix4(part.matrixWorld);
     if(!floors.some(f=>v.x>=f.min.x-.0001&&v.x<=f.max.x+.0001&&v.z>=f.min.z-.0001&&v.z<=f.max.z+.0001))outsideFloor++;
    }
   }
   // Distinct leaves may touch at hinge hardware, but must not intersect each other's components.
   const lm=moving.filter(o=>{for(let p=o;p;p=p.parent)if(p===left)return true;return false});
   const rm=moving.filter(o=>!lm.includes(o));
   for(const a of lm)for(const b of rm)if(box(a).intersectsBox(box(b))&&body(a).intersectsOBB(body(b)))collisions.push({mode,degrees:deg,part:a.name,obstacle:b.name});
   if(mode==='both'&&deg===90){
    // Projected passage measured in the door's closed local horizontal direction.
    const axis=new Vector3(1,0,0).transformDirection(door.matrixWorld);
    const project=pivot=>{const values=[];pivot.traverse(o=>{if(o.isMesh){const a=o.geometry.attributes.position;for(let i=0;i<a.count;i++)values.push(new Vector3().fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld).dot(axis))}});return [Math.min(...values),Math.max(...values)]};
    openWidth=project(right)[0]-project(left)[1];
   }
  }modes.push({mode,samples});
 }
 left.rotation.y=right.rotation.y=0;scene.updateMatrixWorld(true);
 records.push({door:door.name,modes,collisions:collisions.slice(0,20),collisionCount:collisions.length,outsideFloorVertexSamples:outsideFloor,openClearWidthMetres:openWidth,pass:!collisions.length&&!outsideFloor&&openWidth>1.73});
}
const simultaneous={samples:0,collisions:[],minimumCentralGapMetres:null};
if(rootDoors.length===2){
 const movingByDoor=rootDoors.map(d=>{const parts=[];for(const pivot of [find(d,'HINGE_Left'),find(d,'HINGE_Right')])pivot.traverse(o=>{if(o.isMesh)parts.push(o)});return parts});
 let minGap=Infinity;
 for(let deg=0;deg<=90;deg++){
  for(const d of rootDoors){find(d,'HINGE_Left').rotation.y=-deg*Math.PI/180;find(d,'HINGE_Right').rotation.y=deg*Math.PI/180}scene.updateMatrixWorld(true);simultaneous.samples++;
  const boxes=movingByDoor.map(parts=>{const b=new Box3();for(const o of parts)b.union(box(o));return b});minGap=Math.min(minGap,boxes[1].min.x-boxes[0].max.x);
  for(const a of movingByDoor[0])for(const b of movingByDoor[1])if(box(a).intersectsBox(box(b))&&body(a).intersectsOBB(body(b)))simultaneous.collisions.push({degrees:deg,a:a.name,b:b.name});
 }simultaneous.minimumCentralGapMetres=minGap;
}
const result={input,method:'0..90 degrees at 1-degree intervals; conservative component OBBs shrunk 10 micrometres; all moving vertices projected onto floor-cell union. Hinge bearings excluded only at their intentional axis. No continuous-time or human-accessibility certification.',records,simultaneous,pass:records.every(r=>r.pass)&&simultaneous.collisions.length===0};
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
for(const r of records)console.log(r.door,'collisions',r.collisionCount,'outside-floor samples',r.outsideFloorVertexSamples,'open width',r.openClearWidthMetres,r.pass?'PASS':'FAIL',r.collisions.slice(0,2));
if(!result.pass)process.exitCode=1;

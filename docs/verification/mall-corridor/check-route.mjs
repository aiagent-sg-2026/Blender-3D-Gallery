import fs from 'node:fs';
import {Vector3,Box3} from 'three';
import {OBB} from 'three/addons/math/OBB.js';
import {readGlb} from '../../../models/mall-shopfront-door/glb.mjs';
const {scene}=await readGlb('docs/verification/mall-corridor/corridor.glb');
scene.traverse(o=>{if(o.name.startsWith('HINGE_Left'))o.rotation.y=-Math.PI/2;if(o.name.startsWith('HINGE_Right'))o.rotation.y=Math.PI/2});scene.updateMatrixWorld(true);
const floors=[],obstacles=[];
scene.traverse(o=>{
 if(/^Floor_\d+$/.test(o.name))floors.push(new Box3().setFromObject(o));
 if(!o.isMesh)return;
 o.geometry.computeBoundingBox();const b=o.geometry.boundingBox;
 const world=new Box3().setFromObject(o);if(world.max.y<.01||world.min.y>1.8)return;
 obstacles.push({name:o.name,obb:new OBB(b.getCenter(new Vector3()),b.getSize(new Vector3()).multiplyScalar(.5)).applyMatrix4(o.matrixWorld)});
});
// glTF X/Z: arrival -> shop A -> centre -> shop B -> arrival, doors open 90 degrees.
const points=[[0,3.3],[0,0],[-3.6,0],[0,0],[3.6,0],[0,0],[0,3.3]];
const failures=[];let samples=0;
for(let j=1;j<points.length;j++){
 const a=points[j-1],b=points[j],steps=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.05);
 for(let i=0;i<=steps;i++){
  const x=a[0]+(b[0]-a[0])*i/steps,z=a[1]+(b[1]-a[1])*i/steps;samples++;
  for(const [dx,dz] of [[0,0],[.25,0],[-.25,0],[0,.25],[0,-.25]])if(!floors.some(f=>x+dx>=f.min.x-.0001&&x+dx<=f.max.x+.0001&&z+dz>=f.min.z-.0001&&z+dz<=f.max.z+.0001))failures.push({type:'floor',x,z});
  for(const y of [.25,.9,1.55]){
   const p=new Vector3(x,y,z);for(const o of obstacles){const q=o.obb.clampPoint(p,new Vector3());if(q.distanceTo(p)<.24999)failures.push({type:'capsule',x,y,z,obstacle:o.name})}
  }
 }
}
const result={method:'Sampled 0.25 m radius / 1.8 m tall proxy at <=0.05 m route spacing, 3 vertical sphere samples, component OBB obstacles, doors at 90 degrees. Not a runtime character controller.',waypointsGLTFXZ:points,samples,failures:failures.slice(0,20),failureCount:failures.length,pass:failures.length===0};
fs.writeFileSync('docs/verification/mall-corridor/route-results.json',JSON.stringify(result,null,2)+'\n');console.log('ROUTE',samples,'samples',failures.length,'failures',result.failures);if(!result.pass)process.exitCode=1;

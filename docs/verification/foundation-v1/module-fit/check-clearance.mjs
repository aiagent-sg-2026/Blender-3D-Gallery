import assert from 'node:assert/strict';
import path from 'node:path';
import {Vector3} from 'three';
import {readGlb} from '../../../../models/mall-shopfront-door/glb.mjs';
import {report} from '../qa-utils.mjs';

const here=path.dirname(new URL(import.meta.url).pathname);
const {scene}=await readGlb(here+'/foundation-fitted.glb');
const rows=[];
for(const name of ['Door_A','Door_B']){
  const door=scene.getObjectByName(name),inverse=door.matrixWorld.clone().invert();
  function extent(prefix){
    let mesh;door.traverse(o=>{if(o.isMesh&&o.name.startsWith(prefix))mesh=o;});assert.ok(mesh,prefix);
    const xs=[],ys=[],positions=mesh.geometry.attributes.position;
    for(let i=0;i<positions.count;i++){
      const p=new Vector3().fromBufferAttribute(positions,i).applyMatrix4(mesh.matrixWorld).applyMatrix4(inverse);xs.push(p.x);ys.push(p.y);
    }
    return {minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys)};
  }
  const left=extent('FRAME_Jamb_Left'),right=extent('FRAME_Jamb_Right'),header=extent('FRAME_Header');
  const width=right.minX-left.maxX,height=header.minY,outerWidth=right.maxX-left.minX,outerHeight=header.maxY;
  const scale=door.getWorldScale(new Vector3()).toArray();assert.ok(scale.every(v=>Math.abs(v-1)<.00001));
  for(const [a,b] of [[width,1.94],[height,2.32],[outerWidth,2.1],[outerHeight,2.4]])assert.ok(Math.abs(a-b)<.00001);
  rows.push({door:name,outerWidthMetres:outerWidth,outerHeightMetres:outerHeight,frameClearWidthMetres:width,frameClearHeightMetres:height,worldScale:scale});
}
await report(here+'/reports/clearance.json',{status:'PASS',method:'Actual frame vertex extents transformed back to each unscaled door root; floor Y=0. Full-open leaf/hardware projection is recorded independently in geometry.json.',rows});
console.log('PASS: installed door outer size 2.10 x 2.40 m; frame aperture 1.94 x 2.32 m');

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Box3, Ray, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const folder=process.env.CHALK_QA_ASSET_DIR || 'models/eight-ball-billiards/exports';
async function load(file){
  const b=fs.readFileSync(`${folder}/${file}`);const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
  gltf.scene.updateMatrixWorld(true);const root=gltf.scene.getObjectByName('ASSET_Chalk');assert.ok(root);return {gltf,root};
}
for(const file of ['chalk.glb','billiards-scene.glb'])test(`${file}: chalk preserves its full-size core and sleeve contact`,async()=>{
  const {root}=await load(file);const meshes=[];root.traverse(ob=>{if(ob.isMesh)meshes.push(ob);});assert.equal(meshes.length,2);
  const paper=meshes.find(ob=>ob.name.includes('paper_sleeve')),core=meshes.find(ob=>ob.name.includes('blue_top'));assert.ok(paper&&core);
  const a=new Box3().setFromObject(paper),b=new Box3().setFromObject(core),size=new Box3().setFromObject(root).getSize(new Vector3());
  assert.ok(Math.abs(size.x-.025)<1e-6&&Math.abs(size.y-.027)<1e-6&&Math.abs(size.z-.025)<1e-6,'Preserve25×25×27mm scale');
  assert.ok(b.min.x>=a.min.x&&b.max.x<=a.max.x&&b.min.z>=a.min.z&&b.max.z<=a.max.z,'Core remains inside sleeve footprint');
  assert.ok(a.max.y-b.min.y>.0009&&a.max.y-b.min.y<.0011,'Preserve1mm material overlap without an air gap');
  assert.ok(b.max.y>a.max.y,'The usable chalk face remains exposed');
});
test('assembled chalk rests on the actual flat wooden rail surface',async()=>{
  const {gltf,root}=await load('billiards-scene.glb');const chalk=new Box3().setFromObject(root);const rails=[];
  gltf.scene.getObjectByName('ASSET_Table').traverse(ob=>{if(ob.isMesh&&ob.name.startsWith('Long_rail')){const b=new Box3().setFromObject(ob);if(chalk.min.x>=b.min.x&&chalk.max.x<=b.max.x&&chalk.min.z>=b.min.z&&chalk.max.z<=b.max.z)rails.push(ob);}});
  assert.equal(rails.length,1,'Exactly one rail supports the entire footprint');const rail=rails[0],top=new Box3().setFromObject(rail).max.y;
  const positions=rail.geometry.getAttribute('position'),index=rail.geometry.index;
  for(const [x,z] of [[chalk.min.x,chalk.min.z],[chalk.min.x,chalk.max.z],[chalk.max.x,chalk.min.z],[chalk.max.x,chalk.max.z],[(chalk.min.x+chalk.max.x)/2,(chalk.min.z+chalk.max.z)/2]]){
    const ray=new Ray(new Vector3(x,top+1,z),new Vector3(0,-1,0));const hits=[];
    for(let k=0;k<index.count;k+=3){const points=[0,1,2].map(j=>new Vector3().fromBufferAttribute(positions,index.getX(k+j)).applyMatrix4(rail.matrixWorld));const hit=ray.intersectTriangle(...points,false,new Vector3());if(hit)hits.push(hit.y);}
    assert.ok(hits.length,'Actual rail triangles must support every sampled footprint corner');assert.ok(Math.abs(Math.max(...hits)-top)<1e-6,'Support is on the flat top, outside the bevel');
  }
  const gap=chalk.min.y-top;assert.ok(gap>=-.0002&&gap<=1e-6,`Chalk/rail separation ${gap}m`);
});

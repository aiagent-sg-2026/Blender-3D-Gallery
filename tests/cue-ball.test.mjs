import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Box3, Ray, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const directory=process.env.CUE_BALL_QA_ASSET_DIR||'models/eight-ball-billiards/exports';
async function load(file){const b=fs.readFileSync(`${directory}/${file}`);const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');gltf.scene.updateMatrixWorld(true);const root=gltf.scene.getObjectByName('ASSET_Ball_00');assert.ok(root);const meshes=[];root.traverse(ob=>{if(ob.isMesh)meshes.push(ob);});assert.equal(meshes.length,1,'Cue ball has one unnumbered resin body');return {gltf,root,body:meshes[0]};}
for(const file of ['ball_00.glb','billiards-scene.glb'])test(`${file}: cue ball retains57.15mm spherical geometry and smooth outward normals`,async()=>{
  const {body}=await load(file);const p=body.geometry.getAttribute('position'),n=body.geometry.getAttribute('normal'),radius=.05715/2;
  assert.equal(body.geometry.index.count/3,3968);
  for(let i=0;i<p.count;i++){
    const point=new Vector3().fromBufferAttribute(p,i),normal=new Vector3().fromBufferAttribute(n,i);
    assert.ok(Math.abs(point.length()-radius)<radius*1e-5,'Every vertex lies on the authored sphere');
    assert.ok(Math.abs(normal.length()-1)<1e-5);
    // Half the authored64-longitude/32-latitude angular spacing bounds normal
    // deviation without assuming exact analytic normals from a polygon mesh.
    assert.ok(normal.dot(point.normalize())>Math.cos(Math.PI/64),'Normals follow the sphere, without a polar or seam crease');
  }
  assert.equal(body.material.metalness,0);assert.ok(Math.abs(body.material.roughness-.24)<1e-6);assert.equal(body.material.opacity,1);assert.equal(body.material.transparent,false);
});
test('assembled cue ball is tangent to the actual flat cloth surface',async()=>{
  const {gltf,root}=await load('billiards-scene.glb');const ball=new Box3().setFromObject(root);let cloth;gltf.scene.traverse(ob=>{if(ob.isMesh&&ob.name.includes('slate_and_green_cloth'))cloth=ob;});assert.ok(cloth);
  const center=ball.getCenter(new Vector3()),ray=new Ray(new Vector3(center.x,ball.max.y+1,center.z),new Vector3(0,-1,0)),p=cloth.geometry.getAttribute('position'),index=cloth.geometry.index,hits=[];
  for(let k=0;k<index.count;k+=3){const v=[0,1,2].map(j=>new Vector3().fromBufferAttribute(p,index.getX(k+j)).applyMatrix4(cloth.matrixWorld));const hit=ray.intersectTriangle(...v,false,new Vector3());if(hit)hits.push(hit.y);}
  assert.ok(hits.length,'A real cloth triangle supports the cue ball');const top=Math.max(...hits),gap=ball.min.y-top;
  assert.ok(Math.abs(gap)<1e-6,`Spherical bottom must be tangent to cloth, got ${gap}m`);
});

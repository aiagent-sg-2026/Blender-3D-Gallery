import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Triangle, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const directory=process.env.RACK_QA_ASSET_DIR || 'models/eight-ball-billiards/exports';
async function load(file) {
  const bytes=fs.readFileSync(`${directory}/${file}`);
  const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
  gltf.scene.updateMatrixWorld(true);
  const root=gltf.scene.getObjectByName('ASSET_Triangle_Rack');
  assert.ok(root);
  const bars=[];root.traverse(ob=>{if(ob.isMesh)bars.push(ob);});
  bars.sort((a,b)=>a.name.localeCompare(b.name));assert.equal(bars.length,3);
  return {gltf,bars};
}

for(const file of ['triangle_rack.glb','billiards-scene.glb']) {
  test(`${file}: rack holds fifteen touching balls at the authored57.15mm diameter`,async()=>{
    const {bars}=await load(file);
    const radius=.05715/2,diameter=2*radius;
    const center=bars.reduce((sum,ob)=>sum.add(new Vector3().setFromMatrixPosition(ob.matrixWorld)),new Vector3()).divideScalar(3);
    // An equilateral five-row pack has a fixed convex hull. Center its hull
    // on the rack, with the single-ball row facing the authored left corner.
    const balls=[];
    for(let row=0;row<5;row++)for(let column=0;column<=row;column++)balls.push(new Vector3(center.x+(row-8/3)*diameter*Math.sqrt(3)/2,center.y-.0089+radius,center.z+(column-row/2)*diameter));
    assert.equal(balls.length,15);
    for(let i=0;i<balls.length;i++)for(let j=i+1;j<balls.length;j++)assert.ok(balls[i].distanceTo(balls[j])>=diameter-1e-7,'Balls must not overlap');
    for(const ob of bars) {
      const midpoint=new Vector3().setFromMatrixPosition(ob.matrixWorld);
      const axis=new Vector3(0,1,0).transformDirection(ob.matrixWorld);
      const inward=new Vector3(axis.z,0,-axis.x);
      if(inward.dot(center.clone().sub(midpoint))<0)inward.negate();
      const g=ob.geometry,p=g.getAttribute('position'),idx=g.index;
      for(const ball of balls) {
        assert.ok(inward.dot(ball.clone().sub(midpoint))>0,'Every ball center must be inside the rack');
        for(let k=0;k<idx.count;k+=3) {
          const vertices=[0,1,2].map(j=>new Vector3().fromBufferAttribute(p,idx.getX(k+j)).applyMatrix4(ob.matrixWorld));
          const closest=new Triangle(...vertices).closestPointToPoint(ball,new Vector3());
          assert.ok(closest.distanceTo(ball)>=radius-1e-6,'Full-size ball must not intersect any rack triangle');
        }
      }
    }
  });
  test(`${file}: rack has matching closed miter rings at all three joints`,async()=>{
    const {bars}=await load(file);
    const ends=bars.map(ob=>{
      const p=ob.geometry.getAttribute('position');const rings=[[],[]];
      for(let i=0;i<p.count;i++) {
        const v=new Vector3().fromBufferAttribute(p,i);
        // Blender's local Z longitudinal axis becomes local Y in glTF.
        const ring=rings[Number(v.y>0)];v.applyMatrix4(ob.matrixWorld);
        if(!ring.some(q=>q.distanceTo(v)<1e-7))ring.push(v);
      }
      assert.deepEqual(rings.map(r=>r.length),[12,12]);return rings;
    });
    for(let i=0;i<3;i++) {
      const a=ends[i][1],b=ends[(i+1)%3][0];
      assert.ok(Math.max(...a.map(p=>Math.min(...b.map(q=>p.distanceTo(q)))))<1e-6,'No outer notch or unmatched joint vertex');
    }
  });
  test(`${file}: rack planar caps and radial cylinder normals follow geometry`,async()=>{
    const {bars}=await load(file);
    for(const ob of bars) {
      const g=ob.geometry,p=g.getAttribute('position'),n=g.getAttribute('normal'),idx=g.index;
      let caps=0,sides=0;
      for(let k=0;k<idx.count;k+=3) {
        const ids=[0,1,2].map(j=>idx.getX(k+j));
        const points=ids.map(id=>new Vector3().fromBufferAttribute(p,id));
        // Side triangles contain two vertices on one longitudinal generator.
        // Miter-cap triangles have three distinct radial XZ positions.
        const side=points.some((a,i)=>points.some((b,j)=>i!==j && Math.hypot(a.x-b.x,a.z-b.z)<1e-7));
        const face=points[1].clone().sub(points[0]).cross(points[2].clone().sub(points[0]));
        assert.ok(face.lengthSq()>1e-18);face.normalize();
        if(side)sides++;else caps++;
        ids.forEach((id,j)=>{
          const normal=new Vector3().fromBufferAttribute(n,id);
          assert.ok(Math.abs(normal.length()-1)<1e-5);
          const expected=side?new Vector3(points[j].x,0,points[j].z).normalize():face;
          assert.ok(normal.dot(expected)>.9999,side?'Cylinder normals remain radial at oblique cuts':'Cap normals remain planar');
        });
      }
      assert.equal(caps,20);assert.equal(sides,24);
    }
  });
}

test('assembled rack is seated on the preserved table playing surface',async()=>{
  const {gltf,bars}=await load('billiards-scene.glb');
  let cloth;gltf.scene.traverse(ob=>{if(ob.name.includes('slate_and_green_cloth'))cloth=ob;});
  // Blender exporter sanitizes the original display name. Fail explicitly
  // if the named support disappears rather than selecting an arbitrary mesh.
  assert.ok(cloth,'Named slate/cloth support must exist');
  const top=[];cloth.traverse(ob=>{if(ob.isMesh){const p=ob.geometry.getAttribute('position');for(let i=0;i<p.count;i++)top.push(new Vector3().fromBufferAttribute(p,i).applyMatrix4(ob.matrixWorld).y);}});
  const bottom=[];for(const ob of bars){const p=ob.geometry.getAttribute('position');for(let i=0;i<p.count;i++)bottom.push(new Vector3().fromBufferAttribute(p,i).applyMatrix4(ob.matrixWorld).y);}
  const separation=Math.min(...bottom)-Math.max(...top);
  assert.ok(separation>=-.0002 && separation<=1e-6,`Rack/support separation ${separation} m`);
});
